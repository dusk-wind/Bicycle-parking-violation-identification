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

"""
RDK X5 视频检测程序 - 使用BIN模型进行实时自行车违停检测
基于hobot_dnn进行硬件加速推理
"""

import cv2
import numpy as np
from scipy.special import softmax
from hobot_dnn import pyeasy_dnn as dnn

import time
import argparse
import logging
import datetime
import os

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] [%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("RDK_VIDEO_DETECTION")

class BaseModel:
    def __init__(self, model_file: str) -> None:
        # 加载BPU的bin模型
        try:
            begin_time = time.time()
            self.quantize_model = dnn.load(model_file)
            logger.info(f"✅ Load BPU model time = {1000*(time.time() - begin_time):.2f} ms")
        except Exception as e:
            logger.error(f"❌ Failed to load model file: {model_file}")
            logger.error(e)
            exit(1)

        logger.info("🔍 Model Input Tensors:")
        for i, quantize_input in enumerate(self.quantize_model[0].inputs):
            logger.info(f"  input[{i}]: {quantize_input.name}, {quantize_input.properties.dtype}, {quantize_input.properties.shape}")

        logger.info("🔍 Model Output Tensors:")
        for i, quantize_output in enumerate(self.quantize_model[0].outputs):
            logger.info(f"  output[{i}]: {quantize_output.name}, {quantize_output.properties.dtype}, {quantize_output.properties.shape}")

        self.model_input_height, self.model_input_width = self.quantize_model[0].inputs[0].properties.shape[2:4]
        logger.info(f"📐 Model input size: {self.model_input_width}×{self.model_input_height}")

    def resizer(self, img: np.ndarray) -> np.ndarray:
        """调整图像尺寸到模型输入大小"""
        img_h, img_w = img.shape[0:2]
        self.y_scale, self.x_scale = img_h/self.model_input_height, img_w/self.model_input_width
        return cv2.resize(img, (self.model_input_width, self.model_input_height), interpolation=cv2.INTER_NEAREST)

    def bgr2nv12(self, bgr_img: np.ndarray) -> np.ndarray:
        """将BGR图像转换为NV12格式"""
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
        return nv12

    def forward(self, input_tensor: np.array) -> list:
        """BPU前向推理"""
        return self.quantize_model[0].forward(input_tensor)

    def c2numpy(self, outputs) -> list:
        """将C++输出转换为numpy数组"""
        return [dnnTensor.buffer for dnnTensor in outputs]

class BicycleViolationDetector(BaseModel):
    def __init__(self, model_file: str, conf: float = 0.6, iou: float = 0.45):
        super().__init__(model_file)
        
        # 检查输出数量
        output_count = len(self.quantize_model[0].outputs)
        logger.info(f"📊 Model has {output_count} outputs")
        
        # 检查模型输出类型
        output_dtypes = [output.properties.dtype for output in self.quantize_model[0].outputs]
        logger.info(f"📊 Output data types: {output_dtypes}")
        
        # 设置量化系数
        if all(dtype == 'float32' for dtype in output_dtypes):
            logger.info("✅ Model outputs float32 (already dequantized)")
            self.s_bboxes_scale = None
            self.m_bboxes_scale = None  
            self.l_bboxes_scale = None
        else:
            try:
                self.s_bboxes_scale = self.quantize_model[0].outputs[1].properties.scale_data[np.newaxis, :]
                self.m_bboxes_scale = self.quantize_model[0].outputs[3].properties.scale_data[np.newaxis, :]
                self.l_bboxes_scale = self.quantize_model[0].outputs[5].properties.scale_data[np.newaxis, :]
                logger.info("✅ Quantization scales loaded")
            except Exception as e:
                logger.warning(f"⚠️ Cannot load quantization scales: {e}")
                self.s_bboxes_scale = None
                self.m_bboxes_scale = None  
                self.l_bboxes_scale = None

        # DFL权重
        self.weights_static = np.array([i for i in range(16)]).astype(np.float32)[np.newaxis, np.newaxis, :]

        # Anchors for different scales
        self.s_anchor = np.stack([np.tile(np.linspace(0.5, 79.5, 80), reps=80), 
                            np.repeat(np.arange(0.5, 80.5, 1), 80)], axis=0).transpose(1,0)
        self.m_anchor = np.stack([np.tile(np.linspace(0.5, 39.5, 40), reps=40), 
                            np.repeat(np.arange(0.5, 40.5, 1), 40)], axis=0).transpose(1,0)
        self.l_anchor = np.stack([np.tile(np.linspace(0.5, 19.5, 20), reps=20), 
                            np.repeat(np.arange(0.5, 20.5, 1), 20)], axis=0).transpose(1,0)

        # 阈值配置
        self.conf = conf
        self.iou = iou
        self.conf_inverse = -np.log(1/conf - 1)
        logger.info(f"⚡ Confidence threshold: {conf:.2f}, IoU threshold: {iou:.2f}")

    def postProcess(self, outputs: list[np.ndarray]) -> tuple[list, list, list]:
        """后处理：解析模型输出并进行NMS"""
        if len(outputs) != 6:
            logger.error(f"❌ Expected 6 outputs, got {len(outputs)}")
            return [], [], []
        
        # 重塑输出
        s_clses = outputs[0].reshape(-1, 1)    # (6400, 1)
        s_bboxes = outputs[1].reshape(-1, 64)  # (6400, 64)
        m_clses = outputs[2].reshape(-1, 1)    # (1600, 1) 
        m_bboxes = outputs[3].reshape(-1, 64)  # (1600, 64)
        l_clses = outputs[4].reshape(-1, 1)    # (400, 1)
        l_bboxes = outputs[5].reshape(-1, 64)  # (400, 64)

        # 分类阈值筛选
        s_valid_indices = np.flatnonzero(s_clses.flatten() >= self.conf_inverse)
        s_ids = np.zeros(len(s_valid_indices), dtype=np.int32)
        s_scores = s_clses.flatten()[s_valid_indices]

        m_valid_indices = np.flatnonzero(m_clses.flatten() >= self.conf_inverse)
        m_ids = np.zeros(len(m_valid_indices), dtype=np.int32)
        m_scores = m_clses.flatten()[m_valid_indices]

        l_valid_indices = np.flatnonzero(l_clses.flatten() >= self.conf_inverse)
        l_ids = np.zeros(len(l_valid_indices), dtype=np.int32)
        l_scores = l_clses.flatten()[l_valid_indices]

        # Sigmoid
        s_scores = 1 / (1 + np.exp(-s_scores))
        m_scores = 1 / (1 + np.exp(-m_scores))
        l_scores = 1 / (1 + np.exp(-l_scores))

        # Bounding Box处理
        s_bboxes_float32 = s_bboxes[s_valid_indices,:]
        m_bboxes_float32 = m_bboxes[m_valid_indices,:]
        l_bboxes_float32 = l_bboxes[l_valid_indices,:]

        # 应用量化系数
        if self.s_bboxes_scale is not None:
            s_bboxes_float32 = s_bboxes_float32.astype(np.float32) * self.s_bboxes_scale
            m_bboxes_float32 = m_bboxes_float32.astype(np.float32) * self.m_bboxes_scale
            l_bboxes_float32 = l_bboxes_float32.astype(np.float32) * self.l_bboxes_scale

        # dist2bbox处理
        s_dbboxes = self._dist2bbox(s_bboxes_float32, self.s_anchor, s_valid_indices, 8)
        m_dbboxes = self._dist2bbox(m_bboxes_float32, self.m_anchor, m_valid_indices, 16)
        l_dbboxes = self._dist2bbox(l_bboxes_float32, self.l_anchor, l_valid_indices, 32)

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
                    return ids[indices], scores[indices], bboxes
        
        return [], [], []

    def _dist2bbox(self, bboxes_data, anchor, valid_indices, stride):
        """将距离预测转换为边界框坐标"""
        if len(valid_indices) > 0:
            ltrb_indices = np.sum(softmax(bboxes_data.reshape(-1, 4, 16), axis=2) * self.weights_static, axis=2)
            anchor_indices = anchor[valid_indices, :]
            x1y1 = anchor_indices - ltrb_indices[:, 0:2]
            x2y2 = anchor_indices + ltrb_indices[:, 2:4]
            return np.hstack([x1y1, x2y2]) * stride
        else:
            return np.empty((0, 4))

    def detect_frame(self, frame):
        """检测单帧图像"""
        # 预处理
        input_tensor = self.bgr2nv12(frame)
        
        # 推理
        outputs = self.forward(input_tensor)
        outputs = self.c2numpy(outputs)
        
        # 后处理
        ids, scores, bboxes = self.postProcess(outputs)
        
        return ids, scores, bboxes

def draw_detection(img: np.ndarray, 
                   bbox: tuple[int, int, int, int],
                   score: float, 
                   class_id: int) -> None:
    """绘制检测结果"""
    x1, y1, x2, y2 = bbox
    color = (0, 0, 255)  # 红色
    
    # 绘制检测框
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
    
    # 绘制标签
    label = f"Illegal Parking {score:.2f}"
    (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    
    # 标签背景
    cv2.rectangle(img, 
                  (x1, y1 - label_height - 10), 
                  (x1 + label_width, y1), 
                  color, -1)
    
    # 标签文字
    cv2.putText(img, label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

def add_info_overlay(frame, frame_count, fps, detections, total_detections):
    """添加信息覆盖层"""
    info_bg_color = (0, 0, 0)
    info_text_color = (255, 255, 255)
    
    # 绘制信息背景
    cv2.rectangle(frame, (5, 5), (350, 120), info_bg_color, -1)
    
    # 信息文本
    fps_text = f"FPS: {fps:.1f}"
    frame_text = f"Frame: {frame_count}"
    detection_text = f"Current Detections: {detections}"
    total_text = f"Total Detections: {total_detections}"
    time_text = f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}"
    
    # 绘制文本
    y_offset = 22
    for text in [fps_text, frame_text, detection_text, total_text, time_text]:
        cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, info_text_color, 1)
        y_offset += 18

def real_time_video_detection(model_path, video_source=0, show_video=True, save_images=False, output_dir="detection_results"):
    """实时视频检测主函数"""
    
    # 初始化检测器
    logger.info("🚀 Loading BPU model...")
    detector = BicycleViolationDetector(model_path)
    logger.info("✅ Model loaded successfully")
    
    # 创建输出目录
    if save_images and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"📁 Created output directory: {output_dir}")
    
    # 打开视频源
    if isinstance(video_source, str) and os.path.isfile(video_source):
        cap = cv2.VideoCapture(video_source)
        logger.info(f"📹 Opening video file: {video_source}")
    else:
        cap = cv2.VideoCapture(int(video_source))
        logger.info(f"📹 Opening camera: {video_source}")
    
    if not cap.isOpened():
        logger.error(f"❌ Cannot open video source: {video_source}")
        return
    
    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"📐 Video: {width}×{height}, {fps:.1f}FPS")
    
    if show_video:
        cv2.namedWindow('RDK Smart Parking Violation Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('RDK Smart Parking Violation Detection', 1200, 800)
        logger.info("🎬 Press 'q' to quit, 'space' to pause/resume, 's' to save current frame")
    
    # 统计变量
    frame_count = 0
    total_detections = 0
    paused = False
    fps_counter = 0
    fps_timer = time.time()
    current_fps = 0
    
    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    logger.info("📽️ Video processing completed")
                    break
                
                frame_count += 1
                start_time = time.time()
                
                # 检测
                ids, scores, bboxes = detector.detect_frame(frame)
                
                inference_time = time.time() - start_time
                current_detections = len(ids)
                total_detections += current_detections
                
                # 绘制检测结果
                for i, (class_id, score, bbox) in enumerate(zip(ids, scores, bboxes)):
                    draw_detection(frame, bbox, score, class_id)
                    x1, y1, x2, y2 = bbox
                    logger.info(f"🚲 Frame {frame_count}: Detection {i+1}, confidence={score:.3f}, bbox=({x1},{y1},{x2},{y2})")
                
                # 计算FPS
                fps_counter += 1
                if time.time() - fps_timer >= 1.0:
                    current_fps = fps_counter / (time.time() - fps_timer)
                    fps_counter = 0
                    fps_timer = time.time()
                
                # 添加信息覆盖层
                add_info_overlay(frame, frame_count, current_fps, current_detections, total_detections)
                
                # 保存检测图片
                if save_images and current_detections > 0:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"detection_frame_{frame_count:06d}_{timestamp}.jpg"
                    output_path = os.path.join(output_dir, filename)
                    cv2.imwrite(output_path, frame)
                    logger.info(f" Saved: {filename}")
                
                # 输出检测统计
                if current_detections > 0:
                    logger.info(f" Frame {frame_count}: {current_detections} violations detected, inference: {inference_time*1000:.1f}ms")
            
            # 显示视频
            if show_video:
                cv2.imshow('RDK Smart Parking Violation Detection', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info(" User quit detection")
                    break
                elif key == ord(' '):
                    paused = not paused
                    logger.info(f"⏸ {'Paused' if paused else 'Resumed'}")
                elif key == ord('s') and not paused:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"manual_save_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    logger.info(f"📸 Manual save: {filename}")
            else:
                time.sleep(0.01)
    
    except KeyboardInterrupt:
        logger.info(" Detection interrupted")
    
    finally:
        cap.release()
        if show_video:
            cv2.destroyAllWindows()
        
        # 最终统计
        logger.info("="*60)
        logger.info(" Detection Statistics:")
        logger.info(f"   Total frames processed: {frame_count}")
        logger.info(f"   Total detections: {total_detections}")
        if frame_count > 0:
            logger.info(f"   Average detection rate: {total_detections/frame_count:.3f} per frame")
        if save_images:
            logger.info(f"   Images saved to: {output_dir}")
        logger.info(" Detection completed")

def main():
    parser = argparse.ArgumentParser(description='RDK X5 Real-time Video Detection')
    parser.add_argument('--model-path', type=str, default='bicycle_violation_640x640_nv12.bin',
                        help='Path to BPU quantized model (.bin)')
    parser.add_argument('--video-source', type=str, default='0',
                        help='Video source: camera index (0,1,2...) or video file path')
    parser.add_argument('--conf-thres', type=float, default=0.6,
                        help='Confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45,
                        help='IoU threshold for NMS')
    parser.add_argument('--no-display', action='store_true',
                        help='Disable video display (headless mode)')
    parser.add_argument('--save-images', action='store_true',
                        help='Save detection result images')
    parser.add_argument('--output-dir', type=str, default='detection_results',
                        help='Output directory for saved images')
    
    args = parser.parse_args()
    
    logger.info(" RDK X5 Smart Parking Violation Detection System")
    logger.info("="*50)
    logger.info(f" Model: {args.model_path}")
    logger.info(f" Video source: {args.video_source}")
    logger.info(f" Confidence: {args.conf_thres}, IoU: {args.iou_thres}")
    logger.info(f" Display: {'No' if args.no_display else 'Yes'}")
    logger.info(f" Save images: {'Yes' if args.save_images else 'No'}")
    
    # 处理视频源参数
    video_source = args.video_source
    if video_source.isdigit():
        video_source = int(video_source)
    
    # 开始检测
    real_time_video_detection(
        model_path=args.model_path,
        video_source=video_source,
        show_video=not args.no_display,
        save_images=args.save_images,
        output_dir=args.output_dir
    )

if __name__ == "__main__":
    main() 