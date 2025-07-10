import request from '@/utils/Request';
import type { 
  ViolationRecord, 
  StatisticsData, 
  SystemUpdate 
} from './type/IndexType';

/**
 * 获取首页统计数据
 */
export const getIndexStatistics = () => {
  return request<StatisticsData>({
    url: '/api/index/statistics',
    method: 'GET'
  });
};

/**
 * 获取最新违规记录
 */
export const getLatestRecords = (limit: number = 6) => {
  return request<ViolationRecord[]>({
    url: `/api/index/latest/${limit}`,
    method: 'GET'
  });
};

/**
 * 获取系统更新记录
 */
export const getSystemUpdates = () => {
  return request<SystemUpdate[]>({
    url: '/api/index/updates',
    method: 'GET'
  });
};

/**
 * 获取违规记录详情
 */
export const getViolationDetail = (id: number) => {
  return request<ViolationRecord>({
    url: `/api/history/detail/${id}`,
    method: 'GET'
  });
};
