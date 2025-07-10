import request from '@/utils/Request';
import type { 
  OverviewStats, 
  WeeklyTrendData, 
  ViolationTypeData, 
  LocationDistributionData,
  AllStatsData 
} from './type/DataType';

/**
 * 获取总览统计数据
 */
export const getOverviewStats = () => {
  return request<OverviewStats>({
    url: '/api/data/overview',
    method: 'GET'
  });
};

// 注意：以下API端点暂时注释，等待后端实现
// /**
//  * 获取周趋势数据
//  */
// export const getWeeklyTrendData = () => {
//   return request<WeeklyTrendData[]>({
//     url: '/api/data/weekly-trend',
//     method: 'GET'
//   });
// };

// /**
//  * 获取违规类型分布数据
//  */
// export const getViolationTypeData = () => {
//   return request<ViolationTypeData[]>({
//     url: '/api/data/violation-type',
//     method: 'GET'
//   });
// };

// /**
//  * 获取地点分布数据
//  */
// export const getLocationDistributionData = () => {
//   return request<LocationDistributionData[]>({
//     url: '/api/data/location-distribution',
//     method: 'GET'
//   });
// };

/**
 * 获取所有统计数据
 */
export const getAllStats = () => {
  return request<AllStatsData>({
    url: '/api/data/all',
    method: 'GET'
  });
};
