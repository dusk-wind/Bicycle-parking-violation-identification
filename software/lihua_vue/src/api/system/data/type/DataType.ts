/**
 * 总览统计数据
 */
export interface OverviewStats {
  weekViolationCount: number;
  totalViolations: number;
  avgConfidence: number;
  cameraTotal: number;
  cameraOnline: number;
  cameraOffline: number;
  weekCompareRate: number;
  monthCompareRate: number;
}

/**
 * 周趋势数据
 */
export interface WeeklyTrendData {
  week: string;
  violationCount: number;
  date: string;
}

/**
 * 违规类型分布数据
 */
export interface ViolationTypeData {
  type: string;
  count: number;
  percentage: number;
}

/**
 * 地点分布数据
 */
export interface LocationDistributionData {
  location: string;
  count: number;
  percentage: number;
}

/**
 * 数据查询参数
 */
export interface DataQueryParams {
  startDate?: string;
  endDate?: string;
  location?: string;
  violationType?: string;
}

/**
 * 所有统计数据
 */
export interface AllStatsData {
  overview: OverviewStats;
  weeklyTrend: WeeklyTrendData[];
  violationType: ViolationTypeData[];
  locationDistribution: LocationDistributionData[];
}
