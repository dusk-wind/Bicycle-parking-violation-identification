package com.lihua.demo.Violation.service;

import com.lihua.demo.Violation.dto.ViolationQueryParams;
import com.lihua.demo.Violation.entity.ViolationRecord;
import com.lihua.demo.common.PageResult;
import com.lihua.demo.dto.StatisticsData;
import com.lihua.demo.dto.WeeklyTrendDto;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * 违停记录服务接口
 * @author lihua
 */
public interface ViolationRecordService {
    
    /**
     * 分页查询违停记录
     * @param params 查询参数
     * @return 分页结果
     */
    PageResult<ViolationRecord> getViolationRecords(ViolationQueryParams params);
    
    /**
     * 根据ID获取违停记录详情
     * @param id 记录ID
     * @return 违停记录
     */
    ViolationRecord getViolationById(Long id);
    
    /**
     * 获取统计数据
     * @return 统计数据
     */
    StatisticsData getStatistics();
    
    /**
     * 获取最新记录
     * @param limit 限制数量
     * @return 最新记录列表
     */
    List<ViolationRecord> getLatestRecords(Integer limit);
    
    /**
     * 添加违停记录
     * @param record 违停记录
     * @return 是否成功
     */
    boolean addViolationRecord(ViolationRecord record);
    
    /**
     * 更新违停记录
     * @param record 违停记录
     * @return 是否成功
     */
    boolean updateViolationRecord(ViolationRecord record);
    
    /**
     * 删除违停记录
     * @param id 记录ID
     * @return 是否成功
     */
    boolean deleteViolationRecord(Long id);
    
    /**
     * 获取周趋势数据
     * @return 周趋势数据
     */
    List<WeeklyTrendDto> getWeeklyTrend();
    
    /**
     * 获取类型分布数据
     * @return 类型分布数据
     */
    List<Map<String, Object>> getTypeDistribution();
    
    /**
     * 获取地点分布数据
     * @return 地点分布数据
     */
    List<Map<String, Object>> getLocationDistribution();
    
    /**
     * 获取概览统计数据
     * @return 概览统计数据
     */
    Map<String, Object> getOverviewStats();
    
    /**
     * 获取所有统计数据
     * @return 所有统计数据
     */
    Map<String, Object> getAllStats();
    
    /**
     * 导出违停记录
     * @param params 查询参数
     * @return Excel文件字节数组
     */
    byte[] exportViolationRecords(ViolationQueryParams params);
    
    /**
     * 发送违规检测通知（仅发送SSE消息，不保存数据库）
     * @param record 违规记录数据
     */
    void sendViolationNotification(ViolationRecord record);
} 