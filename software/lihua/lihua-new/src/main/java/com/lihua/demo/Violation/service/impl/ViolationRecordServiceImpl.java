package com.lihua.demo.Violation.service.impl;

import com.lihua.demo.Camera.mapper.CameraMapper;
import com.lihua.demo.Violation.dto.ViolationQueryParams;
import com.lihua.demo.Violation.entity.ViolationRecord;
import com.lihua.demo.Violation.mapper.ViolationRecordMapper;
import com.lihua.demo.Violation.service.ViolationRecordService;
import com.lihua.demo.common.PageResult;
import com.lihua.demo.dto.StatisticsData;
import com.lihua.demo.dto.WeeklyTrendDto;
import com.lihua.enums.ServerSentEventsEnum;
import com.lihua.model.sse.ServerSentEventsResult;
import com.lihua.utils.sse.ServerSentEventsManager;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 违停记录服务实现类
 * @author lihua
 */
@Slf4j
@Service
public class ViolationRecordServiceImpl implements ViolationRecordService {

    @Autowired
    private ViolationRecordMapper violationRecordMapper;
    
    @Autowired
    private CameraMapper cameraMapper;

    @Override
    public PageResult<ViolationRecord> getViolationRecords(ViolationQueryParams params) {
        // 计算偏移量
        int offset = (params.getPageNum() - 1) * params.getPageSize();
        params.setPageNum(offset);
        
        List<ViolationRecord> records = violationRecordMapper.selectPage(params);
        Long total = violationRecordMapper.countTotal(params);
        
        return new PageResult<>(records, total, (long) params.getPageNum(), (long) params.getPageSize());
    }

    @Override
    public ViolationRecord getViolationById(Long id) {
        return violationRecordMapper.selectById(id);
    }

    @Override
    public StatisticsData getStatistics() {
        Long totalRecords = violationRecordMapper.countAllRecords();
        Long todayRecords = violationRecordMapper.countTodayRecords();
        BigDecimal avgConfidence = violationRecordMapper.getAverageConfidence();
        Long totalCameras = cameraMapper.countTotal();
        Long onlineCameras = cameraMapper.countByConnected(true);
        Long offlineCameras = cameraMapper.countByConnected(false);
        
        return new StatisticsData(totalRecords, todayRecords, avgConfidence, 
                                totalCameras, onlineCameras, offlineCameras);
    }

    @Override
    public List<ViolationRecord> getLatestRecords(Integer limit) {
        return violationRecordMapper.selectLatestRecords(limit);
    }

    @Override
    public boolean addViolationRecord(ViolationRecord record) {
        return violationRecordMapper.insert(record) > 0;
    }

    @Override
    public boolean updateViolationRecord(ViolationRecord record) {
        return violationRecordMapper.update(record) > 0;
    }

    @Override
    public boolean deleteViolationRecord(Long id) {
        return violationRecordMapper.deleteById(id) > 0;
    }

    @Override
    public List<WeeklyTrendDto> getWeeklyTrend() {
        return violationRecordMapper.selectWeeklyTrend();
    }

    @Override
    public List<Map<String, Object>> getTypeDistribution() {
        return violationRecordMapper.selectTypeDistribution();
    }

    @Override
    public List<Map<String, Object>> getLocationDistribution() {
        return violationRecordMapper.selectLocationDistribution();
    }

    @Override
    public Map<String, Object> getOverviewStats() {
        Map<String, Object> overview = new HashMap<>();
        
        // 基础统计
        Long totalViolations = violationRecordMapper.countAllRecords();
        Long weekViolationCount = violationRecordMapper.countThisWeekRecords();
        Long lastWeekCount = violationRecordMapper.countLastWeekRecords();
        Long thisMonthCount = violationRecordMapper.countThisMonthRecords();
        Long lastMonthCount = violationRecordMapper.countLastMonthRecords();
        BigDecimal avgConfidence = violationRecordMapper.getAverageConfidence();
        
        // 摄像头统计
        Long cameraTotal = cameraMapper.countTotal();
        Long cameraOnline = cameraMapper.countByConnected(true);
        Long cameraOffline = cameraMapper.countByConnected(false);
        
        // 计算环比增长率
        double weekCompareRate = calculateCompareRate(weekViolationCount, lastWeekCount);
        double monthCompareRate = calculateCompareRate(thisMonthCount, lastMonthCount);
        
        overview.put("totalViolations", totalViolations);
        overview.put("weekViolationCount", weekViolationCount);
        overview.put("avgConfidence", avgConfidence);
        overview.put("cameraTotal", cameraTotal);
        overview.put("cameraOnline", cameraOnline);
        overview.put("cameraOffline", cameraOffline);
        overview.put("weekCompareRate", weekCompareRate);
        overview.put("monthCompareRate", monthCompareRate);
        
        return overview;
    }

    @Override
    public Map<String, Object> getAllStats() {
        Map<String, Object> allStats = new HashMap<>();
        
        // 概览统计
        allStats.put("overview", getOverviewStats());
        
        // 周趋势
        allStats.put("weeklyTrend", getWeeklyTrend());
        
        // 违规类型分布
        allStats.put("violationType", getTypeDistribution());
        
        // 地点分布
        allStats.put("locationDistribution", getLocationDistribution());
        
        return allStats;
    }

    @Override
    public byte[] exportViolationRecords(ViolationQueryParams params) {
        // 获取所有记录
        List<ViolationRecord> records = violationRecordMapper.selectPage(params);
        
        // 这里应该使用Excel导出库，如POI或EasyExcel
        // 由于项目依赖限制，这里返回简单的CSV格式
        return generateCSVData(records);
    }

    /**
     * 计算环比增长率
     */
    private double calculateCompareRate(Long current, Long previous) {
        if (previous == null || previous == 0) {
            return current == null || current == 0 ? 0 : 100;
        }
        if (current == null) {
            return -100;
        }
        return ((double) (current - previous) / previous) * 100;
    }

    /**
     * 生成CSV格式数据
     */
    private byte[] generateCSVData(List<ViolationRecord> records) {
        try {
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            StringBuilder csv = new StringBuilder();
            
            // CSV头
            csv.append("记录ID,摄像头ID,图片路径,上传时间,置信度,位置\n");
            
            // 数据行
            for (ViolationRecord record : records) {
                csv.append(record.getId()).append(",")
                   .append(record.getCameraId()).append(",")
                   .append(record.getImagePath()).append(",")
                   .append(record.getUploadTime()).append(",")
                   .append(record.getConfidence()).append(",")
                   .append(record.getLocation()).append("\n");
            }
            
            outputStream.write(csv.toString().getBytes("UTF-8"));
            return outputStream.toByteArray();
        } catch (Exception e) {
            throw new RuntimeException("导出数据失败", e);
        }
    }

    @Override
    public void sendViolationNotification(ViolationRecord record) {
        try {
            // 异步发送SSE消息通知
            Map<String, Object> notificationData = new HashMap<>();
            notificationData.put("id", record.getId());
            notificationData.put("cameraId", record.getCameraId());
            notificationData.put("location", record.getLocation());
            notificationData.put("confidence", record.getConfidence());
            notificationData.put("imagePath", record.getImagePath());
            notificationData.put("uploadTime", record.getUploadTime());
            // 处理置信度格式化，确保类型安全
            double confidencePercent = record.getConfidence() != null ? 
                record.getConfidence().multiply(BigDecimal.valueOf(100)).doubleValue() : 0.0;
            notificationData.put("message", String.format("摄像头%d在%s检测到违规行为，置信度%.1f%%", 
                record.getCameraId(), record.getLocation(), confidencePercent));
            
            // 通过SSE向所有在线管理员发送消息
            ServerSentEventsManager.send(
                new ServerSentEventsResult<>(ServerSentEventsEnum.SSE_VIOLATION_ALERT, notificationData)
            );
            
            log.info("违规记录SSE通知已发送: recordId={}, location={}", 
                record.getId(), record.getLocation());
            
        } catch (Exception e) {
            log.error("发送违规记录SSE通知失败", e);
            // 不抛出异常，避免影响主流程
        }
    }
} 