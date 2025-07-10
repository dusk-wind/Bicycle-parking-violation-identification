package com.lihua.demo.dto;

/**
 * 周趋势数据DTO
 * @author lihua
 */
public class WeeklyTrendDto {
    
    /**
     * 周次
     */
    private String week;
    
    /**
     * 违规数量
     */
    private Long violationCount;
    
    /**
     * 日期范围
     */
    private String dateRange;

    public WeeklyTrendDto() {}

    public WeeklyTrendDto(String week, Long violationCount, String dateRange) {
        this.week = week;
        this.violationCount = violationCount;
        this.dateRange = dateRange;
    }

    public String getWeek() {
        return week;
    }

    public void setWeek(String week) {
        this.week = week;
    }

    public Long getViolationCount() {
        return violationCount;
    }

    public void setViolationCount(Long violationCount) {
        this.violationCount = violationCount;
    }

    public String getDateRange() {
        return dateRange;
    }

    public void setDateRange(String dateRange) {
        this.dateRange = dateRange;
    }

    @Override
    public String toString() {
        return "WeeklyTrendDto{" +
                "week='" + week + '\'' +
                ", violationCount=" + violationCount +
                ", dateRange='" + dateRange + '\'' +
                '}';
    }
} 