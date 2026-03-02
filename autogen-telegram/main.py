"""
AutoGen Multi-Agent Telegram Bot (v2 - Simple Router)
─────────────────────────────────────────────────────
Dùng keyword routing thay vì GroupChat Manager
để tránh bị Gamene block system prompt phức tạp.
"""

import asyncio
import logging
import re

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
#  Agents
# ═══════════════════════════════════════════════

agents = {
    "coder": autogen.AssistantAgent(
        name="Coder",
        system_message=(
            "You are a professional programmer. "
            "Write clean code with comments. "
            "Support Python, JavaScript, Go, Bash, SQL. "
            "Reply in the same language the user uses."
        ),
        llm_config=get_llm_config(CODER_MODEL),
    ),
    "researcher": autogen.AssistantAgent(
        name="Researcher",
        system_message=(
            "You are a research and analysis expert. "
            "Provide thorough, well-structured answers. "
            "Compare options and cite sources when possible. "
            "Reply in the same language the user uses."
        ),
        llm_config=get_llm_config(RESEARCHER_MODEL),
    ),
    "writer": autogen.AssistantAgent(
        name="Writer",
        system_message=(
            "You are a creative content writer. "
            "Write blogs, emails, reports, translations. "
            "Professional and easy to read. "
            "Reply in the same language the user uses."
        ),
        llm_config=get_llm_config(WRITER_MODEL),
    ),
}

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0,
    code_execution_config=False,
)

# ═══════════════════════════════════════════════
#  Keyword router
# ═══════════════════════════════════════════════

CODE_KW = re.compile(
    r'(?i)(code|script|function|bug|debug|fix|error|python|javascript|js|go|golang|'
    r'bash|sql|html|css|api|server|docker|git|compile|class|import|pip|npm|'
    r'viet code|sua code|loi|deploy|cai dat|install|build|database|db|'
    r'algorithm|sort|loop|array|regex|json|http|curl|'
    r'viet code|sua code|ham|bien|trien khai)'
)

RESEARCH_KW = re.compile(
    r'(?i)(search|find|compare|research|explain|what is|how does|why|difference|'
    r'vs|versus|review|analyze|pros|cons|recommend|best|'
    r'tim|so sanh|giai thich|tai sao|the nao|khac nhau|phan tich|'
    r'la gi|nghia la|lich su|history|wiki|define)'
)

WRITER_KW = re.compile(
    r'(?i)(write|blog|article|email|letter|translate|draft|essay|story|poem|'
    r'content|copy|marketing|seo|summary|summarize|rewrite|'
    r'viet bai|dich|tom tat|noi dung|bai viet|thu|soan|bien tap)'
)


def route_message(text):
    code_score = len(CODE_KW.findall(text))
    research_score = len(RESEARCH_KW.findall(text))
    writer_score = len(WRITER_KW.findall(text))

    if code_score >= research_score and code_score >= writer_score and code_score > 0:
        return "coder", "Coder"
    elif writer_score >= research_score and writer_score > 0:
        return "writer", "Writer"
    elif research_score > 0:
        return "researcher", "Researcher"
    else:
        return "researcher", "Researcher"


# ═══════════════════════════════════════════════
#  Run agent
# ═══════════════════════════════════════════════

def run_agent_sync(message):
    agent_key, agent_label = route_message(message)
    agent = agents[agent_key]
    log.info(f"Routed to: {agent_label}")

    try:
        user_proxy.initiate_chat(agent, message=message, clear_history=True)
    except Exception as e:
        log.error(f"Agent error ({agent_key}): {e}")
        if agent_key != "researcher":
            log.info("Fallback to researcher...")
            try:
                user_proxy.initiate_chat(agents["researcher"], message=message, clear_history=True)
                agent = agents["researcher"]
                agent_label = "Researcher (fallback)"
            except Exception as e2:
                return f"Error: {e2}"
        else:
            return f"Error: {e}"

    last_msg = agent.last_message(user_proxy)
    if last_msg and last_msg.get("content"):
        return f"[{agent_label}]\n{last_msg['content']}"
    return "No response."


async def run_agent_async(message):
    return await asyncio.get_event_loop().run_in_executor(None, run_agent_sync, message)


# ═══════════════════════════════════════════════
#  Telegram
# ═══════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "AutoGen Multi-Agent Bot\n\n"
        "Coder | Researcher | Writer\n"
        "Send any message!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        await update.message.reply_text("Access denied.")
        return

    text = update.message.text
    if not text:
        return

    log.info(f"[{user_id}] {text[:80]}")
    await update.message.chat.send_action("typing")

    agent_key, agent_label = route_message(text)
    ph = await update.message.reply_text(f"{agent_label} is working...")

    try:
        reply = await run_agent_async(text)
    except Exception as e:
        reply = f"Error: {e}"

    if len(reply) <= 4096:
        try:
            await ph.edit_text(reply, parse_mode="Markdown")
        except Exception:
            await ph.edit_text(reply)
    else:
        try:
            await ph.edit_text(reply[:4096], parse_mode="Markdown")
        except Exception:
            await ph.edit_text(reply[:4096])
        for i in range(4096, len(reply), 4096):
            await update.message.reply_text(reply[i:i+4096])

    log.info(f"[{user_id}] done")


def main():
    log.info("Starting AutoGen Telegram Bot v2")
    log.info(f"Users: {ALLOWED_USERS}")
    log.info(f"Coder={CODER_MODEL}, Researcher={RESEARCHER_MODEL}, Writer={WRITER_MODEL}")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
