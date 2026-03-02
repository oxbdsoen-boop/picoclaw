# 🐳 PicoClaw Docker Setup Guide

> Cài đặt PicoClaw trên Docker với Gamene & DeepSeek API

## 🚀 Nhanh nhất - 1 lệnh

```bash
# 1. Clone repo
git clone https://github.com/sipeed/picoclaw.git
cd picoclaw

# 2. Copy config Gamene
cp config/config.gamene.json docker/data/config.json

# 3. Chạy gateway (background)
docker compose -f docker/docker-compose.yml --profile gateway up -d

# 4. Kiểm tra logs
docker compose -f docker/docker-compose.yml logs -f picoclaw-gateway

# 5. Test
docker compose -f docker/docker-compose.yml --profile agent run --rm picoclaw-agent -m "Xin chào!"
```

---

## 📋 Hướng Dẫn Chi Tiết

### **Bước 1: Chuẩn Bị**

```bash
# Cài Docker (nếu chưa có)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker

# Cài Docker Compose
sudo apt install docker-compose-plugin -y

# Verify
docker --version
docker compose version
```

### **Bước 2: Setup PicoClaw Docker**

```bash
# Clone repo
git clone https://github.com/sipeed/picoclaw.git
cd picoclaw

# Tạo thư mục dữ liệu
mkdir -p docker/data

# Tạo config từ file Gamene
cp config/config.gamene.json docker/data/config.json

# Kiểm tra config
cat docker/data/config.json
```

### **Bước 3: Khởi Động Docker Container**

```bash
# Lần đầu chạy (sẽ tạo config và thoát)
docker compose -f docker/docker-compose.yml --profile gateway up

# Nhấn Ctrl+C để dừng

# Khởi động lại ở background
docker compose -f docker/docker-compose.yml --profile gateway up -d

# Kiểm tra container đang chạy
docker compose -f docker/docker-compose.yml ps
```

### **Bước 4: Kiểm Tra Logs**

```bash
# Xem logs realtime
docker compose -f docker/docker-compose.yml logs -f picoclaw-gateway

# Xem 100 dòng cuối
docker compose -f docker/docker-compose.yml logs --tail 100

# Dừng xem logs
# Ctrl+C
```

### **Bước 5: Test API**

```bash
# Health check
curl http://localhost:8080/health

# Test agent mode (one-shot)
docker compose -f docker/docker-compose.yml --profile agent run --rm picoclaw-agent -m "2+2=?"

# Test với model khác
docker compose -f docker/docker-compose.yml --profile agent run --rm picoclaw-agent -m "Code Python sort list" --model deepseek-coder

# Interactive mode
docker compose -f docker/docker-compose.yml --profile agent run --rm picoclaw-agent
```

---

## 🎯 Các Lệnh Thường Dùng

### **Quản Lý Container**

```bash
# Khởi động
docker compose -f docker/docker-compose.yml --profile gateway up -d

# Dừng
docker compose -f docker/docker-compose.yml --profile gateway down

# Khởi động lại
docker compose -f docker/docker-compose.yml --profile gateway restart

# Xóa container (giữ config)
docker compose -f docker/docker-compose.yml --profile gateway down

# Xóa hoàn toàn (xóa cả config)
docker compose -f docker/docker-compose.yml --profile gateway down -v
```

### **Xem Logs**

```bash
# Logs realtime
docker compose -f docker/docker-compose.yml logs -f picoclaw-gateway

# 50 dòng gần nhất
docker compose -f docker/docker-compose.yml logs --tail 50

# Logs từ 10 phút trước
docker compose -f docker/docker-compose.yml logs --since 10m
```

### **Chỉnh Sửa Config**

```bash
# Sửa config
nano docker/data/config.json

# Khởi động lại để apply
docker compose -f docker/docker-compose.yml --profile gateway restart

# Kiểm tra change
docker compose -f docker/docker-compose.yml logs --tail 20
```

---

## 🔧 Docker Compose Tùy Chỉnh

Nếu muốn custom, tạo file `docker-compose.yml` riêng:

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  picoclaw:
    image: docker.io/sipeed/picoclaw:latest
    container_name: picoclaw-gateway
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - ./data:/root/.picoclaw
    environment:
      - PICOCLAW_GATEWAY_HOST=0.0.0.0
      - PICOCLAW_GATEWAY_PORT=8080
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Reverse proxy (Caddy)
  caddy:
    image: caddy:latest
    container_name: picoclaw-caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
      - caddy-config:/config
    depends_on:
      - picoclaw

volumes:
  caddy-data:
  caddy-config:
EOF
```

Chạy:
```bash
docker compose up -d
```

---

## 🌐 Port Mapping

| Service | Container Port | Host Port | Mục đích |
|---------|----------------|-----------|---------|
| PicoClaw Gateway | 8080 | 8080 | API & Health checks |
| Caddy Reverse Proxy | 80, 443 | 80, 443 | HTTP/HTTPS |

### Mở firewall (nếu cần)

```bash
# UFW
sudo ufw allow 8080/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

---

## 🔐 Các Config Quan Trọng

### **1. Mount Volume (Dữ liệu persistence)**

```yaml
volumes:
  - ./docker/data:/root/.picoclaw
```

→ Config, logs, workspace lưu tại `./docker/data`

### **2. Restart Policy**

```yaml
restart: unless-stopped
```

→ Tự động khởi động lại khi container crash

### **3. Health Check**

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

→ Kiểm tra container liveness mỗi 30 giây

### **4. Environment Variables**

```yaml
environment:
  - PICOCLAW_GATEWAY_HOST=0.0.0.0
  - PICOCLAW_GATEWAY_PORT=8080
```

→ Cấu hình host/port từ env

---

## 🚨 Troubleshooting

### **Container không khởi động**

```bash
# Kiểm tra logs
docker compose logs picoclaw-gateway

# Kiểm tra image
docker images | grep picoclaw

# Pull image mới
docker pull docker.io/sipeed/picoclaw:latest

# Khởi động lại
docker compose restart picoclaw-gateway
```

### **Port đã được sử dụng**

```bash
# Kiểm tra port
sudo lsof -i :8080

# Hoặc đổi port trong compose
# ports:
#   - "9090:8080"  <- 9090 là port VPS của bạn

docker compose restart
```

### **Config không load**

```bash
# Kiểm tra file tồn tại
ls -la docker/data/config.json

# Kiểm tra permissions
chmod 644 docker/data/config.json

# Xóa cache và restart
docker compose down -v
docker compose up -d
```

---

## 📊 Monitor Container

```bash
# Status tất cả container
docker ps -a

# CPU/RAM usage
docker stats

# Inspect container
docker inspect picoclaw-gateway

# View network
docker network ls
docker inspect picoclaw_default
```

---

## 🆚 So Sánh: Docker vs VPS Binary

| Tiêu Chí | Docker | Binary |
|----------|--------|--------|
| **Cài đặt** | 🐳 Container ready | 📦 Thủ công |
| **Cập nhật** | `docker pull` | Tải binary mới |
| **Config** | Riêng biệt | Chung hệ thống |
| **Resource** | Isolation tốt | Lightweight |
| **Production** | ⭐⭐⭐ Có hay dùng | ⭐⭐⭐ Cũng dùng |

---

## 🎁 Advanced: Docker Swarm / Kubernetes

### Swarm (Simple)

```bash
docker swarm init
docker stack deploy -c docker-compose.yml picoclaw
```

### Kubernetes (Complex)

```bash
kubectl apply -f k8s-deployment.yaml
```

---

## 📞 Support

- 📖 Docs: https://picoclaw.io
- 🐛 Issues: https://github.com/sipeed/picoclaw/issues
- 💬 Discord: https://discord.gg/V4sAZ9XWpN

---

**🐳 Enjoy PicoClaw on Docker!**
