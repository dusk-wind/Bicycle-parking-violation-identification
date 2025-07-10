package com.lihua.demo.Violation.mapper;

import com.lihua.demo.Violation.dto.ViolationQueryParams;
import com.lihua.demo.Violation.entity.ViolationRecord;
import com.lihua.demo.dto.WeeklyTrendDto;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * 违停记录Mapper接口
 * @author lihua
 */
@Mapper
public interface ViolationRecordMapper {
    
    /**
     * 分页查询违停记录列表
     * @param params 查询参数
     * @return 记录列表
     */
    List<ViolationRecord> selectPage(ViolationQueryParams params);
    
    /**
     * 统计总记录数
     * @param params 查询参数
     * @return 总数
     */
    Long countTotal(ViolationQueryParams params);
    
    /**
     * 根据ID查询违停记录
     * @param id 记录ID
     * @return 违停记录
     */
    ViolationRecord selectById(@Param("id") Long id);
    
    /**
     * 插入违停记录
     * @param record 违停记录
     * @return 影响行数
     */
    int insert(ViolationRecord record);
    
    /**
     * 更新违停记录
     * @param record 违停记录
     * @return 影响行数
     */
    int update(ViolationRecord record);
    
    /**
     * 删除违停记录
     * @param id 记录ID
     * @return 影响行数
     */
    int deleteById(@Param("id") Long id);
    
    /**
     * 统计总记录数
     * @return 总数
     */
    Long countAllRecords();
    
    /**
     * 统计今日记录数
     * @return 今日记录数
     */
    Long countTodayRecords();
    
    /**
     * 计算平均置信度
     * @return 平均置信度
     */
    BigDecimal getAverageConfidence();
    
    /**
     * 获取最新记录
     * @param limit 限制数量
     * @return 最新记录列表
     */
    List<ViolationRecord> selectLatestRecords(@Param("limit") Integer limit);
    
    /**
     * 按周统计违规趋势
     * @return 周趋势数据
     */
    List<WeeklyTrendDto> selectWeeklyTrend();
    
    /**
     * 按类型统计违规分布（基于位置信息模拟类型）
     * @return 类型分布数据
     */
    List<Map<String, Object>> selectTypeDistribution();
    
    /**
     * 按地点统计违规分布
     * @return 地点分布数据
     */
    List<Map<String, Object>> selectLocationDistribution();
    
    /**
     * 获取本周违规数量
     * @return 本周违规数量
     */
    Long countThisWeekRecords();
    
    /**
     * 获取上周违规数量
     * @return 上周违规数量
     */
    Long countLastWeekRecords();
    
    /**
     * 获取本月违规数量
     * @return 本月违规数量
     */
    Long countThisMonthRecords();
    
    /**
     * 获取上月违规数量
     * @return 上月违规数量
     */
    Long countLastMonthRecords();
} 