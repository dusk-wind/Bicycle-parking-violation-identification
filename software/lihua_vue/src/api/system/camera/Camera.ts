import request from '@/utils/Request';
import type { CameraInfo, CameraListParams, CameraListResponse } from './type/CameraType';

/**
 * 获取摄像头状态
 */
export const getCameraStatus = () => {
  return request<{
    camera: CameraInfo;
    streamUrl: string;
  }>({
    url: '/api/camera/status',
    method: 'GET'
  });
};

/**
 * 切换摄像头连接状态
 */
export const toggleCamera = (connect: boolean) => {
  return request<void>({
    url: '/api/camera/toggle',
    method: 'POST',
    data: { connect }
  });
};

/**
 * 重启摄像头
 */
export const restartCamera = () => {
  return request<void>({
    url: '/api/camera/restart',
    method: 'POST'
  });
};

/**
 * 获取摄像头列表
 */
export const getCameraList = (params: CameraListParams) => {
  return request<CameraListResponse>({
    url: '/api/camera/list',
    method: 'GET',
    params
  });
};

/**
 * 获取摄像头详情
 */
export const getCameraDetail = (id: number) => {
  return request<CameraInfo>({
    url: `/api/camera/${id}`,
    method: 'GET'
  });
};

/**
 * 添加摄像头
 */
export const addCamera = (data: Partial<CameraInfo>) => {
  return request<void>({
    url: '/api/camera/add',
    method: 'POST',
    data
  });
};

/**
 * 更新摄像头
 */
export const updateCamera = (id: number, data: Partial<CameraInfo>) => {
  return request<void>({
    url: `/api/camera/${id}`,
    method: 'PUT',
    data
  });
};

/**
 * 删除摄像头
 */
export const deleteCamera = (id: number) => {
  return request<void>({
    url: `/api/camera/${id}`,
    method: 'DELETE'
  });
};
