# 摄像头视频流系统配置指南 📹

## 🎯 系统概述

本系统支持：
- 实时摄像头视频流（HLS格式）
- 前端部署到公网服务器
- 多种摄像头接入方式
- 本地开发和生产环境配置

## 📦 前端依赖安装

### 1. 安装HLS.js依赖
```bash
cd lihua-vue
npm install hls.js
npm install @types/hls.js --save-dev
```

### 2. 配置环境变量
创建环境变量文件：

```bash
# .env.local (本地开发)
VITE_API_BASE_URL=http://localhost:8080
VITE_STREAM_BASE_URL=http://localhost:8080/stream

# .env.production (生产环境)
VITE_API_BASE_URL=http://your-server-ip:8080
VITE_STREAM_BASE_URL=http://your-server-ip:8080/stream
```

### 3. 配置TypeScript类型
在 `src/vite-env.d.ts` 中添加：

```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_STREAM_BASE_URL: string;
  // 其他环境变量...
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

## 🖥️ 后端配置

### 1. 服务器依赖安装
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg v4l-utils

# CentOS/RHEL
sudo yum install ffmpeg v4l-utils

# 检查摄像头设备
ls /dev/video*
```

### 2. 摄像头权限配置
```bash
# 添加用户到video组
sudo usermod -a -G video $USER

# 重新登录或重启生效
```

### 3. 创建HLS输出目录
```bash
sudo mkdir -p /tmp/hls
sudo chmod 777 /tmp/hls
```

## 🚀 部署方案

### 方案一：本地开发 + 远程服务器

#### 1. 本地开发环境
```bash
# 前端开发
cd lihua-vue
npm run dev

# 后端开发
cd lihua
./mvnw spring-boot:run
```

#### 2. 生产环境部署
```bash
# 构建前端
cd lihua-vue
npm run build

# 上传到服务器
scp -r dist/* user@your-server-ip:/var/www/html/

# 后端部署
cd lihua
./mvnw clean package
scp target/*.jar user@your-server-ip:/opt/lihua/
```

### 方案二：完全云端部署

#### 1. 服务器环境准备
```bash
# 安装基础环境
sudo apt update
sudo apt install -y nginx openjdk-17-jdk ffmpeg v4l-utils

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 2. 应用部署
```bash
# 克隆代码到服务器
git clone your-repo-url /opt/lihua-app
cd /opt/lihua-app

# 构建前端
cd lihua-vue
npm install
npm run build

# 配置Nginx
sudo cp nginx.conf /etc/nginx/sites-available/lihua
sudo ln -s /etc/nginx/sites-available/lihua /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 构建后端
cd ../lihua
./mvnw clean package

# 配置systemd服务
sudo cp lihua.service /etc/systemd/system/
sudo systemctl enable lihua
sudo systemctl start lihua
```

## 📝 配置文件

### 1. Nginx配置 (nginx.conf)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 视频流代理
    location /stream/ {
        proxy_pass http://localhost:8080/stream/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # HLS流特殊配置
        location ~* \.(m3u8)$ {
            add_header Cache-Control no-cache;
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Credentials true;
        }
        
        location ~* \.(ts)$ {
            add_header Cache-Control "public, max-age=3600";
            add_header Access-Control-Allow-Origin *;
        }
    }
}
```

### 2. 系统服务配置 (lihua.service)
```ini
[Unit]
Description=Lihua Camera System
After=network.target

[Service]
Type=simple
User=lihua
WorkingDirectory=/opt/lihua-app/lihua
ExecStart=/usr/bin/java -jar target/lihua-admin.jar
Restart=always
RestartSec=10

# 环境变量
Environment=JAVA_OPTS="-Xmx1024m -Xms512m"
Environment=SPRING_PROFILES_ACTIVE=prod

[Install]
WantedBy=multi-user.target
```

## 📱 摄像头接入方案

### 1. USB摄像头
```bash
# 检查设备
lsusb
ls /dev/video*

# 测试摄像头
ffmpeg -f v4l2 -i /dev/video0 -t 5 test.mp4
```

### 2. IP摄像头(RTSP)
修改 `VideoStreamServiceImpl.java` 中的摄像头源：
```java
// 替换USB摄像头配置
private static final String CAMERA_DEVICE = "rtsp://username:password@ip:port/path";

// 修改FFmpeg命令
ProcessBuilder processBuilder = new ProcessBuilder(
    "ffmpeg",
    "-i", CAMERA_DEVICE,  // RTSP输入
    "-c:v", "libx264",
    "-preset", "ultrafast",
    // ... 其他参数
);
```

### 3. 模拟摄像头（开发测试）
```bash
# 创建虚拟摄像头
sudo modprobe v4l2loopback

# 使用测试视频
ffmpeg -re -i test_video.mp4 -f v4l2 /dev/video0
```

## 🔧 故障排除

### 1. 摄像头问题
```bash
# 检查摄像头权限
ls -la /dev/video*

# 检查是否被占用
lsof /dev/video0

# 重启摄像头设备
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo
```

### 2. 网络问题
```bash
# 检查端口占用
netstat -tulpn | grep 8080

# 检查防火墙
sudo ufw status
sudo ufw allow 8080

# 检查HLS文件
ls -la /tmp/hls/
```

### 3. 前端播放问题
```bash
# 检查浏览器控制台
# 确认HLS.js正确加载
# 检查CORS设置
```

## 📊 性能优化

### 1. 视频参数调优
```java
// 低配置服务器优化
"-video_size", "640x480",    // 较小分辨率
"-framerate", "10",          // 较低帧率
"-crf", "28",                // 较低质量
"-preset", "ultrafast",      // 最快编码
```

### 2. 网络优化
```nginx
# 启用gzip压缩
gzip on;
gzip_types text/plain application/json application/javascript text/css;

# 设置缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. 服务器优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化内核参数
echo "net.core.rmem_max = 16777216" >> /etc/sysctl.conf
echo "net.core.wmem_max = 16777216" >> /etc/sysctl.conf
sysctl -p
```

## 📋 部署检查清单

### 前端部署
- [ ] 安装Node.js和npm
- [ ] 安装hls.js依赖
- [ ] 配置环境变量
- [ ] 构建生产版本
- [ ] 上传到服务器
- [ ] 配置Nginx

### 后端部署
- [ ] 安装Java 17+
- [ ] 安装FFmpeg
- [ ] 配置摄像头权限
- [ ] 创建HLS输出目录
- [ ] 构建Spring Boot应用
- [ ] 配置数据库连接
- [ ] 创建系统服务

### 网络配置
- [ ] 配置域名解析
- [ ] 开放必要端口
- [ ] 配置SSL证书（可选）
- [ ] 设置防火墙规则

### 测试验证
- [ ] 访问前端页面
- [ ] 测试摄像头连接
- [ ] 验证视频流播放
- [ ] 检查性能表现

## 💡 常见问题

### Q: 视频无法播放？
A: 检查摄像头权限、FFmpeg安装、HLS文件生成

### Q: 延迟太高？
A: 调整HLS段时长、减少缓冲、优化网络

### Q: 前端连接失败？
A: 检查API地址、CORS配置、网络连通性

### Q: 服务器性能不足？
A: 降低视频质量、减少帧率、增加服务器配置

---

🎉 **恭喜！** 按照本指南完成配置后，您就拥有了一个完整的摄像头视频流系统！ 