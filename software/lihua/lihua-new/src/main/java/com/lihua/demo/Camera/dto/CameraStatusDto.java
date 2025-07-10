package com.lihua.demo.Camera.dto;

/**
 * 摄像头状态DTO
 * @author lihua
 */
public class CameraStatusDto {
    
    /**
     * 是否连接
     */
    private Boolean isConnected;
    
    /**
     * 连接状态描述
     */
    private String connectionStatus;
    
    /**
     * 摄像头信息
     */
    private CameraInfoDto cameraInfo;
    
    /**
     * 视频流URL
     */
    private String streamUrl;

    public CameraStatusDto() {}

    public CameraStatusDto(Boolean isConnected, String connectionStatus, 
                          CameraInfoDto cameraInfo, String streamUrl) {
        this.isConnected = isConnected;
        this.connectionStatus = connectionStatus;
        this.cameraInfo = cameraInfo;
        this.streamUrl = streamUrl;
    }

    public Boolean getIsConnected() {
        return isConnected;
    }

    public void setIsConnected(Boolean isConnected) {
        this.isConnected = isConnected;
    }

    public String getConnectionStatus() {
        return connectionStatus;
    }

    public void setConnectionStatus(String connectionStatus) {
        this.connectionStatus = connectionStatus;
    }

    public CameraInfoDto getCameraInfo() {
        return cameraInfo;
    }

    public void setCameraInfo(CameraInfoDto cameraInfo) {
        this.cameraInfo = cameraInfo;
    }

    public String getStreamUrl() {
        return streamUrl;
    }

    public void setStreamUrl(String streamUrl) {
        this.streamUrl = streamUrl;
    }

    @Override
    public String toString() {
        return "CameraStatusDto{" +
                "isConnected=" + isConnected +
                ", connectionStatus='" + connectionStatus + '\'' +
                ", cameraInfo=" + cameraInfo +
                ", streamUrl='" + streamUrl + '\'' +
                '}';
    }
} 