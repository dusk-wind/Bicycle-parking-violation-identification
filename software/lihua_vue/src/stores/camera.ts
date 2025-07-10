import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// 摄像头信息接口
interface CameraInfo {
  id: number;
  serial: string;
  interfaceType: string;
  connected: boolean;
  lastUpdated: string;
}

// 摄像头状态响应接口
interface CameraStatusResponse {
  code: number;
  msg: string;
  data: {
    camera: CameraInfo;
    streamUrl: string;
  };
}

export const useCameraStore = defineStore('camera', () => {
  // 摄像头信息
  const cameraInfo = ref<CameraInfo | null>(null);
  const streamUrl = ref('');
  const lastUpdateTime = ref<number>(0);

  // 计算属性
  const isConnected = computed(() => cameraInfo.value?.connected ?? false);
  const connectionStatus = computed(() => isConnected.value ? '在线' : '离线');
  const onlineCameras = computed(() => isConnected.value ? 1 : 0);
  const totalCameras = computed(() => 1);

  // 获取摄像头状态 - 使用摄像头API代理
  const fetchCameraStatus = async () => {
    try {
      const response = await fetch('/camera-api/api/camera/status');
      const data: CameraStatusResponse = await response.json();
      
      if (data.code === 200) {
        cameraInfo.value = data.data.camera;
        streamUrl.value = data.data.streamUrl;
        lastUpdateTime.value = Date.now();
        return true;
      }
      return false;
    } catch (error) {
      console.error('获取摄像头状态失败：', error);
      return false;
    }
  };

  // 切换摄像头状态 - 使用摄像头API代理
  const toggleCameraStatus = async (connect: boolean) => {
    try {
      const response = await fetch('/camera-api/api/camera/toggle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ connect })
      });
      
      const data = await response.json();
      if (data.code === 200) {
        await fetchCameraStatus();
        return { success: true, message: data.msg };
      }
      return { success: false, message: data.msg || '操作失败' };
    } catch (error) {
      console.error('切换摄像头状态失败：', error);
      return { success: false, message: '操作失败' };
    }
  };

  // 初始化摄像头状态
  const initCameraStatus = async () => {
    await fetchCameraStatus();
  };

  // 检查是否需要更新状态（缓存5秒）
  const shouldUpdate = () => {
    return Date.now() - lastUpdateTime.value > 5000;
  };

  // 获取缓存的摄像头状态或重新获取
  const getCameraStatus = async () => {
    if (shouldUpdate()) {
      await fetchCameraStatus();
    }
    return {
      connected: isConnected.value,
      onlineCameras: onlineCameras.value,
      totalCameras: totalCameras.value,
      status: connectionStatus.value
    };
  };

  return {
    // 状态
    cameraInfo,
    streamUrl,
    lastUpdateTime,
    
    // 计算属性
    isConnected,
    connectionStatus,
    onlineCameras,
    totalCameras,
    
    // 方法
    fetchCameraStatus,
    toggleCameraStatus,
    initCameraStatus,
    getCameraStatus,
    shouldUpdate
  };
}); 