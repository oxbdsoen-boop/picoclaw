#!/bin/bash
# ═══════════════════════════════════════════════
#  PicoClaw + DeepSeek (dep.apphay.io.vn) Setup
# ═══════════════════════════════════════════════
set -e

echo "════════════════════════════════════════"
echo "  PicoClaw DeepSeek Bot - Installer"
echo "════════════════════════════════════════"

REPO_DIR="$HOME/picoclaw"
PICO_DIR="$REPO_DIR/deepseek-pico"

cd "$PICO_DIR"

# Kiểm tra config
if grep -q "YOUR_DEEPSEEK_BOT_TOKEN" data/config.json; then
    echo ""
    echo "⚠️  Chưa có Telegram bot token!"
    echo "1. Mở Telegram → @BotFather → /newbot"
    echo "2. Lấy token, rồi chạy:"
    echo "   sed -i 's|YOUR_DEEPSEEK_BOT_TOKEN|TOKEN_CUA_BAN|' $PICO_DIR/data/config.json"
    echo "3. Chạy lại script này"
    exit 1
fi

# Kiểm tra PicoClaw image
if ! docker image inspect picoclaw:local &>/dev/null; then
    echo "🔨 Build PicoClaw image..."
    cd "$REPO_DIR"
    docker build -t picoclaw:local -f docker/Dockerfile .
    cd "$PICO_DIR"
fi

# Build & run
echo "🔨 Build adapter..."
docker compose build

echo "🚀 Khởi động..."
docker compose up -d

echo ""
echo "════════════════════════════════════════"
echo "  ✅ PicoClaw DeepSeek Bot đã chạy!"
echo "════════════════════════════════════════"
echo ""
echo "  Models: DeepSeek-V3, R1, Coder, VL"
echo "  API:    dep.apphay.io.vn"
echo ""
echo "  Lệnh:"
echo "  • Logs:    docker compose logs -f"
echo "  • Restart: docker compose restart"
echo "  • Stop:    docker compose down"
echo "════════════════════════════════════════"
