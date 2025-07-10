package com.lihua.demo.dto;

import java.math.BigDecimal;

/**
 * 统计数据DTO
 * @author lihua
 */
public class StatisticsData {
    
    /**
     * 总记录数
     */
    private Long totalRecords;
    
    /**
     * 今日记录数
     */
    private Long todayRecords;
    
    /**
     * 平均置信度
     */
    private BigDecimal avgConfidence;
    
    /**
     * 总摄像头数
     */
    private Long totalCameras;
    
    /**
     * 在线摄像头数
     */
    private Long onlineCameras;
    
    /**
     * 离线摄像头数
     */
    private Long offlineCameras;

    public StatisticsData() {}

    public StatisticsData(Long totalRecords, Long todayRecords, BigDecimal avgConfidence, 
                         Long totalCameras, Long onlineCameras, Long offlineCameras) {
        this.totalRecords = totalRecords;
        this.todayRecords = todayRecords;
        this.avgConfidence = avgConfidence;
        this.totalCameras = totalCameras;
        this.onlineCameras = onlineCameras;
        this.offlineCameras = offlineCameras;
    }

    public Long getTotalRecords() {
        return totalRecords;
    }

    public void setTotalRecords(Long totalRecords) {
        this.totalRecords = totalRecords;
    }

    public Long getTodayRecords() {
        return todayRecords;
    }

    public void setTodayRecords(Long todayRecords) {
        this.todayRecords = todayRecords;
    }

    public BigDecimal getAvgConfidence() {
        return avgConfidence;
    }

    public void setAvgConfidence(BigDecimal avgConfidence) {
        this.avgConfidence = avgConfidence;
    }

    public Long getTotalCameras() {
        return totalCameras;
    }

    public void setTotalCameras(Long totalCameras) {
        this.totalCameras = totalCameras;
    }

    public Long getOnlineCameras() {
        return onlineCameras;
    }

    public void setOnlineCameras(Long onlineCameras) {
        this.onlineCameras = onlineCameras;
    }

    public Long getOfflineCameras() {
        return offlineCameras;
    }

    public void setOfflineCameras(Long offlineCameras) {
        this.offlineCameras = offlineCameras;
    }

    @Override
    public String toString() {
        return "StatisticsData{" +
                "totalRecords=" + totalRecords +
                ", todayRecords=" + todayRecords +
                ", avgConfidence=" + avgConfidence +
                ", totalCameras=" + totalCameras +
                ", onlineCameras=" + onlineCameras +
                ", offlineCameras=" + offlineCameras +
                '}';
    }
} 