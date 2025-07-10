/**
 * 违规记录
 */
export interface ViolationRecord {
  id: number;
  cameraId: number;
  imagePath: string;
  uploadTime: string;
  confidence: number;
  location: string;
}

/**
 * 统计数据
 */
export interface StatisticsData {
  totalRecords: number;
  todayRecords: number;
  avgConfidence: number;
  cameraStatus: string;
}

/**
 * 系统更新
 */
export interface SystemUpdate {
  id: number;
  type: 'update' | 'feature' | 'notice' | 'optimize';
  title: string;
  content: string;
  time: string;
}

/**
 * 统计卡片数据
 */
export interface StatisticData {
  title: string;
  value: number | string;
  suffix?: string;
  icon: string;
}
