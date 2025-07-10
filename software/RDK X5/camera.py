import cv2
import threading
import time
import os
import glob
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

class CameraStreamer:
    def __init__(self):
        self.camera = None
        self.is_streaming = False
        self.frame = None
        self.frame_lock = threading.Lock()
        self.current_device = None
        self.camera_info = {
            'id': 1,
            'serial': 'CAM001',
            'interfaceType': 'USB',
            'connected': False,
            'lastUpdated': datetime.now().isoformat()
        }

    def detect_camera_devices(self):
        """自动检测可用的摄像头设备"""
        available_devices = []
        
        # 方法1: 检查/dev/video*设备文件
        try:
            video_devices = glob.glob('/dev/video*')
            for device_path in sorted(video_devices):
                device_num = int(device_path.split('video')[1])
                # 尝试打开设备
                test_cap = cv2.VideoCapture(device_num)
                if test_cap.isOpened():
                    # 尝试读取一帧来确认设备可用
                    ret, frame = test_cap.read()
                    if ret:
                        available_devices.append({
                            'device_num': device_num,
                            'device_path': device_path,
                            'resolution': (int(test_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                                         int(test_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                        })
                        print(f"检测到可用摄像头: {device_path} (设备号: {device_num})")
                test_cap.release()
        except Exception as e:
            print(f"检测摄像头设备时出错: {e}")
        
        # 方法2: 如果方法1失败，尝试遍历设备号0-10
        if not available_devices:
            print("使用备用检测方法...")
            for i in range(10):
                try:
                    test_cap = cv2.VideoCapture(i)
                    if test_cap.isOpened():
                        ret, frame = test_cap.read()
                        if ret:
                            available_devices.append({
                                'device_num': i,
                                'device_path': f'/dev/video{i}',
                                'resolution': (int(test_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                                             int(test_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                            })
                            print(f"检测到可用摄像头: 设备号 {i}")
                    test_cap.release()
                except:
                    continue
        
        return available_devices

    def start_camera(self):
        """启动摄像头，自动检测可用设备"""
        try:
            # 检测可用的摄像头设备
            available_devices = self.detect_camera_devices()
            
            if not available_devices:
                print("未检测到可用的摄像头设备")
                return False
            
            # 选择第一个可用的摄像头设备
            selected_device = available_devices[0]
            device_num = selected_device['device_num']
            
            print(f"尝试连接摄像头设备: {selected_device['device_path']} (设备号: {device_num})")
            
            self.camera = cv2.VideoCapture(device_num)
            if not self.camera.isOpened():
                print(f"无法打开摄像头设备 {device_num}")
                return False

            # 设置摄像头参数
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # 测试读取一帧
            ret, test_frame = self.camera.read()
            if not ret:
                print("摄像头打开成功但无法读取画面")
                self.camera.release()
                return False

            self.is_streaming = True
            self.current_device = selected_device
            self.camera_info['connected'] = True
            self.camera_info['lastUpdated'] = datetime.now().isoformat()
            self.camera_info['serial'] = f"CAM-{device_num:03d}"
            
            # 启动帧捕获线程
            threading.Thread(target=self._capture_frames, daemon=True).start()
            
            print(f"摄像头启动成功! 设备: {selected_device['device_path']}, 分辨率: {selected_device['resolution']}")
            return True
            
        except Exception as e:
            print(f"启动摄像头时发生错误: {e}")
            return False

    def stop_camera(self):
        """停止摄像头"""
        self.is_streaming = False
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.current_device = None
        self.camera_info['connected'] = False
        self.camera_info['lastUpdated'] = datetime.now().isoformat()
        print("摄像头已停止")
        return True

    def _capture_frames(self):
        """捕获视频帧的线程函数"""
        consecutive_failures = 0
        max_failures = 30  # 连续失败30次后停止
        
        while self.is_streaming and self.camera:
            try:
                ret, frame = self.camera.read()
                if ret:
                    with self.frame_lock:
                        self.frame = frame
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        print("连续读取失败，停止摄像头")
                        self.stop_camera()
                        break
                    time.sleep(0.1)
            except Exception as e:
                print(f"帧捕获错误: {e}")
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    self.stop_camera()
                    break
                time.sleep(0.1)

    def get_frame(self):
        """获取当前帧"""
        with self.frame_lock:
            return self.frame.copy() if self.frame is not None else None

    def generate_frames(self):
        """生成视频流帧"""
        while self.is_streaming:
            frame = self.get_frame()
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.033)  # 约30fps

    def get_device_info(self):
        """获取当前设备信息"""
        if self.current_device:
            return {
                'device_path': self.current_device['device_path'],
                'device_num': self.current_device['device_num'],
                'resolution': self.current_device['resolution']
            }
        return None

streamer = CameraStreamer()

@app.route('/api/camera/status', methods=['GET'])
def get_camera_status():
    """获取摄像头状态"""
    device_info = streamer.get_device_info()
    camera_info = streamer.camera_info.copy()
    
    # 添加设备信息到返回数据
    if device_info:
        camera_info['devicePath'] = device_info['device_path']
        camera_info['deviceNum'] = device_info['device_num']
        camera_info['resolution'] = f"{device_info['resolution'][0]}x{device_info['resolution'][1]}"
    
    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': {
            'camera': camera_info,
            'streamUrl': 'http://192.168.76.178:5050/stream'  # 请手动修改为你的实际IP
        }
    })

@app.route('/api/camera/toggle', methods=['POST'])
def toggle_camera():
    """切换摄像头状态"""
    data = request.get_json()
    connect = data.get('connect', False)

    if connect:
        success = streamer.start_camera()
        msg = '摄像头连接成功' if success else '摄像头连接失败，请检查设备'
        code = 200 if success else 500
    else:
        success = streamer.stop_camera()
        msg = '摄像头已断开' if success else '摄像头断开失败'
        code = 200 if success else 500

    return jsonify({'code': code, 'msg': msg})

@app.route('/stream')
def video_stream():
    """视频流接口"""
    if not streamer.is_streaming:
        return jsonify({'error': '摄像头未连接'}), 400
    return Response(streamer.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/camera/devices', methods=['GET'])
def list_camera_devices():
    """列出所有可用的摄像头设备"""
    devices = streamer.detect_camera_devices()
    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': {
            'devices': devices,
            'count': len(devices)
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    device_info = streamer.get_device_info()
    return jsonify({
        'status': 'healthy',
        'camera_connected': streamer.camera_info['connected'],
        'streaming': streamer.is_streaming,
        'current_device': device_info,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 60)
    print("摄像头服务启动中...")
    print("=" * 60)
    
    # 启动时检测可用设备
    devices = streamer.detect_camera_devices()
    if devices:
        print(f"检测到 {len(devices)} 个可用摄像头设备:")
        for device in devices:
            print(f"  - {device['device_path']} (设备号: {device['device_num']}, 分辨率: {device['resolution']})")
    else:
        print("⚠️  警告: 未检测到可用的摄像头设备")
    
    print(f"\n服务地址: http://0.0.0.0:5050")
    print(f"视频流地址: http://你的IP:5050/stream")
    print(f"设备列表: http://你的IP:5050/api/camera/devices")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5050, debug=False, threaded=True) 