"""
AutoGen Multi-Agent Telegram Bot
─────────────────────────────────
Agents:
  • Manager   — nhận tin nhắn, phân công cho agent phù hợp
  • Coder     — viết / debug code
  • Researcher— tìm kiếm, phân tích thông tin
  • Writer    — viết nội dung, dịch thuật

Flow:  User → Telegram → Manager → GroupChat (agents trao đổi) → reply User
"""

import asyncio
import logging
import textwrap

import autogen
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import (
    TELEGRAM_TOKEN,
    ALLOWED_USERS,
    get_llm_config,
    MANAGER_MODEL,
    CODER_MODEL,
    RESEARCHER_MODEL,
    WRITER_MODEL,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("autogen-tg")

# ═══════════════════════════════════════════════
#  AutoGen Agents
# ═══════════════════════════════════════════════

coder = autogen.AssistantAgent(
    name="Coder",
    system_message=textwrap.dedent("""\
        Bạn là lập trình viên chuyên nghiệp.
        - Viết code sạch, có comment
        - Hỗ trợ Python, JavaScript, Go, Bash, SQL
        - Giải thích ngắn gọn khi cần
        - Nếu task không liên quan code, nói "PASS" để nhường agent khác
    """),
    llm_config=get_llm_config(CODER_MODEL),
)

researcher = autogen.AssistantAgent(
    name="Researcher",
    system_message=textwrap.dedent("""\
        Bạn là chuyên gia nghiên cứu và phân tích.
        - Tìm hiểu, so sánh, tổng hợp thông tin
        - Trả lời dựa trên kiến thức, có dẫn nguồn khi có thể
        - Nếu task không liên quan nghiên cứu, nói "PASS"
    """),
    llm_config=get_llm_config(RESEARCHER_MODEL),
)

writer = autogen.AssistantAgent(
    name="Writer",
    system_message=textwrap.dedent("""\
        Bạn là nhà sáng tạo nội dung.
        - Viết blog, email, báo cáo, dịch thuật
        - Văn phong chuyên nghiệp, dễ đọc
        - Nếu task không liên quan viết lách, nói "PASS"
    """),
    llm_config=get_llm_config(WRITER_MODEL),
)

# User proxy — tự động approve, không chạy code local
user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0,
    code_execution_config=False,
)

# Group chat — Manager tự chọn agent phù hợp
groupchat = autogen.GroupChat(
    agents=[user_proxy, coder, researcher, writer],
    messages=[],
    max_round=6,  # tối đa 6 lượt trao đổi
    speaker_selection_method="auto",
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=get_llm_config(MANAGER_MODEL),
)


# ═══════════════════════════════════════════════
#  Run AutoGen in thread (sync → async bridge)
# ═══════════════════════════════════════════════

def run_autogen_sync(message: str) -> str:
    """Run AutoGen group chat synchronously, return final reply."""
    # Reset chat history for new conversation
    groupchat.messages.clear()

    try:
        user_proxy.initiate_chat(
            manager,
            message=message,
            clear_history=True,
        )
    except Exception as e:
        log.error(f"AutoGen error: {e}")
        return f"❌ Lỗi: {e}"

    # Collect last non-User message as the answer
    for msg in reversed(groupchat.messages):
        if msg.get("name") != "User" and msg.get("content"):
            content = msg["content"].strip()
            if content and content.upper() != "PASS":
                agent_name = msg.get("name", "Agent")
                return f"🤖 **{agent_name}**:\n{content}"

    return "⚠️ Không có agent nào trả lời được. Thử lại với câu hỏi khác."


async def run_autogen_async(message: str) -> str:
    """Async wrapper around sync AutoGen."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_autogen_sync, message)


# ═══════════════════════════════════════════════
#  Telegram Handlers
# ═══════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **AutoGen Multi-Agent Bot**\n\n"
        "Gửi tin nhắn bất kỳ, tôi sẽ phân công cho agent phù hợp:\n"
        "• 💻 **Coder** — viết code, debug\n"
        "• 🔍 **Researcher** — tìm kiếm, phân tích\n"
        "• ✍️ **Writer** — viết nội dung, dịch\n\n"
        "Ví dụ: _Viết Python script download YouTube_",
        parse_mode="Markdown",
    )


async def cmd_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📋 **Models đang dùng:**\n"
        f"• Manager: `{MANAGER_MODEL}`\n"
        f"• Coder: `{CODER_MODEL}`\n"
        f"• Researcher: `{RESEARCHER_MODEL}`\n"
        f"• Writer: `{WRITER_MODEL}`",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Whitelist check
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Bạn không có quyền sử dụng bot này.")
        return

    text = update.message.text
    if not text:
        return

    log.info(f"[{user_id}] → {text[:80]}")

    # Send typing indicator
    await update.message.chat.send_action("typing")
    placeholder = await update.message.reply_text("⏳ Đang xử lý, các agent đang thảo luận...")

    try:
        reply = await run_autogen_async(text)
    except Exception as e:
        reply = f"❌ Lỗi hệ thống: {e}"

    # Edit placeholder with result (split if too long)
    if len(reply) <= 4096:
        await placeholder.edit_text(reply, parse_mode="Markdown")
    else:
        await placeholder.edit_text(reply[:4096], parse_mode="Markdown")
        # Send remaining parts
        for i in range(4096, len(reply), 4096):
            await update.message.reply_text(reply[i:i+4096], parse_mode="Markdown")

    log.info(f"[{user_id}] ← {reply[:80]}")


# ═══════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════

def main():
    log.info("Starting AutoGen Telegram Bot...")
    log.info(f"Allowed users: {ALLOWED_USERS}")
    log.info(f"Models: Manager={MANAGER_MODEL}, Coder={CODER_MODEL}, "
             f"Researcher={RESEARCHER_MODEL}, Writer={WRITER_MODEL}")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("models", cmd_models))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    log.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
