#!/bin/bash
# ═══════════════════════════════════════════════════
#  AutoGen Multi-Agent Telegram Bot — VPS Installer
#  Dùng Gamene API + DeepSeek API
# ═══════════════════════════════════════════════════
set -e

echo "══════════════════════════════════════════"
echo "  AutoGen Telegram Bot - Cài đặt VPS"
echo "══════════════════════════════════════════"

# ── 1. Kiểm tra Docker ──
if ! command -v docker &>/dev/null; then
    echo "❌ Docker chưa cài. Đang cài Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

if ! docker compose version &>/dev/null; then
    echo "❌ Docker Compose chưa có. Cài trước rồi chạy lại."
    exit 1
fi

echo "✅ Docker OK"

# ── 2. Clone/pull repo ──
REPO_DIR="$HOME/picoclaw"
if [ -d "$REPO_DIR/.git" ]; then
    echo "📦 Đang pull code mới..."
    cd "$REPO_DIR" && git pull
else
    echo "📦 Đang clone repo..."
    git clone https://github.com/sipeed/picoclaw.git "$REPO_DIR"
fi

cd "$REPO_DIR/autogen-telegram"

# ── 3. Cấu hình (nếu chưa có .env) ──
if [ ! -f .env ]; then
    echo ""
    echo "📝 Tạo file .env (có thể sửa sau)..."
    cat > .env << 'ENV'
# ── Telegram ──
TELEGRAM_TOKEN=8597970888:AAFXZBHYHdrCloAto-PCkiiNMSiZvDT5lNM
ALLOWED_USERS=1176968735

# ── Gamene API ──
GAMENE_API_KEY=sk-ed70bc16720b4b689bf69f81e3d221f5
GAMENE_BASE_URL=https://api.gamene.online/v1

# ── DeepSeek API ──
DEEPSEEK_BASE_URL=https://dep.apphay.io.vn/v1
DEEPSEEK_API_KEY=none

# ── Model cho mỗi agent (đổi tùy ý) ──
MANAGER_MODEL=claude-sonnet-4-6
CODER_MODEL=claude-opus-4-6
RESEARCHER_MODEL=gpt-4o-mini
WRITER_MODEL=deepseek-chat
ENV
    echo "✅ File .env đã tạo tại: $REPO_DIR/autogen-telegram/.env"
fi

# ── 4. Build & Run ──
echo ""
echo "🔨 Build Docker image..."
docker compose build

echo ""
echo "🚀 Khởi động bot..."
docker compose up -d

echo ""
echo "══════════════════════════════════════════"
echo "  ✅ AutoGen Telegram Bot đã chạy!"
echo "══════════════════════════════════════════"
echo ""
echo "  Agents:"
echo "  • Manager  → claude-sonnet-4-6  (phân công)"
echo "  • Coder    → claude-opus-4-6    (viết code)"
echo "  • Researcher → gpt-4o-mini      (nghiên cứu)"
echo "  • Writer   → deepseek-chat      (viết nội dung)"
echo ""
echo "  Lệnh hữu ích:"
echo "  • Xem logs:    docker compose logs -f"
echo "  • Restart:     docker compose restart"
echo "  • Dừng:        docker compose down"
echo "  • Đổi model:   nano .env → docker compose up -d"
echo ""
echo "  Mở Telegram → gửi tin cho bot để test!"
echo "══════════════════════════════════════════"
