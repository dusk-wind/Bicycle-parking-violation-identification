#!/usr/bin/env python3

# Copyright (c) 2024，WuChao D-Robotics.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# 注意: 此程序在RDK板端运行，调用现有Spring Boot后端
# Attention: This program runs on RDK board, calling existing Spring Boot backend.

import cv2
import numpy as np
from scipy.special import softmax
from hobot_dnn import pyeasy_dnn as dnn  # BSP Python API

from time import time
import argparse
import logging 
import datetime
import json
import os

# 新增依赖库
try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False
    logging.warning("PyMySQL not available. Database features disabled.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("Requests not available. HTTP transfer features disabled.")

# 日志模块配置
logging.basicConfig(
    level = logging.DEBUG,
    format = '[%(name)s] [%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger("RDK_BICYCLE_VIOLATION")

# 配置参数
class Config:
    def __init__(self):
        # Spring Boot后端配置
        self.BACKEND_HOST = "192.168.76.203"   # 您的主机电脑IP地址
        self.BACKEND_PORT = 8080               # Spring Boot端口
        self.BASE_URL = f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT}"
        
        # API接口配置
        self.UPLOAD_URL = f"{self.BASE_URL}/system/attachment/storage/upload"
        self.VIOLATION_RECORD_URL = f"{self.BASE_URL}/system/violation/record"  # 需要创建
        
        # 数据库配置（直接访问数据库）
        self.DB_HOST = "192.168.76.203"
        self.DB_PORT = 3306
        self.DB_USER = "root"
        self.DB_PASSWORD = "1234"
        self.DB_DATABASE = "lihua"
        
        # 检测配置
        self.CAMERA_ID = 1
        self.LOCATION = "测试地点"
        self.ENABLE_DB_UPLOAD = True
        self.ENABLE_IMAGE_UPLOAD = True
        self.ENABLE_SPRING_BACKEND = True
        
        # 本地保存配置
        self.LOCAL_SAVE_PATH = "/tmp/detection_results/"

# 全局配置实例
config = Config()

def init_local_storage():
    """初始化本地存储目录"""
    if not os.path.exists(config.LOCAL_SAVE_PATH):
        os.makedirs(config.LOCAL_SAVE_PATH)
        logger.info(f"Created local storage directory: {config.LOCAL_SAVE_PATH}")

def upload_image_to_python_server(image, filename):
    """将图片上传到Python图片接收服务器"""
    if not REQUESTS_AVAILABLE:
        logger.warning("Requests not available")
        return None
    
    try:
        # 将OpenCV图像编码为JPEG格式的字节数据
        success, img_encoded = cv2.imencode('.jpg', image)
        if not success:
            logger.error("Failed to encode image")
            return None
        
        # 准备文件数据
        files = {
            'file': (filename, img_encoded.tobytes(), 'image/jpeg')
        }
        
        # 发送到Python图片接收服务器
        upload_url = f"http://{config.BACKEND_HOST}:8088/upload_image"
        response = requests.post(
            upload_url,
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                filename = result.get('filename')
                logger.info(f"✅ Image uploaded to Python server: {filename}")
                return filename
            else:
                logger.warning(f"⚠️ Python server error: {result.get('message', 'Unknown error')}")
                return None
        else:
            logger.warning(f"⚠️ Upload failed: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Image upload error: {e}")
        return None

def save_violation_record_to_db(detection_data, image_path=None):
    """直接保存违规记录到数据库"""
    if not PYMYSQL_AVAILABLE or not config.ENABLE_DB_UPLOAD:
        logger.warning("Database upload disabled or PyMySQL not available")
        return False
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_DATABASE,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 根据实际表结构插入违规记录
            sql = """
                INSERT INTO violation_record 
                (camera_id, image_path, confidence, location, upload_time)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            # 使用传入的image_path，如果没有则使用默认值
            final_image_path = image_path or detection_data.get('image_path', f"local:{detection_data.get('image_filename', 'unknown.jpg')}")
            
            cursor.execute(sql, (
                detection_data['camera_id'],
                final_image_path,
                detection_data['confidence'],
                detection_data['location'],
                detection_data.get('detection_time', datetime.datetime.now())
            ))
            
            # 获取插入记录的ID
            record_id = cursor.lastrowid
            
        connection.commit()
        connection.close()
        
        logger.info(f"✅ Violation record saved to database successfully (ID: {record_id})")
        return record_id
        
    except Exception as e:
        logger.error(f"❌ Database save failed: {e}")
        return False

def notify_violation_detection(detection_data):
    """通知Spring Boot后端有新的违规检测（仅发送通知，不保存数据）"""
    if not REQUESTS_AVAILABLE or not config.ENABLE_SPRING_BACKEND:
        logger.warning("Spring Backend disabled or Requests not available")
        return False
    
    try:
        # 准备违规记录数据用于通知
        violation_data = {
            'id': detection_data.get('record_id'),  # 从数据库插入后获取的ID
            'cameraId': detection_data['camera_id'],
            'location': detection_data['location'],
            'confidence': detection_data['confidence'],
            'imagePath': detection_data.get('image_path'),
            # 修复时间格式：使用后端@JsonFormat要求的格式 "yyyy-MM-dd HH:mm:ss"
            'uploadTime': detection_data['detection_time'].strftime('%Y-%m-%d %H:%M:%S') if detection_data.get('detection_time') else None
        }
        
        # 发送HTTP POST请求到通知接口
        notify_url = f"{config.BASE_URL}/api/violation/notify"
        response = requests.post(
            notify_url,
            json=violation_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            # 适配Result格式：code=200表示成功，msg为消息
            if result.get('code') == 200:
                logger.info("✅ Violation detection notification sent successfully")
                return True
            else:
                logger.warning(f"⚠️ Notification warning: {result.get('msg', 'Unknown error')}")
                return True  # 通知失败不影响主流程
        else:
            logger.warning(f"⚠️ Notification failed: HTTP {response.status_code}")
            return True  # 通知失败不影响主流程
            
    except Exception as e:
        logger.warning(f"⚠️ Notification error (not critical): {e}")
        return True  # 通知失败不影响主流程

def save_local_backup(image, detection_data, filename):
    """本地备份保存"""
    try:
        # 保存图片
        local_image_path = os.path.join(config.LOCAL_SAVE_PATH, filename)
        cv2.imwrite(local_image_path, image)
        
        # 保存检测数据（JSON格式）
        json_filename = filename.replace('.jpg', '.json')
        local_json_path = os.path.join(config.LOCAL_SAVE_PATH, json_filename)
        
        with open(local_json_path, 'w', encoding='utf-8') as f:
            json.dump(detection_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"📁 Local backup saved: {local_image_path}")
        return local_image_path
        
    except Exception as e:
        logger.error(f"❌ Local backup failed: {e}")
        return None

def test_backend_connection():
    """测试后端连接"""
    if not config.ENABLE_SPRING_BACKEND:
        logger.info("Spring Backend disabled, skipping connection test")
        return True
        
    try:
        # 测试后端是否可访问
        response = requests.get(f"{config.BASE_URL}/actuator/health", timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Backend connection successful: {config.BASE_URL}")
            return True
        else:
            logger.warning(f"⚠️ Backend health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Backend connection failed: {e}")
        logger.info(f"请确保Spring Boot后端已启动: {config.BASE_URL}")
        return False

def test_database_connection():
    """测试数据库连接"""
    if not PYMYSQL_AVAILABLE or not config.ENABLE_DB_UPLOAD:
        logger.info("Database upload disabled or PyMySQL not available")
        return True
        
    try:
        connection = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_DATABASE,
            charset='utf8mb4'
        )
        connection.close()
        logger.info(f"✅ Database connection successful: {config.DB_HOST}:{config.DB_PORT}/{config.DB_DATABASE}")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def process_detection_results(img, ids, scores, bboxes):
    """处理检测结果并上传到Spring Boot后端或直接数据库"""
    if len(ids) == 0:
        logger.info("❌ No violations detected")
        return
    
    current_time = datetime.datetime.now()
    timestamp_str = current_time.strftime("%Y%m%d_%H%M%S")
    
    logger.info(f"✅ Detected {len(ids)} violations")
    
    for i, (class_id, score, bbox) in enumerate(zip(ids, scores, bboxes)):
        x1, y1, x2, y2 = bbox
        logger.info(f"Violation {i+1}: position({x1}, {y1}, {x2}, {y2}) confidence: {score:.3f}")
        
        # 绘制检测结果
        draw_detection(img, (x1, y1, x2, y2), score, class_id)
        
        # 生成文件名
        filename = f"violation_cam{config.CAMERA_ID}_{timestamp_str}_{i+1:03d}.jpg"
        
        # 准备检测数据
        detection_data = {
            'camera_id': config.CAMERA_ID,
            'location': config.LOCATION,
            'detection_time': current_time,
            'confidence': float(score),
            'bbox': [int(x1), int(y1), int(x2), int(y2)],
            'class_id': int(class_id),
            'class_name': violation_names[class_id],
            'image_filename': filename
        }
        
        # 1. 本地备份保存
        local_path = save_local_backup(img, detection_data, filename)
        
        success = False
        record_id = None
        
        # 2. 上传图片到Python服务器
        image_filename = upload_image_to_python_server(img, filename)
        if image_filename:
            image_path = image_filename  # 只保存文件名，不加前缀
            detection_data['image_path'] = image_path
            logger.info(f"📸 Image uploaded to Python server: {image_filename}")
        else:
            # 如果上传失败，不保存图片路径（数据库中为NULL）
            detection_data['image_path'] = None
            logger.warning(f"⚠️ Failed to upload image to Python server, image_path set to NULL")
        
        # 3. 保存到数据库（使用已确定的image_path）
        if config.ENABLE_DB_UPLOAD:
            # 直接通过pymysql保存到数据库
            record_id = save_violation_record_to_db(detection_data, image_path)
            success = bool(record_id)
        
        # 4. 发送通知到Spring Boot（触发SSE消息）
        if config.ENABLE_SPRING_BACKEND:
            detection_data['record_id'] = record_id
            detection_data['image_path'] = image_path
            notify_violation_detection(detection_data)
        
        if success:
            logger.info(f"🎉 Violation record {i+1} processed successfully")
        else:
            logger.warning(f"⚠️ Violation record {i+1} failed to upload, saved locally only")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', type=str, default='bicycle_violation_640x640_nv12.bin', 
                        help="""Path to BPU Quantized *.bin Model for bicycle violation detection.""") 
    parser.add_argument('--test-img', type=str, default='test.jpg', help='Path to Load Test Image.')
    parser.add_argument('--img-save-path', type=str, default='bicycle_violation_result.jpg', help='Path to Save Result Image.')
    parser.add_argument('--classes-num', type=int, default=1, help='Classes Num to Detect (bicycle violation).')
    parser.add_argument('--reg', type=int, default=16, help='DFL reg layer.')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='IoU threshold.')
    parser.add_argument('--conf-thres', type=float, default=0.3, help='confidence threshold.')
    
    # 网络配置参数
    parser.add_argument('--backend-host', type=str, default=config.BACKEND_HOST, help='Spring Boot backend host IP')
    parser.add_argument('--db-host', type=str, default=config.DB_HOST, help='Database host IP')
    parser.add_argument('--camera-id', type=int, default=config.CAMERA_ID, help='Camera ID')
    parser.add_argument('--location', type=str, default=config.LOCATION, help='Detection location')
    parser.add_argument('--disable-db', action='store_true', help='Disable database upload')
    parser.add_argument('--disable-image-upload', action='store_true', help='Disable image upload')
    parser.add_argument('--disable-spring', action='store_true', help='Disable Spring Boot backend')
    
    opt = parser.parse_args()
    logger.info(opt)
    
    # 更新配置
    config.BACKEND_HOST = opt.backend_host
    config.DB_HOST = opt.db_host
    config.BASE_URL = f"http://{config.BACKEND_HOST}:{config.BACKEND_PORT}"
    config.UPLOAD_URL = f"{config.BASE_URL}/system/attachment/storage/upload"
    config.VIOLATION_RECORD_URL = f"{config.BASE_URL}/api/violation"
    config.CAMERA_ID = opt.camera_id
    config.LOCATION = opt.location
    config.ENABLE_DB_UPLOAD = not opt.disable_db
    config.ENABLE_IMAGE_UPLOAD = not opt.disable_image_upload
    config.ENABLE_SPRING_BACKEND = not opt.disable_spring
    
    logger.info(f"🌐 Spring Boot backend: {config.BASE_URL} (enabled: {config.ENABLE_SPRING_BACKEND})")
    logger.info(f"🗄️ Database: {config.DB_HOST}:{config.DB_PORT}/{config.DB_DATABASE} (enabled: {config.ENABLE_DB_UPLOAD})")
    logger.info(f"📹 Camera ID: {config.CAMERA_ID}")
    logger.info(f"📍 Location: {config.LOCATION}")
    
    # 测试连接
    backend_ok = test_backend_connection()
    database_ok = test_database_connection()
    
    if not backend_ok and not database_ok:
        logger.error("❌ Both backend and database connections failed. Please check configuration.")
        return
    
    # 初始化本地存储
    init_local_storage()

    # 实例化违规停车检测模型
    model = BicycleViolation_Detect(opt.model_path, opt.conf_thres, opt.iou_thres)
    # 读图
    img = cv2.imread(opt.test_img)
    if img is None:
        logger.error(f"❌ Cannot load image: {opt.test_img}")
        return
    
    # 准备输入数据
    input_tensor = model.bgr2nv12(img)
    # 推理
    outputs = model.c2numpy(model.forward(input_tensor))
    # 后处理
    ids, scores, bboxes = model.postProcess(outputs)
    
    # 处理检测结果并上传
    logger.info("\033[1;32m" + "Bicycle Violation Detection Results: " + "\033[0m")
    process_detection_results(img, ids, scores, bboxes)
    
    # 保存本地结果图片
    cv2.imwrite(opt.img_save_path, img)
    logger.info("\033[1;32m" + f"Local result saved: \"./{opt.img_save_path}\"" + "\033[0m")

class BaseModel:
    def __init__(self, model_file: str) -> None:
        # 加载BPU的bin模型
        try:
            begin_time = time()
            self.quantize_model = dnn.load(model_file)
            logger.debug("\033[1;31m" + "Load D-Robotics Quantize model time = %.2f ms"%(1000*(time() - begin_time)) + "\033[0m")
        except Exception as e:
            logger.error("❌ Failed to load model file: %s"%(model_file))
            logger.error(e)
            exit(1)

        logger.info("\033[1;32m" + "-> input tensors" + "\033[0m")
        for i, quantize_input in enumerate(self.quantize_model[0].inputs):
            logger.info(f"input[{i}], name={quantize_input.name}, type={quantize_input.properties.dtype}, shape={quantize_input.properties.shape}")

        logger.info("\033[1;32m" + "-> output tensors" + "\033[0m")
        for i, quantize_input in enumerate(self.quantize_model[0].outputs):
            logger.info(f"output[{i}], name={quantize_input.name}, type={quantize_input.properties.dtype}, shape={quantize_input.properties.shape}")

        self.model_input_height, self.model_input_width = self.quantize_model[0].inputs[0].properties.shape[2:4]

    def resizer(self, img: np.ndarray)->np.ndarray:
        img_h, img_w = img.shape[0:2]
        self.y_scale, self.x_scale = img_h/self.model_input_height, img_w/self.model_input_width
        return cv2.resize(img, (self.model_input_width, self.model_input_height), interpolation=cv2.INTER_NEAREST)

    def bgr2nv12(self, bgr_img: np.ndarray) -> np.ndarray:
        """
        Convert a BGR image to the NV12 format.
        """
        begin_time = time()
        bgr_img = self.resizer(bgr_img)
        height, width = bgr_img.shape[0], bgr_img.shape[1]
        area = height * width
        yuv420p = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2YUV_I420).reshape((area * 3 // 2,))
        y = yuv420p[:area]
        uv_planar = yuv420p[area:].reshape((2, area // 4))
        uv_packed = uv_planar.transpose((1, 0)).reshape((area // 2,))
        nv12 = np.zeros_like(yuv420p)
        nv12[:height * width] = y
        nv12[height * width:] = uv_packed

        logger.debug("\033[1;31m" + f"bgr8 to nv12 time = {1000*(time() - begin_time):.2f} ms" + "\033[0m")
        return nv12

    def forward(self, input_tensor: np.array) -> list[dnn.pyDNNTensor]:
        begin_time = time()
        quantize_outputs = self.quantize_model[0].forward(input_tensor)
        logger.debug("\033[1;31m" + f"forward time = {1000*(time() - begin_time):.2f} ms" + "\033[0m")
        return quantize_outputs

    def c2numpy(self, outputs) -> list[np.array]:
        begin_time = time()
        outputs = [dnnTensor.buffer for dnnTensor in outputs]
        logger.debug("\033[1;31m" + f"c to numpy time = {1000*(time() - begin_time):.2f} ms" + "\033[0m")
        return outputs

class BicycleViolation_Detect(BaseModel):
    def __init__(self, model_file: str, conf: float, iou: float):
        super().__init__(model_file)
        
        # 检查输出数量 - 违规停车检测应该有6个输出 (3个bbox + 3个cls)
        output_count = len(self.quantize_model[0].outputs)
        logger.info(f"Model has {output_count} outputs")
        if output_count != 6:
            logger.warning(f"Expected 6 outputs for YOLOv8, got {output_count}")
        
        # 检查模型输出类型判断是否需要量化系数
        output_dtypes = [output.properties.dtype for output in self.quantize_model[0].outputs]
        logger.info(f"Output data types: {output_dtypes}")
        
        if all(dtype == 'float32' for dtype in output_dtypes):
            # 输出是float32，说明模型已经包含反量化节点
            logger.info("✅ Model outputs float32 (已包含反量化节点)")
            self.s_bboxes_scale = None
            self.m_bboxes_scale = None  
            self.l_bboxes_scale = None
        else:
            # 尝试获取量化系数（针对bbox输出）
            try:
                self.s_bboxes_scale = self.quantize_model[0].outputs[1].properties.scale_data[np.newaxis, :]  # bbox输出
                self.m_bboxes_scale = self.quantize_model[0].outputs[3].properties.scale_data[np.newaxis, :]  # bbox输出
                self.l_bboxes_scale = self.quantize_model[0].outputs[5].properties.scale_data[np.newaxis, :]  # bbox输出
                logger.info("✅ Model with quantization scales (未去除反量化)")
                logger.info(f"Scale shapes: s={self.s_bboxes_scale.shape}, m={self.m_bboxes_scale.shape}, l={self.l_bboxes_scale.shape}")
            except Exception as e:
                logger.warning(f"无法获取量化系数: {e}")
                self.s_bboxes_scale = None
                self.m_bboxes_scale = None  
                self.l_bboxes_scale = None

        # DFL求期望的系数
        self.weights_static = np.array([i for i in range(16)]).astype(np.float32)[np.newaxis, np.newaxis, :]
        logger.info(f"{self.weights_static.shape = }")

        # anchors
        self.s_anchor = np.stack([np.tile(np.linspace(0.5, 79.5, 80), reps=80), 
                            np.repeat(np.arange(0.5, 80.5, 1), 80)], axis=0).transpose(1,0)
        self.m_anchor = np.stack([np.tile(np.linspace(0.5, 39.5, 40), reps=40), 
                            np.repeat(np.arange(0.5, 40.5, 1), 40)], axis=0).transpose(1,0)
        self.l_anchor = np.stack([np.tile(np.linspace(0.5, 19.5, 20), reps=20), 
                            np.repeat(np.arange(0.5, 20.5, 1), 20)], axis=0).transpose(1,0)
        logger.info(f"{self.s_anchor.shape = }, {self.m_anchor.shape = }, {self.l_anchor.shape = }")

        # 阈值配置
        self.input_image_size = 640
        self.conf = conf
        self.iou = iou
        self.conf_inverse = -np.log(1/conf - 1)
        logger.info("iou threshold = %.2f, conf threshold = %.2f"%(iou, conf))
        logger.info("sigmoid_inverse threshold = %.2f"%self.conf_inverse)

    def postProcess(self, outputs: list[np.ndarray]) -> tuple[list, list, list]:
        begin_time = time()
        
        # 检查输出数量
        if len(outputs) != 6:
            logger.error(f"Expected 6 outputs, got {len(outputs)}")
            return [], [], []
        
        # 动态检测输出格式和顺序
        logger.debug(f"Output shapes: {[out.shape for out in outputs]}")
        
        # 根据实际输出解析: cls-bbox-cls-bbox-cls-bbox (NHWC格式)
        # output[0]: (1, 80, 80, 1) - s_clses  
        # output[1]: (1, 80, 80, 64) - s_bboxes
        # output[2]: (1, 40, 40, 1) - m_clses
        # output[3]: (1, 40, 40, 64) - m_bboxes  
        # output[4]: (1, 20, 20, 1) - l_clses
        # output[5]: (1, 20, 20, 64) - l_bboxes
        
        s_clses = outputs[0].reshape(-1, 1)    # (6400, 1)
        s_bboxes = outputs[1].reshape(-1, 64)  # (6400, 64)
        m_clses = outputs[2].reshape(-1, 1)    # (1600, 1) 
        m_bboxes = outputs[3].reshape(-1, 64)  # (1600, 64)
        l_clses = outputs[4].reshape(-1, 1)    # (400, 1)
        l_bboxes = outputs[5].reshape(-1, 64)  # (400, 64)
        
        logger.debug(f"Reshaped: s_clses={s_clses.shape}, s_bboxes={s_bboxes.shape}")
        logger.debug(f"Reshaped: m_clses={m_clses.shape}, m_bboxes={m_bboxes.shape}")  
        logger.debug(f"Reshaped: l_clses={l_clses.shape}, l_bboxes={l_bboxes.shape}")

        # 分类阈值筛选
        s_valid_indices = np.flatnonzero(s_clses.flatten() >= self.conf_inverse)
        s_ids = np.zeros(len(s_valid_indices), dtype=np.int32)  # 只有一个类别，全部为0
        s_scores = s_clses.flatten()[s_valid_indices]

        m_valid_indices = np.flatnonzero(m_clses.flatten() >= self.conf_inverse)
        m_ids = np.zeros(len(m_valid_indices), dtype=np.int32)
        m_scores = m_clses.flatten()[m_valid_indices]

        l_valid_indices = np.flatnonzero(l_clses.flatten() >= self.conf_inverse)
        l_ids = np.zeros(len(l_valid_indices), dtype=np.int32)
        l_scores = l_clses.flatten()[l_valid_indices]

        # Sigmoid计算
        s_scores = 1 / (1 + np.exp(-s_scores))
        m_scores = 1 / (1 + np.exp(-m_scores))
        l_scores = 1 / (1 + np.exp(-l_scores))

        # Bounding Box处理
        s_bboxes_float32 = s_bboxes[s_valid_indices,:]
        m_bboxes_float32 = m_bboxes[m_valid_indices,:]
        l_bboxes_float32 = l_bboxes[l_valid_indices,:]

        # 应用量化系数（如果存在）
        if self.s_bboxes_scale is not None:
            s_bboxes_float32 = s_bboxes_float32.astype(np.float32) * self.s_bboxes_scale
            m_bboxes_float32 = m_bboxes_float32.astype(np.float32) * self.m_bboxes_scale
            l_bboxes_float32 = l_bboxes_float32.astype(np.float32) * self.l_bboxes_scale

        # dist2bbox (ltrb2xyxy)
        if len(s_valid_indices) > 0:
            s_ltrb_indices = np.sum(softmax(s_bboxes_float32.reshape(-1, 4, 16), axis=2) * self.weights_static, axis=2)
            s_anchor_indices = self.s_anchor[s_valid_indices, :]
            s_x1y1 = s_anchor_indices - s_ltrb_indices[:, 0:2]
            s_x2y2 = s_anchor_indices + s_ltrb_indices[:, 2:4]
            s_dbboxes = np.hstack([s_x1y1, s_x2y2])*8
        else:
            s_dbboxes = np.empty((0, 4))

        if len(m_valid_indices) > 0:
            m_ltrb_indices = np.sum(softmax(m_bboxes_float32.reshape(-1, 4, 16), axis=2) * self.weights_static, axis=2)
            m_anchor_indices = self.m_anchor[m_valid_indices, :]
            m_x1y1 = m_anchor_indices - m_ltrb_indices[:, 0:2]
            m_x2y2 = m_anchor_indices + m_ltrb_indices[:, 2:4]
            m_dbboxes = np.hstack([m_x1y1, m_x2y2])*16
        else:
            m_dbboxes = np.empty((0, 4))

        if len(l_valid_indices) > 0:
            l_ltrb_indices = np.sum(softmax(l_bboxes_float32.reshape(-1, 4, 16), axis=2) * self.weights_static, axis=2)
            l_anchor_indices = self.l_anchor[l_valid_indices,:]
            l_x1y1 = l_anchor_indices - l_ltrb_indices[:, 0:2]
            l_x2y2 = l_anchor_indices + l_ltrb_indices[:, 2:4]
            l_dbboxes = np.hstack([l_x1y1, l_x2y2])*32
        else:
            l_dbboxes = np.empty((0, 4))

        # 拼接所有结果
        if s_dbboxes.size > 0 or m_dbboxes.size > 0 or l_dbboxes.size > 0:
            dbboxes = np.concatenate((s_dbboxes, m_dbboxes, l_dbboxes), axis=0)
            scores = np.concatenate((s_scores, m_scores, l_scores), axis=0)
            ids = np.concatenate((s_ids, m_ids, l_ids), axis=0)

            # NMS
            if len(dbboxes) > 0:
                indices = cv2.dnn.NMSBoxes(dbboxes, scores, self.conf, self.iou)
                
                if len(indices) > 0:
                    # 还原到原始图像尺度
                    bboxes = dbboxes[indices] * np.array([self.x_scale, self.y_scale, self.x_scale, self.y_scale])
                    bboxes = bboxes.astype(np.int32)
                    
                    logger.debug("\033[1;31m" + f"Post Process time = {1000*(time() - begin_time):.2f} ms" + "\033[0m")
                    return ids[indices], scores[indices], bboxes
        
        logger.debug("\033[1;31m" + f"Post Process time = {1000*(time() - begin_time):.2f} ms" + "\033[0m")
        return [], [], []

# 违规停车类别名称
violation_names = ["illegal_parking"]

# 检测框颜色 - 只有一个类别，统一使用红色
VIOLATION_COLOR = (0, 0, 255)  # 红色 - 违规停车

def draw_detection(img: np.array, 
                   bbox: tuple[int, int, int, int],
                   score: float, 
                   class_id: int) -> None:
    """
    绘制违规停车检测结果
    """
    x1, y1, x2, y2 = bbox
    color = VIOLATION_COLOR  # 统一使用红色
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    label = f"{violation_names[class_id]}: {score:.2f}"
    (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    label_x, label_y = x1, y1 - 10 if y1 - 10 > label_height else y1 + 10
    cv2.rectangle(
        img, (label_x, label_y - label_height), (label_x + label_width, label_y + label_height), color, cv2.FILLED
    )
    cv2.putText(img, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

if __name__ == "__main__":
    main() 