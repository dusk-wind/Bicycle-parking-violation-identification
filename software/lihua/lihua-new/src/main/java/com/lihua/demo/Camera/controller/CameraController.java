package com.lihua.demo.Camera.controller;

import com.lihua.demo.Camera.dto.CameraStatusDto;
import com.lihua.demo.Camera.entity.Camera;
import com.lihua.demo.Camera.service.CameraService;
import com.lihua.demo.common.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 摄像头控制器
 * @author lihua
 */
@RestController
@RequestMapping("/api/camera")
@CrossOrigin(origins = "*")
public class CameraController {

    @Autowired
    private CameraService cameraService;

    /**
     * 获取摄像头状态
     */
    @GetMapping("/status")
    public Result<CameraStatusDto> getCameraStatus() {
        try {
            CameraStatusDto status = cameraService.getCameraStatus();
            return Result.success(status);
        } catch (Exception e) {
            return Result.error("获取摄像头状态失败：" + e.getMessage());
        }
    }

    /**
     * 切换摄像头连接状态
     */
    @PostMapping("/toggle")
    public Result<Map<String, Object>> toggleCameraStatus(@RequestBody Map<String, Boolean> request) {
        try {
            Boolean connect = request.get("connect");
            if (connect == null) {
                return Result.error("参数错误");
            }
            
            CameraStatusDto status = cameraService.toggleCameraStatus(connect);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", connect ? "摄像头连接成功" : "摄像头断开成功");
            response.put("status", status);
            
            return Result.success(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "操作失败：" + e.getMessage());
            return Result.success(response);
        }
    }

    /**
     * 获取所有摄像头列表
     */
    @GetMapping("/list")
    public Result<List<Camera>> getAllCameras() {
        try {
            List<Camera> cameras = cameraService.getAllCameras();
            return Result.success(cameras);
        } catch (Exception e) {
            return Result.error("获取摄像头列表失败：" + e.getMessage());
        }
    }

    /**
     * 根据ID获取摄像头
     */
    @GetMapping("/{id}")
    public Result<Camera> getCameraById(@PathVariable Long id) {
        try {
            Camera camera = cameraService.getCameraById(id);
            if (camera == null) {
                return Result.error(404, "摄像头不存在");
            }
            return Result.success(camera);
        } catch (Exception e) {
            return Result.error("获取摄像头信息失败：" + e.getMessage());
        }
    }

    /**
     * 添加摄像头
     */
    @PostMapping("/add")
    public Result<String> addCamera(@RequestBody Camera camera) {
        try {
            boolean success = cameraService.addCamera(camera);
            if (success) {
                return Result.success("添加成功");
            } else {
                return Result.error("添加失败");
            }
        } catch (Exception e) {
            return Result.error("添加摄像头失败：" + e.getMessage());
        }
    }

    /**
     * 更新摄像头信息
     */
    @PutMapping("/update")
    public Result<String> updateCamera(@RequestBody Camera camera) {
        try {
            boolean success = cameraService.updateCamera(camera);
            if (success) {
                return Result.success("更新成功");
            } else {
                return Result.error("更新失败");
            }
        } catch (Exception e) {
            return Result.error("更新摄像头失败：" + e.getMessage());
        }
    }

    /**
     * 删除摄像头
     */
    @DeleteMapping("/{id}")
    public Result<String> deleteCamera(@PathVariable Long id) {
        try {
            boolean success = cameraService.deleteCamera(id);
            if (success) {
                return Result.success("删除成功");
            } else {
                return Result.error("删除失败");
            }
        } catch (Exception e) {
            return Result.error("删除摄像头失败：" + e.getMessage());
        }
    }

    /**
     * 获取摄像头统计信息
     */
    @GetMapping("/stats")
    public Result<Map<String, Object>> getCameraStats() {
        try {
            Map<String, Object> stats = new HashMap<>();
            stats.put("total", cameraService.getTotalCameras());
            stats.put("online", cameraService.getOnlineCameras());
            stats.put("offline", cameraService.getOfflineCameras());
            return Result.success(stats);
        } catch (Exception e) {
            return Result.error("获取统计信息失败：" + e.getMessage());
        }
    }

    /**
     * 模拟视频流接口
     */
    @GetMapping("/stream/{id}")
    public Result<String> getCameraStream(@PathVariable Long id) {
        try {
            // 这里应该返回实际的视频流
            // 目前返回模拟的流地址
            String streamUrl = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...";
            return Result.success(streamUrl);
        } catch (Exception e) {
            return Result.error("获取视频流失败：" + e.getMessage());
        }
    }
} 