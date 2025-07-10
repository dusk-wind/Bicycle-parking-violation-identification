// src/api/history/type/violation.ts

import type { Moment } from 'moment';

// API响应类型
export interface ResponseType<T> {
    code: number;
    msg: string;

}

// 违停记录详情
export interface ViolationRecord {
    id: number;
    cameraId: number;
    imagePath: string;        // 对应数据库的 image_path，只保存文件名
    uploadTime?: string;
    confidence: number;
    location: string;
}

// 违停查询参数
export interface ViolationQueryParams {
    pageNum?: number;
    pageSize?: number;
    location?: string;
    startDate?: string;
    endDate?: string;
    cameraId?: number;
}

// 统计数据
export interface StatisticsData {
    totalRecords: number;
    todayRecords: number;
    avgConfidence: number;
    totalCameras: number;
}

// 违停列表响应数据
export interface ViolationListResponse {
    records: ViolationRecord[];
    total: number;
    current: number;
    size: number;
}

// 搜索表单状态
export interface SearchFormState {
    location?: string;
    dateRange?: [Moment, Moment] | null;
    cameraId?: number;
}

// 分页配置
export interface PaginationConfig {
    current: number;
    pageSize: number;
    total: number;
    showSizeChanger: boolean;
    pageSizeOptions: string[];
    showQuickJumper: boolean;
    showTotal: (total: number, range: [number, number]) => string;
}

// 表格分页参数
export interface TablePagination {
    current: number;
    pageSize: number;
}
