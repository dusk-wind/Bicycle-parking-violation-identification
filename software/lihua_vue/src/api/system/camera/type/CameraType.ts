/**
 * 摄像头信息
 */
export interface CameraInfo {
  id: number;
  serial: string;
  interfaceType: string;
  connected: boolean;
  lastUpdated: string;
}

/**
 * 摄像头列表查询参数
 */
export interface CameraListParams {
  pageNum: number;
  pageSize: number;
  serial?: string;
  interfaceType?: string;
  connected?: boolean;
}

/**
 * 摄像头列表响应
 */
export interface CameraListResponse {
  records: CameraInfo[];
  total: number;
  size: number;
  current: number;
  pages: number;
}

/**
 * 摄像头状态统计
 */
export interface CameraStatusStats {
  totalCameras: number;
  onlineCameras: number;
  offlineCameras: number;
  connectRate: number;
}
