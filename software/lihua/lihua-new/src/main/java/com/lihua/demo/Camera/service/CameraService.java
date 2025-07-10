package com.lihua.demo.Camera.service;

import com.lihua.demo.Camera.dto.CameraStatusDto;
import com.lihua.demo.Camera.entity.Camera;

import java.util.List;

/**
 * 摄像头服务接口
 * @author lihua
 */
public interface CameraService {
    
    /**
     * 获取摄像头状态信息
     * @return 摄像头状态
     */
    CameraStatusDto getCameraStatus();
    
    /**
     * 切换摄像头连接状态
     * @param connect true-连接，false-断开
     * @return 操作结果
     */
    CameraStatusDto toggleCameraStatus(boolean connect);
    
    /**
     * 获取所有摄像头列表
     * @return 摄像头列表
     */
    List<Camera> getAllCameras();
    
    /**
     * 根据ID获取摄像头
     * @param id 摄像头ID
     * @return 摄像头信息
     */
    Camera getCameraById(Long id);
    
    /**
     * 统计摄像头总数
     * @return 总数
     */
    Long getTotalCameras();
    
    /**
     * 统计在线摄像头数
     * @return 在线数量
     */
    Long getOnlineCameras();
    
    /**
     * 统计离线摄像头数
     * @return 离线数量
     */
    Long getOfflineCameras();
    
    /**
     * 添加摄像头
     * @param camera 摄像头信息
     * @return 是否成功
     */
    boolean addCamera(Camera camera);
    
    /**
     * 更新摄像头信息
     * @param camera 摄像头信息
     * @return 是否成功
     */
    boolean updateCamera(Camera camera);
    
    /**
     * 删除摄像头
     * @param id 摄像头ID
     * @return 是否成功
     */
    boolean deleteCamera(Long id);
} 