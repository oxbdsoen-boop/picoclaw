# 🌐 DeepSeek API Documentation

**Base URL:** `https://dep.apphay.io.vn`

> Domain được kết nối qua Cloudflare Tunnel đến DeepSeek API Proxy - **Hoàn toàn miễn phí!**

---

## 🚀 Quick Start với PicoClaw

### 1. Thêm vào config

```json
{
  "model_list": [
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
  ]
}
```

### 2. Test với PicoClaw

```bash
# DeepSeek V3 - Đa năng
picoclaw agent -m "Giải thích quantum computing" --model deepseek-v3

# DeepSeek R1 - Reasoning mạnh
picoclaw agent -m "Tại sao trái đất tròn?" --model deepseek-r1

# DeepSeek Coder - Chuyên code
picoclaw agent -m "Viết API REST bằng Flask" --model deepseek-coder
```

---

## 📡 Native API Endpoints

### 1. Health Check
```bash
curl https://dep.apphay.io.vn/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

### 2. List Models
```bash
curl https://dep.apphay.io.vn/models
```

**Response:**
```json
{
  "models": [
    "DeepSeek-V1", "DeepSeek-V2", "DeepSeek-V2.5", "DeepSeek-V3",
    "DeepSeek-V3-0324", "DeepSeek-V3.1", "DeepSeek-V3.2",
    "DeepSeek-R1", "DeepSeek-R1-0528", "DeepSeek-R1-Distill",
    "DeepSeek-Prover-V1", "DeepSeek-Prover-V1.5", "DeepSeek-Prover-V2",
    "DeepSeek-VL", "DeepSeek-Coder", "DeepSeek-Coder-V2",
    "DeepSeek-Coder-6.7B-base", "DeepSeek-Coder-6.7B-instruct"
  ],
  "count": 18
}
```

---

### 3. Chat API (Native Format)

```bash
curl -X POST https://dep.apphay.io.vn/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Viết code Python tính Fibonacci",
    "model": "DeepSeek-Coder"
  }'
```

**Request Body:**
```json
{
  "message": "Nội dung câu hỏi",
  "model": "DeepSeek-V3"  // Optional, default: DeepSeek-V3
}
```

**Response:**
```json
{
  "success": true,
  "model": "DeepSeek-V3",
  "message": "Viết code Python tính Fibonacci",
  "response": "Đây là code Python tính Fibonacci:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```"
}
```

**Error Response:**
```json
{
  "error": "Message is required"
}
```

---

## 🤖 Models Available

### Production Models (Khuyến nghị dùng trong PicoClaw)

| Model | PicoClaw Config | Đặc Điểm | Use Case |
|-------|----------------|----------|----------|
| **DeepSeek-V3** | `deepseek-v3` | Đa năng, cân bằng | Tổng quát, chat, Q&A |
| **DeepSeek-R1** | `deepseek-r1` | Reasoning mạnh | Logic, toán học, phân tích |
| **DeepSeek-Coder** | `deepseek-coder` | Chuyên code | Viết code, debug, review |

### All Available Models

| Model Family | Models | Mô tả |
|--------------|--------|-------|
| **General** | V1, V2, V2.5, V3, V3.1, V3.2 | Models tổng quát |
| **Reasoning** | R1, R1-0528, R1-Distill | Models có khả năng suy luận |
| **Math/Proof** | Prover-V1, Prover-V1.5, Prover-V2 | Toán học, chứng minh |
| **Vision** | DeepSeek-VL | Hiểu ảnh + text |
| **Coding** | Coder, Coder-V2, Coder-6.7B | Chuyên viết code |

---

## 💻 Code Examples (Direct API)

### Python

```python
import requests

BASE_URL = "https://dep.apphay.io.vn"

def chat(message, model="DeepSeek-V3"):
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": message, "model": model},
        timeout=120
    )
    data = response.json()
    return data.get("response")

# Sử dụng
print(chat("Viết code Python đọc CSV"))
print(chat("Giải phương trình x^2 - 5x + 6 = 0", "DeepSeek-R1"))
```

### JavaScript (Node.js)

```javascript
const fetch = require('node-fetch');

const BASE_URL = "https://dep.apphay.io.vn";

async function chat(message, model = "DeepSeek-V3") {
    const response = await fetch(`${BASE_URL}/chat`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message, model})
    });
    
    const data = await response.json();
    return data.response;
}

// Sử dụng
chat("Xin chào").then(console.log);
```

### cURL

```bash
# General chat
curl -X POST https://dep.apphay.io.vn/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "model": "DeepSeek-V3"}'

# Coding task
curl -X POST https://dep.apphay.io.vn/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Write a React hook for fetching data", "model": "DeepSeek-Coder"}'

# Reasoning task
curl -X POST https://dep.apphay.io.vn/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain why sqrt(2) is irrational", "model": "DeepSeek-R1"}'
```

---

## 🔧 Integration Examples

### N8N Workflow

**HTTP Request Node:**
- **Method:** POST
- **URL:** `https://dep.apphay.io.vn/chat`
- **Body (JSON):**
```json
{
  "message": "{{$json.user_input}}",
  "model": "DeepSeek-V3"
}
```

### Python + OpenAI SDK (Compatible Mode)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://dep.apphay.io.vn/v1",
    api_key="none"  # Not required
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "Hello"}
    ]
)

print(response.choices[0].message.content)
```

---

## 📊 Performance & Limitations

### Advantages ✅
- ✅ **Hoàn toàn miễn phí**
- ✅ **Không cần API key**
- ✅ **Reasoning mạnh (R1 model)**
- ✅ **Code generation tốt**

### Limitations ⚠️
- ⏱️ **Latency cao hơn** (Cloudflare Tunnel)
- 🌐 **Phụ thuộc proxy server** (DeepSeekProxyGUI.exe phải chạy)
- 🚫 **Không có rate limit rõ ràng** (có thể bị giới hạn)
- 📝 **Tiếng Việt kém hơn** Gemini/Claude

### Timeout Settings

```json
{
  "request_timeout": 300  // 300 giây (5 phút)
}
```

> ⚠️ **Lưu ý:** Set timeout >= 120 giây vì AI generation cần thời gian.

---

## 🔐 Security & Infrastructure

### Cloudflare Protection
- ✅ SSL/TLS tự động (HTTPS)
- ✅ DDoS Protection
- ✅ Không expose IP thật server
- ✅ Global CDN

### Architecture

```
User Request 
  → https://dep.apphay.io.vn (Cloudflare)
    → Cloudflare Tunnel
      → DeepSeekProxyGUI.exe (Local Server)
        → DeepSeek Official API
```

---

## 🆚 So Sánh với Gamene API

| Tiêu Chí | Gamene API | DeepSeek API |
|----------|------------|--------------|
| **Cost** | Có quota/limit | ✅ Free unlimited |
| **Speed** | ⚡⚡⚡ Very Fast | 🐢 Medium (tunnel overhead) |
| **Models** | Gemini, Claude, GPT | DeepSeek only |
| **Reasoning** | Claude Thinking | DeepSeek R1 ⭐ |
| **Coding** | Claude Sonnet | DeepSeek Coder ⭐ |
| **Vietnamese** | ⭐⭐⭐ Excellent | ⭐⭐ Good |
| **Vision** | Gemini Pro Image | DeepSeek-VL |
| **Reliability** | ⭐⭐⭐ High | ⭐⭐ Medium |

### Khi nào dùng DeepSeek?

✅ **Nên dùng:**
- Budget = $0
- Task liên quan code/programming
- Cần reasoning logic phức tạp (toán, logic)
- Gamene API hết quota
- Không yêu cầu tốc độ cao

❌ **Không nên dùng:**
- Cần latency thấp
- Vietnamese language priority
- Production critical systems
- Vision/multimodal tasks (dùng Gemini)

---

## 🐛 Troubleshooting

### API không hoạt động

```bash
# 1. Kiểm tra health
curl https://dep.apphay.io.vn/health

# 2. Kiểm tra DNS
nslookup dep.apphay.io.vn

# 3. Test với simple request
curl -X POST https://dep.apphay.io.vn/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### Timeout Error

```json
{
  "request_timeout": 300  // Tăng timeout lên 5 phút
}
```

### Model không tồn tại

```bash
# Lấy danh sách models
curl https://dep.apphay.io.vn/models
```

---

## 📞 Support

Nếu API không hoạt động:
1. ✅ Kiểm tra DeepSeekProxyGUI.exe đã start server chưa
2. ✅ Kiểm tra Cloudflare Tunnel đang chạy
3. ✅ Kiểm tra domain `dep.apphay.io.vn` accessible

---

## 📚 Related Documentation

- [PicoClaw Installation Guide](../INSTALL_GAMENE_VPS.md)
- [Gamene API Documentation](https://api.gamene.online)
- [PicoClaw Main Docs](../README.md)

---

**🆓 DeepSeek API - Free AI for Everyone!**
