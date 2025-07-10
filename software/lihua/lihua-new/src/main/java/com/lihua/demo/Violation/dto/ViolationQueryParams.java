package com.lihua.demo.Violation.dto;

/**
 * 违停记录查询参数DTO
 * @author lihua
 */
public class ViolationQueryParams {
    
    /**
     * 页码，默认第1页
     */
    private Integer pageNum = 1;
    
    /**
     * 每页条数，默认10条
     */
    private Integer pageSize = 10;
    
    /**
     * 位置信息（模糊查询）
     */
    private String location;
    
    /**
     * 开始日期
     */
    private String startDate;
    
    /**
     * 结束日期
     */
    private String endDate;
    
    /**
     * 摄像头ID
     */
    private Long cameraId;

    public ViolationQueryParams() {}

    public Integer getPageNum() {
        return pageNum;
    }

    public void setPageNum(Integer pageNum) {
        this.pageNum = pageNum;
    }

    public Integer getPageSize() {
        return pageSize;
    }

    public void setPageSize(Integer pageSize) {
        this.pageSize = pageSize;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public String getEndDate() {
        return endDate;
    }

    public void setEndDate(String endDate) {
        this.endDate = endDate;
    }

    public Long getCameraId() {
        return cameraId;
    }

    public void setCameraId(Long cameraId) {
        this.cameraId = cameraId;
    }

    @Override
    public String toString() {
        return "ViolationQueryParams{" +
                "pageNum=" + pageNum +
                ", pageSize=" + pageSize +
                ", location='" + location + '\'' +
                ", startDate='" + startDate + '\'' +
                ", endDate='" + endDate + '\'' +
                ", cameraId=" + cameraId +
                '}';
    }
} 