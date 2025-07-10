import cv2
import time
import numpy as np
from ultralytics import YOLO
import os

def real_time_detection(show_video=True, save_images=True):
    """
    实时检测视频并显示结果，可选择保存结果图片
    Args:
        show_video: 是否实时显示视频
        save_images: 是否保存检测结果图片
    """
    # 文件路径
    model_path = r"C:\Users\Acer\Desktop\software\model_online\best_bicycle_violation.pt"
    video_path = r"C:\Users\Acer\Desktop\software\model_online\test.mp4"
    output_dir = r"C:\Users\Acer\Desktop\software\model_online\detection_results"
    
    # 创建输出目录
    if save_images and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")
    
    # 检查文件是否存在
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return
    
    print("🚀 Loading YOLOv8 model...")
    try:
        model = YOLO(model_path)
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return
    
    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open video: {video_path}")
        return
    
    # 获取视频信息
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"\n📹 Video info: {width}x{height}, {fps}FPS, {total_frames} frames")
    if show_video:
        print("🎬 Starting real-time detection... (Press 'q' to quit, 'space' to pause/resume)")
    else:
        print("🎬 Starting detection... (Results will be saved as images)")
    if save_images:
        print(f"📁 Output directory: {output_dir}")
    print("-" * 60)
    
    # 统计变量
    frame_count = 0
    total_detections = 0
    confidence_threshold = 0.6
    save_interval = 30  # 每30帧保存一张检测图片
    paused = False
    
    # 创建窗口（如果需要显示）
    if show_video:
        cv2.namedWindow('Smart Campus Parking Violation Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Smart Campus Parking Violation Detection', 1200, 800)
    
    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print("📽️ Video processing completed")
                    break
                
                frame_count += 1
                
                # 开始检测
                start_time = time.time()
                results = model(frame, conf=confidence_threshold, verbose=False)
                inference_time = time.time() - start_time
                
                # 复制帧用于绘制
                display_frame = frame.copy()
                
                # 处理检测结果
                current_detections = 0
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            # 获取检测信息
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = box.conf[0].cpu().numpy()
                            
                            if confidence >= confidence_threshold:
                                current_detections += 1
                                total_detections += 1
                                
                                # 绘制检测框（更加醒目的样式）
                                cv2.rectangle(display_frame, 
                                            (int(x1), int(y1)), (int(x2), int(y2)), 
                                            (0, 0, 255), 3)  # 红色框
                                
                                # 绘制背景框用于文字
                                label = f"Illegal Parking {confidence:.2f}"
                                (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                                cv2.rectangle(display_frame, 
                                            (int(x1), int(y1) - label_height - 10), 
                                            (int(x1) + label_width, int(y1)), 
                                            (0, 0, 255), -1)  # 红色背景
                                
                                # 绘制白色标签文字
                                cv2.putText(display_frame, label,
                                          (int(x1), int(y1) - 5),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                                
                                # 控制台输出检测结果
                                print(f"🚲 Frame {frame_count}: Illegal parking detected, confidence={confidence:.3f}, position=({int(x1)},{int(y1)})-({int(x2)},{int(y2)})")
                
                # 添加实时信息到图片
                info_bg_color = (0, 0, 0)  # 黑色背景
                info_text_color = (255, 255, 255)  # 白色文字
                
                # 绘制信息背景（更小的尺寸）
                cv2.rectangle(display_frame, (5, 5), (280, 110), info_bg_color, -1)
                
                fps_text = f"FPS: {1/inference_time:.1f}"
                frame_text = f"Frame: {frame_count}/{total_frames}"
                detection_text = f"Current: {current_detections}"
                total_text = f"Total: {total_detections}"
                progress_text = f"Progress: {(frame_count/total_frames)*100:.1f}%"
                
                # 使用更小的字体和更紧密的行间距
                cv2.putText(display_frame, fps_text, (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, info_text_color, 1)
                cv2.putText(display_frame, frame_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, info_text_color, 1)
                cv2.putText(display_frame, detection_text, (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.5, info_text_color, 1)
                cv2.putText(display_frame, total_text, (10, 76), cv2.FONT_HERSHEY_SIMPLEX, 0.5, info_text_color, 1)
                cv2.putText(display_frame, progress_text, (10, 94), cv2.FONT_HERSHEY_SIMPLEX, 0.5, info_text_color, 1)
                
                # 保存检测结果图片（每隔一定帧数或有检测时保存）
                if save_images and (current_detections > 0 or frame_count % save_interval == 0):
                    output_path = os.path.join(output_dir, f"frame_{frame_count:06d}_detected_{current_detections}.jpg")
                    cv2.imwrite(output_path, display_frame)
                    if current_detections > 0:
                        print(f"💾 Saved detection image: frame_{frame_count:06d}_detected_{current_detections}.jpg")
                
                # 控制台输出进度（每60帧输出一次）
                if frame_count % 60 == 0:
                    progress = (frame_count / total_frames) * 100
                    avg_fps = 1 / inference_time
                    print(f"📊 Progress: {progress:.1f}% | Avg FPS: {avg_fps:.1f} | Total detections: {total_detections}")
            
            # 显示视频（如果启用）
            if show_video:
                cv2.imshow('Smart Campus Parking Violation Detection', display_frame)
                
                # 键盘控制
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):  # 按'q'退出
                    print("\n⏹️ User quit detection")
                    break
                elif key == ord(' '):  # 按空格暂停/继续
                    paused = not paused
                    print(f"⏸️ {'Paused' if paused else 'Resumed'} playback")
            else:
                # 如果不显示视频，稍微延迟避免CPU占用过高
                time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n⏹️ Detection interrupted")
    
    finally:
        # 释放资源
        cap.release()
        if show_video:
            cv2.destroyAllWindows()
        
        # 最终统计
        print("\n" + "="*60)
        print("📈 Detection Statistics Report:")
        print(f"   Total frames processed: {frame_count}")
        print(f"   Total detections: {total_detections}")
        if frame_count > 0:
            print(f"   Average detection rate: {total_detections/frame_count:.2f} per frame")
        print(f"   Video completion: {frame_count/total_frames*100:.1f}%")
        if save_images:
            print(f"   Detection images saved to: {output_dir}")
        print("✅ Detection completed")
        
        # 列出保存的图片（如果启用保存）
        if save_images and os.path.exists(output_dir):
            saved_images = [f for f in os.listdir(output_dir) if f.endswith('.jpg')]
            print(f"📸 Total {len(saved_images)} detection images saved")

def main():
    print("🚲 Smart Campus Parking Violation Detection System")
    print("=" * 50)
    print("Choose running mode:")
    print("1. Real-time display + Save images (Recommended)")
    print("2. Real-time display only")
    print("3. Save images only")
    
    try:
        choice = input("Please enter your choice (1-3, default 1): ").strip()
        if choice == "2":
            real_time_detection(show_video=True, save_images=False)
        elif choice == "3":
            real_time_detection(show_video=False, save_images=True)
        else:  # 默认选择1
            real_time_detection(show_video=True, save_images=True)
    except KeyboardInterrupt:
        print("\n👋 Program exited")

if __name__ == "__main__":
    main()
