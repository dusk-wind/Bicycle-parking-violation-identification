package com.lihua.demo.Camera.entity;

import com.fasterxml.jackson.annotation.JsonFormat;

import java.time.LocalDateTime;

/**
 * 摄像头实体类
 * @author lihua
 */
public class Camera {
    
    /**
     * 摄像头主键ID
     */
    private Long id;
    
    /**
     * 设备序列号
     */
    private String serial;
    
    /**
     * 接口类型
     */
    private String interfaceType;
    
    /**
     * 是否连接
     */
    private Boolean connected;
    
    /**
     * 最后更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime lastUpdated;

    public Camera() {}

    public Camera(Long id, String serial, String interfaceType, Boolean connected, LocalDateTime lastUpdated) {
        this.id = id;
        this.serial = serial;
        this.interfaceType = interfaceType;
        this.connected = connected;
        this.lastUpdated = lastUpdated;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getSerial() {
        return serial;
    }

    public void setSerial(String serial) {
        this.serial = serial;
    }

    public String getInterfaceType() {
        return interfaceType;
    }

    public void setInterfaceType(String interfaceType) {
        this.interfaceType = interfaceType;
    }

    public Boolean getConnected() {
        return connected;
    }

    public void setConnected(Boolean connected) {
        this.connected = connected;
    }

    public LocalDateTime getLastUpdated() {
        return lastUpdated;
    }

    public void setLastUpdated(LocalDateTime lastUpdated) {
        this.lastUpdated = lastUpdated;
    }

    @Override
    public String toString() {
        return "Camera{" +
                "id=" + id +
                ", serial='" + serial + '\'' +
                ", interfaceType='" + interfaceType + '\'' +
                ", connected=" + connected +
                ", lastUpdated=" + lastUpdated +
                '}';
    }
} 