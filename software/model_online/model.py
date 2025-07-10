from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from ultralytics import YOLO
import os
import base64
from datetime import datetime
import requests
import json
from werkzeug.utils import secure_filename
import logging
import pymysql
from decimal import Decimal
import gc
import psutil

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lihua_vue', 'public', 'assets', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
JAVA_BACKEND_URL = 'http://localhost:8080'
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'best_bicycle_violation.pt')

# 检测优化配置
DETECTION_CONFIG = {
    'imgsz': 640,           # 输入图片尺寸，可以尝试416、512、640
    'conf': 0.5,            # 置信度阈值，提高可减少误检和后处理时间
    'iou': 0.45,            # NMS IoU阈值
    'max_det': 100,         # 最大检测数量
    'device': 'cpu',        # 设备：'cpu' 或 'cuda' 或 '0'(GPU)
    'half': False,          # 是否使用FP16半精度（需要GPU支持）
    'verbose': False        # 关闭详细输出
}

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1234',
    'database': 'lihua',
    'charset': 'utf8mb4',
    'autocommit': True
}

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 加载YOLOv8模型
try:
    model = YOLO(MODEL_PATH)
    logger.info(f"模型加载成功: {MODEL_PATH}")
except Exception as e:
    logger.error(f"模型加载失败: {e}")
    model = None

# 类别颜色映射
CLASS_COLORS = {
    0: '#FF6B6B',  # 红色
    1: '#4ECDC4',  # 青色
    2: '#45B7D1',  # 蓝色
    3: '#96CEB4',  # 绿色
    4: '#FFEAA7',  # 黄色
    5: '#DDA0DD',  # 紫色
    6: '#FF9F43',  # 橙色
    7: '#F8C471',  # 浅橙色
    8: '#85C1E9',  # 浅蓝色
    9: '#F1C40F',  # 金色
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    """
    检查数据库连接
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 检查violation_record表是否存在
        cursor.execute("SHOW TABLES LIKE 'violation_record'")
        if cursor.fetchone():
            logger.info("violation_record表已存在")
        else:
            logger.warning("violation_record表不存在，请检查数据库")
        
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return False

def save_detection_to_database(detection_data):
    """
    将检测结果保存到violation_record表
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 计算平均置信度
        avg_confidence = 0.0
        if detection_data['detection_results']:
            confidences = [result['confidence'] for result in detection_data['detection_results']]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # 插入violation_record表
        insert_sql = """
        INSERT INTO violation_record (
            camera_id, image_path, upload_time, confidence, location
        ) VALUES (%s, %s, %s, %s, %s)
        """
        
        values = (
            1,  # 默认摄像头ID为1
            detection_data.get('result_filename', ''),  # 只保存文件名，不含路径
            detection_data.get('detection_time', ''),
            Decimal(str(avg_confidence)),
            detection_data.get('location', '')
        )
        
        cursor.execute(insert_sql, values)
        connection.commit()
        
        # 获取插入的记录ID
        record_id = cursor.lastrowid
        logger.info(f"违规记录保存成功，记录ID: {record_id}")
        
        cursor.close()
        connection.close()
        return record_id
    except Exception as e:
        logger.error(f"保存违规记录到数据库失败: {e}")
        return None

def get_java_backend_token():
    """
    从Java后端获取token
    这里采用简单的方式，实际项目中可能需要更复杂的认证逻辑
    """
    try:
        # 使用默认的管理员账户获取token
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = requests.post(
            f"{JAVA_BACKEND_URL}/system/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                return result.get('data')
            else:
                logger.error(f"获取token失败: {result.get('msg')}")
                return None
        else:
            logger.error(f"登录请求失败: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"获取token异常: {e}")
        return None

def send_detection_to_backend(detection_data, token):
    """
    将检测结果发送到Java后端数据库
    """
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # 构建检测记录数据
        record_data = {
            'location': detection_data.get('location', ''),
            'detectionTime': detection_data.get('detection_time', ''),
            'originalImage': detection_data.get('original_image_path', ''),
            'resultImage': detection_data.get('result_image_path', ''),
            'detectionResults': json.dumps(detection_data.get('detection_results', []), ensure_ascii=False),
            'detectionCount': detection_data.get('detection_count', 0),
            'hasDetections': detection_data.get('has_detections', False),
            'message': detection_data.get('message', '')
        }
        
        # 发送到Java后端API
        response = requests.post(
            f"{JAVA_BACKEND_URL}/api/detection/save",
            json=record_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"检测结果保存成功: {result}")
            return True
        else:
            logger.error(f"保存检测结果失败: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"发送检测结果异常: {e}")
        return False

def image_to_base64(image_path):
    """
    将图片文件转换为base64编码
    """
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_data}"
    except Exception as e:
        logger.error(f"图片转base64失败: {e}")
        return None

def image_to_base64_from_array(img_array):
    """
    将图片数组转换为base64编码
    """
    try:
        if img_array is None or img_array.size == 0:
            logger.error("图片数组为空")
            return None
            
        # 优化：使用更高的压缩比和质量设置
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
        success, buffer = cv2.imencode('.jpg', img_array, encode_param)
        
        if not success:
            logger.error("图片编码失败")
            return None
            
        base64_data = base64.b64encode(buffer).decode('utf-8')
        result = f"data:image/jpeg;base64,{base64_data}"
        logger.info(f"图片数组转base64成功，数据长度: {len(base64_data)}")
        return result
    except Exception as e:
        logger.error(f"图片数组转base64失败: {e}")
        return None

def preprocess_image(img, target_size=640):
    """
    图片预处理优化
    """
    try:
        # 获取原始尺寸
        h, w = img.shape[:2]
        
        # 如果图片过大，先进行快速缩放
        if max(h, w) > target_size * 2:
            scale = (target_size * 2) / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            logger.info(f"图片预缩放: {w}x{h} -> {new_w}x{new_h}")
        
        return img
    except Exception as e:
        logger.error(f"图片预处理失败: {e}")
        return img

@app.route('/detect', methods=['POST'])
def detect():
    if model is None:
        return jsonify({'error': '模型未加载成功'}), 500
    
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        location = request.form.get('location', '')
        
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式'}), 400
        
        # 读取图片进行检测（不保存原图）
        img_data = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'error': '图片读取失败'}), 400
        
        # 图片预处理优化
        img = preprocess_image(img, DETECTION_CONFIG['imgsz'])
        
        # 进行目标检测（使用优化参数）
        results = model(
            img,
            imgsz=DETECTION_CONFIG['imgsz'],
            conf=DETECTION_CONFIG['conf'],
            iou=DETECTION_CONFIG['iou'],
            max_det=DETECTION_CONFIG['max_det'],
            verbose=DETECTION_CONFIG['verbose']
        )
        
        # 处理检测结果
        detection_results = []
        has_detections = False
        
        # 在图片上绘制检测框
        result_img = img.copy()
        
        for result in results:
            if result.boxes is not None and len(result.boxes) > 0:
                has_detections = True
                for box in result.boxes:
                    # 获取边界框坐标
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    
                    # 获取类别和置信度，确保转换为Python原生类型
                    class_id = int(box.cls[0].cpu().numpy())
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    # 获取类别名称
                    class_name = model.names[class_id] if class_id in model.names else f"Class_{class_id}"
                    
                    # 获取颜色
                    color_hex = CLASS_COLORS.get(class_id, '#FF6B6B')
                    color_bgr = tuple(int(color_hex[i:i+2], 16) for i in (5, 3, 1))  # 转换为BGR格式
                    
                    # 优化：简化绘制过程，减少函数调用
                    # 绘制检测框
                    cv2.rectangle(result_img, (x1, y1), (x2, y2), color_bgr, 2)
                    
                    # 简化标签绘制
                    label = f"{class_name}: {confidence:.2f}"
                    # 使用固定的标签框大小，避免计算文本尺寸
                    label_height = 25
                    cv2.rectangle(result_img, (x1, y1 - label_height), 
                                (x1 + len(label) * 10, y1), color_bgr, -1)
                    cv2.putText(result_img, label, (x1 + 2, y1 - 8), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                    
                    # 添加到检测结果，确保所有数值都是Python原生类型
                    detection_results.append({
                        'className': class_name,
                        'confidence': float(confidence),
                        'color': color_hex,
                        'bbox': [int(x1), int(y1), int(x2), int(y2)]
                    })
        
        # 构建响应消息
        if has_detections:
            message = f"检测成功，共发现 {len(detection_results)} 个目标"
            
            # 只有检测到目标时才保存图片
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_filename = f"violation_{timestamp}.jpg"
            result_path = os.path.join(UPLOAD_FOLDER, result_filename)
            
            # 确保UPLOAD_FOLDER目录存在
            logger.info(f"检查UPLOAD_FOLDER目录: {UPLOAD_FOLDER}")
            logger.info(f"保存文件路径: {result_path}")
            
            # 直接确保UPLOAD_FOLDER存在，不用dirname
            if not os.path.exists(UPLOAD_FOLDER):
                logger.info(f"创建目录: {UPLOAD_FOLDER}")
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            else:
                logger.info(f"目录已存在: {UPLOAD_FOLDER}")
            
            # 保存图片
            success = cv2.imwrite(result_path, result_img)
            if not success:
                logger.error(f"图片保存失败: {result_path}")
                result_base64 = image_to_base64_from_array(result_img)  # 直接从数组转换
            else:
                logger.info(f"图片保存成功: {result_path}")
                # 转换检测结果图片为base64
                result_base64 = image_to_base64(result_path)
                if not result_base64:
                    logger.warning("文件转base64失败，使用数组转换")
                    result_base64 = image_to_base64_from_array(result_img)
            
            result_image_path = f"assets/images/{result_filename}"
        else:
            message = "未检测到任何目标"
            # 即使没有检测到目标，也返回原图作为结果图
            result_base64 = image_to_base64_from_array(result_img)
            result_image_path = ""
            result_filename = ""  # 未检测到目标时文件名为空
        
        # 转换原图为base64（用于前端显示）
        original_base64 = image_to_base64_from_array(img)
        
        # 构建检测数据
        detection_data = {
            'location': location,
            'detection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'result_image_path': result_image_path,  # 完整路径用于前端显示
            'result_filename': result_filename if has_detections else '',  # 只保存文件名到数据库
            'detection_results': detection_results,
            'detection_count': len(detection_results),
            'has_detections': has_detections,
            'message': message
        }
        
        # 如果有检测结果，保存到数据库
        if has_detections:
            record_id = save_detection_to_database(detection_data)
            if record_id:
                logger.info(f"检测结果已保存到数据库，记录ID: {record_id}")
            else:
                logger.warning("检测结果保存到数据库失败")
        else:
            logger.info("未检测到目标，不保存到数据库")
        
        # 构建响应
        response_data = {
            'original_image': original_base64,
            'result_image': result_base64,
            'detection_results': detection_results,
            'message': message,
            'has_detections': has_detections,
            'detection_time': detection_data['detection_time'],
            'location': location
        }
        
        logger.info(f"检测完成: {message}, 位置: {location}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"检测异常: {e}")
        return jsonify({'error': f'检测失败: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })



if __name__ == '__main__':
    logger.info("启动YOLOv8检测服务...")
    logger.info(f"模型路径: {MODEL_PATH}")
    logger.info(f"图片保存路径(相对): {UPLOAD_FOLDER}")
    logger.info(f"图片保存路径(绝对): {os.path.abspath(UPLOAD_FOLDER)}")
    logger.info(f"Java后端地址: {JAVA_BACKEND_URL}")
    
    # 检查路径是否正确
    expected_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lihua_vue', 'public', 'assets', 'images')
    logger.info(f"期望路径: {os.path.abspath(expected_path)}")
    logger.info(f"路径是否匹配: {os.path.abspath(UPLOAD_FOLDER) == os.path.abspath(expected_path)}")
    
    # 初始化数据库
    if init_database():
        logger.info("数据库连接成功")
    else:
        logger.error("数据库连接失败，请检查配置")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
