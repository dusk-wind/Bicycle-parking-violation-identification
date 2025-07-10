#!/usr/bin/env python3
"""
图片接收服务器
在Windows电脑上运行，接收RDK发送的违规检测图片
"""
import os
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

class ImageReceiveHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """处理POST请求，接收图片"""
        try:
            # 检查路径
            if self.path != '/upload_image':
                self.send_error(404, "Not Found")
                return
            
            # 获取内容长度
            content_length = int(self.headers['Content-Length'])
            
            # 读取POST数据
            post_data = self.rfile.read(content_length)
            
            # 解析multipart/form-data
            boundary = self.headers['Content-Type'].split('boundary=')[1]
            
            # 简单解析（适用于图片上传）
            parts = post_data.split(f'--{boundary}'.encode())
            
            image_data = None
            filename = None
            
            for part in parts:
                if b'Content-Disposition: form-data; name="file"' in part:
                    # 提取文件名
                    if b'filename=' in part:
                        filename_start = part.find(b'filename="') + 10
                        filename_end = part.find(b'"', filename_start)
                        filename = part[filename_start:filename_end].decode()
                    
                    # 提取图片数据
                    data_start = part.find(b'\r\n\r\n') + 4
                    if data_start > 3:
                        image_data = part[data_start:-2]  # 去掉结尾的\r\n
                        break
            
            if image_data and filename:
                # 保存到前端目录
                frontend_images_dir = "lihua_vue/public/assets/images"
                os.makedirs(frontend_images_dir, exist_ok=True)
                
                filepath = os.path.join(frontend_images_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] 图片已保存: {filename}")
                
                # 返回成功响应
                response = {
                    "status": "success",
                    "message": "图片上传成功",
                    "filename": filename,
                    "path": f"assets/images/{filename}"
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            else:
                raise Exception("未找到图片数据")
                
        except Exception as e:
            print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] 上传失败: {e}")
            
            # 返回错误响应
            error_response = {
                "status": "error",
                "message": str(e)
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_GET(self):
        """处理GET请求，返回服务器状态"""
        if self.path == '/status':
            response = {
                "status": "running",
                "message": "图片接收服务器正在运行",
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
        else:
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        """重写日志方法，减少输出"""
        pass

def run_server(host='0.0.0.0', port=8088):
    """运行图片接收服务器"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, ImageReceiveHandler)
    
    print(f"🌐 图片接收服务器启动成功!")
    print(f"📍 监听地址: http://{host}:{port}")
    print(f"📁 保存目录: lihua_vue/public/assets/images/")
    print(f"🔗 状态检查: http://{host}:{port}/status")
    print(f"📤 上传端点: http://{host}:{port}/upload_image")
    print("=" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        httpd.server_close()

if __name__ == "__main__":
    # 确保在正确的目录下运行
    if not os.path.exists("lihua_vue"):
        print("❌ 请在包含lihua_vue文件夹的目录下运行此脚本")
        exit(1)
    
    run_server() 