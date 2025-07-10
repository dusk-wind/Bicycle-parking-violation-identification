# 前端部署到公网服务器指南

## 🚀 部署方案

### 方案一：使用 Nginx 部署静态文件

#### 1. 构建前端项目
```bash
# 在本地构建
npm run build

# 生成dist文件夹
```

#### 2. 上传到服务器
```bash
# 将dist文件夹上传到服务器
scp -r dist/* user@your-server-ip:/var/www/html/
```

#### 3. 配置Nginx
```nginx
# /etc/nginx/sites-available/lihua-vue
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名或IP
    
    root /var/www/html;
    index index.html;
    
    # 前端路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API代理到后端
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 方案二：使用Docker部署

#### 1. 创建Dockerfile
```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 2. 创建nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    server {
        listen 80;
        server_name localhost;
        
        root /usr/share/nginx/html;
        index index.html;
        
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        location /api/ {
            proxy_pass http://host.docker.internal:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

#### 3. 构建和运行
```bash
# 构建镜像
docker build -t lihua-vue .

# 运行容器
docker run -d -p 80:80 --name lihua-vue lihua-vue
```

## 🔧 配置修改

### 1. 修改API基础URL
```typescript
// src/utils/Request.ts
const baseURL = process.env.NODE_ENV === 'production' 
    ? 'http://your-server-ip:8080/api'  // 生产环境
    : 'http://localhost:8080/api';      // 开发环境
```

### 2. 环境变量配置
```bash
# .env.production
VITE_API_BASE_URL=http://your-server-ip:8080/api
VITE_STREAM_BASE_URL=http://your-server-ip:8080/stream
```

## 🚦 快速部署脚本

```bash
#!/bin/bash
# deploy.sh

echo "🚀 开始部署前端到公网服务器..."

# 1. 构建项目
npm run build

# 2. 上传到服务器
rsync -avz --delete dist/ user@your-server-ip:/var/www/html/

# 3. 重启nginx
ssh user@your-server-ip "sudo systemctl restart nginx"

echo "✅ 部署完成！"
echo "访问地址: http://your-server-ip"
``` 