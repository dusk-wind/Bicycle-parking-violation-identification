package com.lihua.demo.Camera.service.impl;

import com.lihua.demo.Camera.dto.CameraInfoDto;
import com.lihua.demo.Camera.dto.CameraStatusDto;
import com.lihua.demo.Camera.entity.Camera;
import com.lihua.demo.Camera.mapper.CameraMapper;
import com.lihua.demo.Camera.service.CameraService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

/**
 * 摄像头服务实现类
 * @author lihua
 */
@Service
public class CameraServiceImpl implements CameraService {

    @Autowired
    private CameraMapper cameraMapper;

    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    @Override
    public CameraStatusDto getCameraStatus() {
        // 获取第一个摄像头作为主摄像头
        List<Camera> cameras = cameraMapper.selectAll();
        Camera camera = cameras.isEmpty() ? getDefaultCamera() : cameras.get(0);
        
        boolean isConnected = camera.getConnected() != null ? camera.getConnected() : false;
        String connectionStatus = isConnected ? "已连接" : "未连接";
        
        CameraInfoDto cameraInfo = new CameraInfoDto(
            camera.getSerial(),
            camera.getInterfaceType(),
            camera.getLastUpdated() != null ? camera.getLastUpdated().format(formatter) : ""
        );
        
        String streamUrl = isConnected ? generateStreamUrl(camera.getId()) : null;
        
        return new CameraStatusDto(isConnected, connectionStatus, cameraInfo, streamUrl);
    }

    @Override
    public CameraStatusDto toggleCameraStatus(boolean connect) {
        List<Camera> cameras = cameraMapper.selectAll();
        Camera camera = cameras.isEmpty() ? createDefaultCamera() : cameras.get(0);
        
        // 更新连接状态
        cameraMapper.updateConnectedStatus(camera.getId(), connect);
        
        // 返回更新后的状态
        return getCameraStatus();
    }

    @Override
    public List<Camera> getAllCameras() {
        return cameraMapper.selectAll();
    }

    @Override
    public Camera getCameraById(Long id) {
        return cameraMapper.selectById(id);
    }

    @Override
    public Long getTotalCameras() {
        return cameraMapper.countTotal();
    }

    @Override
    public Long getOnlineCameras() {
        return cameraMapper.countByConnected(true);
    }

    @Override
    public Long getOfflineCameras() {
        return cameraMapper.countByConnected(false);
    }

    @Override
    public boolean addCamera(Camera camera) {
        return cameraMapper.insert(camera) > 0;
    }

    @Override
    public boolean updateCamera(Camera camera) {
        return cameraMapper.update(camera) > 0;
    }

    @Override
    public boolean deleteCamera(Long id) {
        return cameraMapper.deleteById(id) > 0;
    }

    /**
     * 获取默认摄像头信息
     */
    private Camera getDefaultCamera() {
        Camera camera = new Camera();
        camera.setId(1L);
        camera.setSerial("CAM-001");
        camera.setInterfaceType("USB");
        camera.setConnected(false);
        camera.setLastUpdated(LocalDateTime.now());
        return camera;
    }

    /**
     * 创建默认摄像头
     */
    private Camera createDefaultCamera() {
        Camera camera = getDefaultCamera();
        cameraMapper.insert(camera);
        return camera;
    }

    /**
     * 生成视频流URL
     */
    private String generateStreamUrl(Long cameraId) {
        // 这里可以根据实际情况生成真实的视频流URL
        // 目前返回模拟的URL
        return "http://localhost:8080/api/camera/stream/" + cameraId;
    }
} 