package com.lihua.demo.Violation.controller;

import com.lihua.demo.Violation.dto.ViolationQueryParams;
import com.lihua.demo.Violation.entity.ViolationRecord;
import com.lihua.demo.Violation.service.ViolationRecordService;
import com.lihua.demo.common.PageResult;
import com.lihua.demo.common.Result;
import com.lihua.demo.dto.StatisticsData;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;

/**
 * 违停记录控制器
 * @author lihua
 */
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class ViolationRecordController {

    @Autowired
    private ViolationRecordService violationRecordService;

    /**
     * 分页查询违停记录列表 (History页面)
     */
    @GetMapping("/history/list")
    public Result<PageResult<ViolationRecord>> getViolationList(ViolationQueryParams params) {
        try {
            PageResult<ViolationRecord> result = violationRecordService.getViolationRecords(params);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("获取违停记录失败：" + e.getMessage());
        }
    }

    /**
     * 获取违停记录统计数据 (History页面)
     */
    @GetMapping("/history/stats")
    public Result<StatisticsData> getViolationStats() {
        try {
            StatisticsData stats = violationRecordService.getStatistics();
            return Result.success(stats);
        } catch (Exception e) {
            return Result.error("获取统计数据失败：" + e.getMessage());
        }
    }

    /**
     * 根据ID获取违停记录详情 (History页面和Index页面)
     */
    @GetMapping("/history/detail/{id}")
    public Result<ViolationRecord> getViolationDetail(@PathVariable Long id) {
        try {
            ViolationRecord record = violationRecordService.getViolationById(id);
            if (record == null) {
                return Result.error(404, "记录不存在");
            }
            return Result.success(record);
        } catch (Exception e) {
            return Result.error("获取记录详情失败：" + e.getMessage());
        }
    }

    /**
     * 导出违停记录 (History页面)
     */
    @PostMapping("/history/export")
    public ResponseEntity<byte[]> exportViolationRecords(@RequestBody ViolationQueryParams params) {
        try {
            byte[] data = violationRecordService.exportViolationRecords(params);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
            
            String fileName = "violation_records_" + 
                LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")) + ".csv";
            headers.setContentDispositionFormData("attachment", fileName);
            
            return ResponseEntity.ok()
                    .headers(headers)
                    .body(data);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * 获取首页统计数据 (Index页面)
     */
    @GetMapping("/index/statistics")
    public Result<StatisticsData> getIndexStatistics() {
        try {
            StatisticsData stats = violationRecordService.getStatistics();
            return Result.success(stats);
        } catch (Exception e) {
            return Result.error("获取统计数据失败：" + e.getMessage());
        }
    }

    /**
     * 获取最新记录 (Index页面)
     */
    @GetMapping("/index/latest/{limit}")
    public Result<List<ViolationRecord>> getLatestRecords(@PathVariable Integer limit) {
        try {
            List<ViolationRecord> records = violationRecordService.getLatestRecords(limit);
            return Result.success(records);
        } catch (Exception e) {
            return Result.error("获取最新记录失败：" + e.getMessage());
        }
    }

    /**
     * 获取系统更新信息 (Index页面)
     */
    @GetMapping("/index/updates")
    public Result<List<Map<String, Object>>> getSystemUpdates() {
        try {
            // 模拟系统更新数据
            List<Map<String, Object>> updates = List.of(
                Map.of("type", "update", "title", "系统升级至v2.1.0", "time", "2小时前"),
                Map.of("type", "feature", "title", "新增违停类型检测", "time", "1天前"),
                Map.of("type", "notice", "title", "维护通知", "time", "2天前"),
                Map.of("type", "optimize", "title", "性能优化更新", "time", "3天前")
            );
            return Result.success(updates);
        } catch (Exception e) {
            return Result.error("获取系统更新失败：" + e.getMessage());
        }
    }

    /**
     * 获取概览统计数据 (Data页面)
     */
    @GetMapping("/data/overview")
    public Result<Map<String, Object>> getOverviewStats() {
        try {
            Map<String, Object> stats = violationRecordService.getOverviewStats();
            return Result.success(stats);
        } catch (Exception e) {
            return Result.error("获取概览统计失败：" + e.getMessage());
        }
    }

    /**
     * 获取所有统计数据 (Data页面)
     */
    @GetMapping("/data/all")
    public Result<Map<String, Object>> getAllStats() {
        try {
            Map<String, Object> stats = violationRecordService.getAllStats();
            return Result.success(stats);
        } catch (Exception e) {
            return Result.error("获取统计数据失败：" + e.getMessage());
        }
    }

    /**
     * 添加违停记录
     */
    @PostMapping("/violation/add")
    public Result<String> addViolationRecord(@RequestBody ViolationRecord record) {
        try {
            boolean success = violationRecordService.addViolationRecord(record);
            if (success) {
                return Result.success("添加成功");
            } else {
                return Result.error("添加失败");
            }
        } catch (Exception e) {
            return Result.error("添加违停记录失败：" + e.getMessage());
        }
    }

    /**
     * 更新违停记录
     */
    @PutMapping("/violation/update")
    public Result<String> updateViolationRecord(@RequestBody ViolationRecord record) {
        try {
            boolean success = violationRecordService.updateViolationRecord(record);
            if (success) {
                return Result.success("更新成功");
            } else {
                return Result.error("更新失败");
            }
        } catch (Exception e) {
            return Result.error("更新违停记录失败：" + e.getMessage());
        }
    }

    /**
     * 删除违停记录
     */
    @DeleteMapping("/violation/{id}")
    public Result<String> deleteViolationRecord(@PathVariable Long id) {
        try {
            boolean success = violationRecordService.deleteViolationRecord(id);
            if (success) {
                return Result.success("删除成功");
            } else {
                return Result.error("删除失败");
            }
        } catch (Exception e) {
            return Result.error("删除违停记录失败：" + e.getMessage());
        }
    }

    /**
     * 违规检测通知（用于RDK板端通知新违规记录）
     */
    @PostMapping("/violation/notify")
    public Result<String> notifyViolationDetected(@RequestBody ViolationRecord record) {
        try {
            // 异步发送SSE消息通知（不保存到数据库，因为RDK已经通过pymysql保存了）
            violationRecordService.sendViolationNotification(record);
            return Result.success("通知发送成功");
        } catch (Exception e) {
            return Result.success("通知发送失败，但不影响检测记录保存：" + e.getMessage());
        }
    }
} 