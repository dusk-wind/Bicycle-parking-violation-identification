package com.lihua.demo.Violation.entity;

import com.fasterxml.jackson.annotation.JsonFormat;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 违停记录实体类
 * @author lihua
 */
public class ViolationRecord {
    
    /**
     * 违停记录主键ID
     */
    private Long id;
    
    /**
     * 摄像头ID（外键）
     */
    private Long cameraId;
    
    /**
     * 识别截图路径
     */
    private String imagePath;
    
    /**
     * 识别记录上传时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime uploadTime;
    
    /**
     * 模型识别置信度
     */
    private BigDecimal confidence;
    
    /**
     * 识别位置
     */
    private String location;

    public ViolationRecord() {}

    public ViolationRecord(Long id, Long cameraId, String imagePath, LocalDateTime uploadTime, 
                          BigDecimal confidence, String location) {
        this.id = id;
        this.cameraId = cameraId;
        this.imagePath = imagePath;
        this.uploadTime = uploadTime;
        this.confidence = confidence;
        this.location = location;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getCameraId() {
        return cameraId;
    }

    public void setCameraId(Long cameraId) {
        this.cameraId = cameraId;
    }

    public String getImagePath() {
        return imagePath;
    }

    public void setImagePath(String imagePath) {
        this.imagePath = imagePath;
    }

    public LocalDateTime getUploadTime() {
        return uploadTime;
    }

    public void setUploadTime(LocalDateTime uploadTime) {
        this.uploadTime = uploadTime;
    }

    public BigDecimal getConfidence() {
        return confidence;
    }

    public void setConfidence(BigDecimal confidence) {
        this.confidence = confidence;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    @Override
    public String toString() {
        return "ViolationRecord{" +
                "id=" + id +
                ", cameraId=" + cameraId +
                ", imagePath='" + imagePath + '\'' +
                ", uploadTime=" + uploadTime +
                ", confidence=" + confidence +
                ", location='" + location + '\'' +
                '}';
    }
} 