# 🚀 Hướng Dẫn Cài Đặt PicoClaw với Multi-API

> **Bao gồm:**
> - ✅ [Gamene API](https://api.gamene.online) - Gemini, Claude, GPT (có quota)
> - ✅ [DeepSeek API](https://dep.apphay.io.vn) - DeepSeek V3, R1, Coder (hoàn toàn miễn phí)

## Phương Pháp 1: Script Tự Động (Khuyến nghị) ⚡

```bash
# Tải và chạy script
wget https://raw.githubusercontent.com/sipeed/picoclaw/main/install-picoclaw-gamene.sh
bash install-picoclaw-gamene.sh

# Khởi động service
sudo systemctl start picoclaw
sudo systemctl status picoclaw
```

---

## Phương Pháp 2: Cài Đặt Thủ Công 🔧

### Bước 1: Tải Binary

```bash
# Đối với x86_64 (hầu hết VPS)
wget https://github.com/sipeed/picoclaw/releases/latest/download/picoclaw-linux-amd64
chmod +x picoclaw-linux-amd64
sudo mv picoclaw-linux-amd64 /usr/local/bin/picoclaw

# Đối với ARM64
wget https://github.com/sipeed/picoclaw/releases/latest/download/picoclaw-linux-arm64
chmod +x picoclaw-linux-arm64
sudo mv picoclaw-linux-arm64 /usr/local/bin/picoclaw
```

### Bước 2: Tạo Config

```bash
# Tạo thư mục
mkdir -p ~/.picoclaw

# Tạo file config
nano ~/.picoclaw/config.json
```

**Nội dung file `config.json`:**

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.picoclaw/workspace",
      "model_name": "gemini-flash",
      "max_tokens": 8192,
      "temperature": 0.7
    }
  },
  "model_list": [
    {
      "model_name": "gemini-flash",
      "model": "google/gemini-2.5-flash",
      "api_key": "sk-ed70bc16720b4b689bf69f81e3d221f5",
      "api_base": "https://api.gamene.online/v1"
    },
    {
      "model_name": "gemini-pro",
      "model": "google/gemini-2.5-pro",
      "api_key": "sk-ed70bc16720b4b689bf69f81e3d221f5",
      "api_base": "https://api.gamene.online/v1"
    },
    {
      "model_name": "claude-sonnet",
      "model": "anthropic/claude-sonnet-4-5",
      "api_key": "sk-ed70bc16720b4b689bf69f81e3d221f5",
      "api_base": "https://api.gamene.online/v1"
    },
    {
      "model_name": "deepseek-v3",
      "model": "deepseek/deepseek-chat",
      "api_key": "none",
      "api_base": "https://dep.apphay.io.vn/v1"
    },
    {
      "model_name": "deepseek-coder",
      "model": "deepseek/deepseek-coder",
      "api_key": "none",
      "api_base": "https://dep.apphay.io.vn/v1"
    }
  ],
  "tools": {
    "web_search": {
      "enabled": true,
      "provider": "auto"
    }
  },
  "gateway": {
    "host": "0.0.0.0",
    "port": 8080
  }
}
```

### Bước 3: Test Nhanh

```bash
# Test agent mode
picoclaw agent -m "Xin chào! Bạn là ai?" --model gemini-flash

# Test với Claude
picoclaw agent -m "Giải thích cách hoạt động của AI" --model claude-sonnet

# Test với Gemini Pro
picoclaw agent -m "Viết code Python đọc file CSV" --model gemini-pro
```

### Bước 4: Tạo Systemd Service

```bash
sudo nano /etc/systemd/system/picoclaw.service
```

**Nội dung:**

```ini
[Unit]
Description=PicoClaw AI Gateway (Gamene API)
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/picoclaw gateway start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Thay `YOUR_USERNAME` bằng username của bạn:**

```bash
# Lấy username hiện tại
whoami

# Sửa trong file service (thay yourusername)
sudo sed -i "s/YOUR_USERNAME/$(whoami)/g" /etc/systemd/system/picoclaw.service
```

### Bước 5: Khởi Động Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Khởi động
sudo systemctl start picoclaw

# Kiểm tra status
sudo systemctl status picoclaw

# Tự động khởi động khi reboot
sudo systemctl enable picoclaw

# Xem logs realtime
sudo journalctl -u picoclaw -f
```

---

## 📱 Kết Nối Bot Telegram

### 1. Tạo Bot Telegram

1. Mở [@BotFather](https://t.me/BotFather) trên Telegram
2. Gửi `/newbot`
3. Đặt tên và username cho bot
4. Lưu **token** (dạng: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Lấy User ID

1. Mở [@userinfobot](https://t.me/userinfobot)
2. Gửi bất kỳ tin nhắn nào
3. Lưu **ID** của bạn (dạng: `123456789`)

### 3. Cập Nhật Config

```bash
nano ~/.picoclaw/config.json
```

Sửa phần `channels.telegram`:

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
      "allow_from": ["123456789"]
    }
  }
}
```

### 4. Khởi Động Lại

```bash
sudo systemctl restart picoclaw
sudo systemctl status picoclaw
```

### 5. Test Bot

Mở bot Telegram của bạn và gửi:
- `Xin chào`
- `Giải thích machine learning`
- `Viết code Python tính Fibonacci`

---

## 🎮 Các Models Có Sẵn

### Gamene API Models

| Model Name | Model ID | Đặc Điểm |
|-----------|----------|----------|
| `gemini-flash` | `google/gemini-2.5-flash` | ⚡ Nhanh nhất, tiết kiệm |
| `gemini-pro` | `google/gemini-2.5-pro` | 🧠 Thông minh nhất |
| `gemini-flash-lite` | `google/gemini-2.5-flash-lite` | 🪶 Siêu nhẹ |
| `gemini-flash-thinking` | `google/gemini-2.5-flash-thinking` | 🤔 Có reasoning |
| `claude-sonnet` | `anthropic/claude-sonnet-4-5` | 📝 Giỏi viết, code |
| `claude-sonnet-thinking` | `anthropic/claude-sonnet-4-6-thinking` | 🧐 Có suy luận sâu |
| `gpt-oss` | `openai/gpt-oss-120b-medium` | 🆓 Open source |

### DeepSeek API Models (Free)

| Model Name | Model ID | Đặc Điểm |
|-----------|----------|----------|
| `deepseek-v3` | `deepseek/deepseek-chat` | 🚀 DeepSeek V3, đa năng |
| `deepseek-r1` | `deepseek/deepseek-reasoner` | 🧠 Reasoning, logic |
| `deepseek-coder` | `deepseek/deepseek-coder` | 💻 Chuyên code |

### Đổi Model Mặc Định

```bash
nano ~/.picoclaw/config.json
```

Sửa:
```json
{
  "agents": {
    "defaults": {
      "model_name": "claude-sonnet"  // Thay đổi ở đây
      // Hoặc: gemini-pro, deepseek-v3, deepseek-r1, deepseek-coder
    }
  }
}
```

**Gợi ý lựa chọn:**
- `gemini-flash` - Tốc độ + Chi phí thấp (mặc định)
- `gemini-pro` - Thông minh nhất
- `claude-sonnet` - Viết văn + Code tốt
- `deepseek-v3` - Miễn phí, đa năng
- `deepseek-coder` - Miễn phí, chuyên code

---

## 🔧 Quản Lý Service

```bash
# Xem status
sudo systemctl status picoclaw

# Khởi động
sudo systemctl start picoclaw

# Dừng
sudo systemctl stop picoclaw

# Khởi động lại
sudo systemctl restart picoclaw

# Xem logs
sudo journalctl -u picoclaw -f

# Xem logs gần đây nhất
sudo journalctl -u picoclaw -n 100

# Xem logs theo thời gian
sudo journalctl -u picoclaw --since "10 minutes ago"
```

---

## 🐛 Xử Lý Lỗi

### Lỗi: Cannot bind to 0.0.0.0:8080

```bash
# Kiểm tra port đang dùng
sudo lsof -i :8080

# Đổi port trong config
nano ~/.picoclaw/config.json
# Sửa: "port": 8081

sudo systemctl restart picoclaw
```

### Lỗi: API Key Invalid

```bash
# Kiểm tra config
cat ~/.picoclaw/config.json | grep api_key

# Sửa API key
nano ~/.picoclaw/config.json

sudo systemctl restart picoclaw
```

### Lỗi: Permission Denied

```bash
# Cấp quyền đúng
chmod +x /usr/local/bin/picoclaw
sudo chown $USER:$USER ~/.picoclaw -R
```

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8080/health
```

Response:
```json
{"status":"ok"}
```

### Readiness Check

```bash
curl http://localhost:8080/ready
```

---

## 🔐 Bảo Mật

### 1. Firewall

```bash
# Chỉ cho phép SSH và health check
sudo ufw allow 22/tcp
sudo ufw allow 8080/tcp
sudo ufw enable
```

### 2. Giới hạn truy cập nếu cần

Sửa trong config:
```json
{
  "gateway": {
    "host": "127.0.0.1",  // Chỉ local
    "port": 8080
  }
}
```

---

## 🎯 Tips & Tricks

### Test Nhanh Nhiều Models

```bash
# Gemini Flash
picoclaw agent -m "2+2=?" --model gemini-flash

# Claude Sonnet
picoclaw agent -m "2+2=?" --model claude-sonnet

# Gemini Pro
picoclaw agent -m "2+2=?" --model gemini-pro

# DeepSeek V3 (Free)
picoclaw agent -m "2+2=?" --model deepseek-v3

# DeepSeek R1 (Reasoning)
picoclaw agent -m "Giải thích cách giải phương trình bậc 2" --model deepseek-r1

# DeepSeek Coder (Code)
picoclaw agent -m "Viết code Python đọc CSV" --model deepseek-coder
```

### Interactive Mode

```bash
# Chế độ tương tác
picoclaw agent --model gemini-flash

# Hoặc với workspace riêng
picoclaw agent --model claude-sonnet --workspace /tmp/myworkspace
```

### Cập Nhật Version Mới

```bash
# Dừng service
sudo systemctl stop picoclaw

# Tải version mới
cd /tmp
wget https://github.com/sipeed/picoclaw/releases/latest/download/picoclaw-linux-amd64
chmod +x picoclaw-linux-amd64
sudo mv picoclaw-linux-amd64 /usr/local/bin/picoclaw

# Khởi động lại
sudo systemctl start picoclaw
```

---

## 📞 Hỗ Trợ

- 🐛 **Issues**: https://github.com/sipeed/picoclaw/issues
- 💬 **Discord**: https://discord.gg/V4sAZ9XWpN
- 📖 **Docs**: https://picoclaw.io

### API Providers
- **Gamene API**: https://api.gamene.online
- **DeepSeek API**: https://dep.apphay.io.vn (miễn phí)

---

## 🆓 DeepSeek API (Free Alternative)

### Giới thiệu

DeepSeek API là giải pháp thay thế **hoàn toàn miễn phí** thông qua domain tùy chỉnh `dep.apphay.io.vn`.

**Base URL:** `https://dep.apphay.io.vn`

### Models có sẵn

| Model | ID trong PicoClaw | Đặc điểm |
|-------|-------------------|----------|
| DeepSeek V3 | `deepseek-v3` | Model mặc định, đa năng |
| DeepSeek R1 | `deepseek-r1` | Reasoning, tư duy logic mạnh |
| DeepSeek Coder | `deepseek-coder` | Chuyên viết code |

### Test API trực tiếp

```bash
# Health check
curl https://dep.apphay.io.vn/health

# List models
curl https://dep.apphay.io.vn/models

# Test chat (Native API)
curl -X POST https://dep.apphay.io.vn/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Viết code Python tính Fibonacci",
    "model": "DeepSeek-Coder"
  }'
```

### Test với PicoClaw

```bash
# DeepSeek V3 - General purpose
picoclaw agent -m "Giải thích machine learning đơn giản" --model deepseek-v3

# DeepSeek R1 - Reasoning
picoclaw agent -m "Tại sao 0.1 + 0.2 không bằng 0.3 trong máy tính?" --model deepseek-r1

# DeepSeek Coder - Programming
picoclaw agent -m "Viết React component cho form đăng nhập" --model deepseek-coder
```

### So sánh hiệu suất

| Tiêu chí | Gamene API | DeepSeek API |
|----------|------------|--------------|
| **Giá** | Có giới hạn | ✅ Hoàn toàn miễn phí |
| **Speed** | ⚡ Rất nhanh | 🐢 Trung bình |
| **Models** | Gemini, Claude, GPT | DeepSeek V3, R1, Coder |
| **Reasoning** | Claude thinking | DeepSeek R1 |
| **Coding** | Claude Sonnet | DeepSeek Coder |

### Khi nào dùng DeepSeek?

✅ **Dùng khi:**
- Cần giải pháp hoàn toàn miễn phí
- Task liên quan coding
- Cần reasoning logic phức tạp
- Gamene API hết quota

❌ **Không dùng khi:**
- Cần tốc độ xử lý nhanh
- Cần khả năng đa ngôn ngữ tốt
- Cần vision/image understanding

### Lưu ý kỹ thuật

> ⚠️ **API này chạy qua Cloudflare Tunnel**:
> - Có thể chậm hơn API trực tiếp
> - Phụ thuộc vào DeepSeekProxyGUI.exe đang chạy
> - Timeout nên set >= 120 giây

---

## ✨ Tính Năng Nâng Cao

### Web Search (Tìm kiếm web)

```json
{
  "tools": {
    "web_search": {
      "enabled": true,
      "provider": "tavily",
      "tavily_api_key": "tvly-YOUR-KEY"
    }
  }
}
```

### Discord Bot

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_DISCORD_BOT_TOKEN",
      "allow_from": []
    }
  }
}
```

---

**🎉 Chúc bạn sử dụng PicoClaw vui vẻ!**
