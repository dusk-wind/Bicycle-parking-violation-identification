package com.lihua.demo.common;

import java.util.List;

/**
 * 分页响应结果类
 * @param <T> 数据类型
 * @author lihua
 */
public class PageResult<T> {
    
    /**
     * 数据列表
     */
    private List<T> records;
    
    /**
     * 总记录数
     */
    private Long total;
    
    /**
     * 当前页码
     */
    private Long current;
    
    /**
     * 每页条数
     */
    private Long pageSize;

    public PageResult() {}

    public PageResult(List<T> records, Long total, Long current, Long pageSize) {
        this.records = records;
        this.total = total;
        this.current = current;
        this.pageSize = pageSize;
    }

    public List<T> getRecords() {
        return records;
    }

    public void setRecords(List<T> records) {
        this.records = records;
    }

    public Long getTotal() {
        return total;
    }

    public void setTotal(Long total) {
        this.total = total;
    }

    public Long getCurrent() {
        return current;
    }

    public void setCurrent(Long current) {
        this.current = current;
    }

    public Long getPageSize() {
        return pageSize;
    }

    public void setPageSize(Long pageSize) {
        this.pageSize = pageSize;
    }

    @Override
    public String toString() {
        return "PageResult{" +
                "records=" + records +
                ", total=" + total +
                ", current=" + current +
                ", pageSize=" + pageSize +
                '}';
    }
} 