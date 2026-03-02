#!/bin/bash
# Script cài đặt PicoClaw với Gamene API trên Ubuntu VPS
# Sử dụng: bash install-picoclaw-gamene.sh

set -e

echo "🚀 Cài đặt PicoClaw với Gamene API"
echo "===================================="

# Màu sắc
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Kiểm tra hệ điều hành
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}❌ Không phải Ubuntu/Debian${NC}"
    exit 1
fi

# Cập nhật hệ thống
echo -e "${YELLOW}📦 Cập nhật hệ thống...${NC}"
sudo apt update -qq

# Tải binary PicoClaw
echo -e "${YELLOW}⬇️  Tải PicoClaw binary...${NC}"
ARCH=$(uname -m)
if [ "$ARCH" == "x86_64" ]; then
    BINARY="picoclaw-linux-amd64"
elif [ "$ARCH" == "aarch64" ]; then
    BINARY="picoclaw-linux-arm64"
else
    echo -e "${RED}❌ Architecture không hỗ trợ: $ARCH${NC}"
    exit 1
fi

cd /tmp
wget -q --show-progress "https://github.com/sipeed/picoclaw/releases/latest/download/$BINARY" -O picoclaw
chmod +x picoclaw
sudo mv picoclaw /usr/local/bin/picoclaw

echo -e "${GREEN}✅ Đã cài đặt binary${NC}"

# Tạo thư mục config
echo -e "${YELLOW}📁 Tạo thư mục cấu hình...${NC}"
mkdir -p ~/.picoclaw

# Tải config Gamene
echo -e "${YELLOW}📝 Tạo config với Gamene API...${NC}"
cat > ~/.picoclaw/config.json << 'EOF'
{
  "agents": {
    "defaults": {
      "workspace": "~/.picoclaw/workspace",
      "restrict_to_workspace": true,
      "model_name": "gemini-flash",
      "max_tokens": 8192,
      "temperature": 0.7,
      "max_tool_iterations": 20
    }
  },
  "model_list": [
    {
      "model_name": "gemini-flash",
      "model": "google/gemini-2.5-flash",
      "api_key": "sk-ed70bc16720b4b689bf69f81e3d221f5",
      "api_base": "https://api.gamene.online/v1",
      "request_timeout": 300
    },
    {
      "model_name": "gemini-pro",
      "model": "google/gemini-2.5-pro",
      "api_key": "sk-ed70bc16720b4b689bf69f81e3d221f5",
      "api_base": "https://api.gamene.online/v1",
      "request_timeout": 300
    },
    {
      "model_name": "claude-sonnet",
      "model": "anthropic/claude-sonnet-4-5",
      "api_key": "sk-ed70bc16720b4b689bf69f81e3d221f5",
      "api_base": "https://api.gamene.online/v1",
      "request_timeout": 300
    },
    {
      "model_name": "deepseek-v3",
      "model": "deepseek/deepseek-chat",
      "api_key": "none",
      "api_base": "https://dep.apphay.io.vn/v1",
      "request_timeout": 300
    },
    {
      "model_name": "deepseek-r1",
      "model": "deepseek/deepseek-reasoner",
      "api_key": "none",
      "api_base": "https://dep.apphay.io.vn/v1",
      "request_timeout": 300
    },
    {
      "model_name": "deepseek-coder",
      "model": "deepseek/deepseek-coder",
      "api_key": "none",
      "api_base": "https://dep.apphay.io.vn/v1",
      "request_timeout": 300
    }
  ],
  "tools": {
    "web_search": {
      "enabled": true,
      "provider": "auto",
      "max_results": 5
    }
  },
  "channels": {
    "telegram": {
      "enabled": false,
      "token": "YOUR_TELEGRAM_BOT_TOKEN",
      "allow_from": []
    }
  },
  "gateway": {
    "host": "0.0.0.0",
    "port": 8080,
    "health_path": "/health",
    "readiness_path": "/ready"
  },
  "logging": {
    "level": "info",
    "format": "json"
  }
}
EOF

echo -e "${GREEN}✅ Đã tạo config${NC}"

# Tạo systemd service
echo -e "${YELLOW}⚙️  Tạo systemd service...${NC}"
sudo tee /etc/systemd/system/picoclaw.service > /dev/null << EOF
[Unit]
Description=PicoClaw AI Gateway with Gamene API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/picoclaw gateway start
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Đã tạo systemd service${NC}"

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo -e "${GREEN}🎉 Cài đặt hoàn tất!${NC}"
echo ""
echo "📋 Các lệnh quản lý:"
echo "  - Khởi động:       sudo systemctl start picoclaw"
echo "  - Dừng:            sudo systemctl stop picoclaw"
echo "  - Khởi động lại:   sudo systemctl restart picoclaw"
echo "  - Xem logs:        sudo journalctl -u picoclaw -f"
echo "  - Tự động khởi động: sudo systemctl enable picoclaw"
echo ""
echo "📝 Config: ~/.picoclaw/config.json"
echo ""
echo "🚀 Khởi động ngay:"
echo "   sudo systemctl start picoclaw"
echo "   sudo systemctl status picoclaw"
echo ""
echo "🔧 Test API:"
echo "   picoclaw agent -m 'Xin chào!' --model gemini-flash"
echo ""
