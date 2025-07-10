// src/api/history/violation.ts

import request from "@/utils/Request";
import type {
    ViolationQueryParams,
    ViolationListResponse,
    StatisticsData,
    ViolationRecord
} from './type/violation';

// 获取违停记录列表
export const getViolationList = (params: ViolationQueryParams) => {
    return request<ViolationListResponse>({
        url: '/api/history/list',
        method: 'get',
        params
    });
};

// 获取统计数据
export const getViolationStats = () => {
    return request<StatisticsData>({
        url: '/api/history/stats',
        method: 'get'
    });
};

// 获取违停记录详情
export const getViolationDetail = (id: number) => {
    return request<ViolationRecord>({
        url: `/api/history/detail/${id}`,
        method: 'get'
    });
};

// 导出违停记录Excel
export const exportViolationRecords = (params: ViolationQueryParams) => {
    return request({
        url: '/api/history/export',
        method: 'post',
        data: params,
        responseType: 'blob'
    });
};
