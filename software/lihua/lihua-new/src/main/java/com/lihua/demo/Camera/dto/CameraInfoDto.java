package com.lihua.demo.Camera.dto;

/**
 * 摄像头信息DTO
 * @author lihua
 */
public class CameraInfoDto {
    
    /**
     * 设备序列号
     */
    private String serial;
    
    /**
     * 接口类型
     */
    private String interfaceType;
    
    /**
     * 最后更新时间
     */
    private String lastUpdated;

    public CameraInfoDto() {}

    public CameraInfoDto(String serial, String interfaceType, String lastUpdated) {
        this.serial = serial;
        this.interfaceType = interfaceType;
        this.lastUpdated = lastUpdated;
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

    public String getLastUpdated() {
        return lastUpdated;
    }

    public void setLastUpdated(String lastUpdated) {
        this.lastUpdated = lastUpdated;
    }

    @Override
    public String toString() {
        return "CameraInfoDto{" +
                "serial='" + serial + '\'' +
                ", interfaceType='" + interfaceType + '\'' +
                ", lastUpdated='" + lastUpdated + '\'' +
                '}';
    }
} 