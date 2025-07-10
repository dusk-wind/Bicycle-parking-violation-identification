<template>
  <div class="camera-container">
    <!-- 状态栏 -->
    <div class="status-bar" :class="{ 'connected': cameraStore.isConnected }">
      <div class="status-content">
        <div class="status-icon">
          <div class="pulse-ring"></div>
          <div class="dot"></div>
        </div>
        <span class="status-text">{{ cameraStore.isConnected ? '已连接' : '未连接' }}</span>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="main-content">
      <!-- 视频流容器 -->
      <div class="stream-container" :class="{ 'offline': !cameraStore.isConnected }">
        <img
            v-if="cameraStore.isConnected"
            ref="videoRef"
            :src="'/camera-api/stream'"
            class="video-stream"
            @error="onVideoError"
            alt="摄像头视频流"
        />
        <div v-else class="offline-placeholder">
          <camera-outlined class="offline-icon" />
          <p>摄像头未连接</p>
          <p class="offline-hint">点击"连接摄像头"开始视频流</p>
        </div>
      </div>

      <!-- 摄像头信息 -->
      <div class="camera-info">
        <h2>摄像头信息</h2>
        <div class="info-grid" v-if="cameraStore.cameraInfo">
          <div class="info-item">
            <label>设备序列号</label>
            <span>{{ cameraStore.cameraInfo.serial || 'CAM-001' }}</span>
          </div>
          <div class="info-item">
            <label>接口类型</label>
            <span>{{ cameraStore.cameraInfo.interfaceType || 'USB 3.0' }}</span>
          </div>
          <div class="info-item">
            <label>连接状态</label>
            <span :class="{'status-online': cameraStore.isConnected, 'status-offline': !cameraStore.isConnected}">
              {{ cameraStore.connectionStatus }}
            </span>
          </div>
          <div class="info-item">
            <label>最后更新</label>
            <span>{{ formatDate(cameraStore.cameraInfo.lastUpdated) }}</span>
          </div>
        </div>
        <a-empty v-else description="暂无摄像头信息" />
      </div>

      <!-- 控制按钮 -->
      <div class="controls">
        <a-button
            type="primary"
            :loading="loading"
            @click="handleToggleCamera"
            class="control-button"
        >
          {{ cameraStore.isConnected ? '断开连接' : '连接摄像头' }}
        </a-button>
        <a-button
            type="default"
            @click="fetchCameraStatus"
            class="control-button"
        >
          刷新状态
        </a-button>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { message } from 'ant-design-vue';
import { CameraOutlined } from '@ant-design/icons-vue';
import { useCameraStore } from '@/stores/camera';
import dayjs from 'dayjs';

const cameraStore = useCameraStore();
const loading = ref(false);
const videoRef = ref<HTMLImageElement | null>(null);
let statusInterval: number | null = null;

// 格式化日期
const formatDate = (date: string | undefined) => {
  if (!date) return '-';
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss');
};

// 获取摄像头状态
const fetchCameraStatus = async () => {
  await cameraStore.fetchCameraStatus();
};

// 切换摄像头连接状态
const handleToggleCamera = async () => {
  loading.value = true;
  try {
    const connect = !cameraStore.isConnected;
    const result = await cameraStore.toggleCameraStatus(connect);
    
    if (result.success) {
      message.success(result.message);
    } else {
      message.error(result.message);
    }
  } catch (error) {
    message.error('操作失败');
    console.error('切换摄像头状态失败：', error);
  } finally {
    loading.value = false;
  }
};

// 视频事件处理函数
const onVideoError = (event: Event) => {
  console.error('视频加载失败：', event);
  message.error('视频加载失败，请检查摄像头连接');
};

onMounted(() => {
  cameraStore.initCameraStatus();
  // 定期更新状态
  statusInterval = setInterval(fetchCameraStatus, 5000);
});

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval);
  }
});
</script>

<style scoped>
.camera-container {
  min-height: calc(100vh - 120px);  /* 减去导航栏高度 */
  background: #f5f5f7;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-bar {
  background: rgba(255, 59, 48, 0.1);
  padding: 12px 24px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.status-bar.connected {
  background: rgba(52, 199, 89, 0.1);
}

.status-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-icon {
  position: relative;
  width: 12px;
  height: 12px;
}

.dot {
  width: 12px;
  height: 12px;
  background: #ff3b30;
  border-radius: 50%;
  position: absolute;
  top: 0;
  left: 0;
}

.status-bar.connected .dot {
  background: #34c759;
}

.pulse-ring {
  border: 2px solid #ff3b30;
  border-radius: 50%;
  height: 24px;
  width: 24px;
  position: absolute;
  left: -6px;
  top: -6px;
  animation: pulse 2s ease-out infinite;
  opacity: 0;
}

.status-bar.connected .pulse-ring {
  border-color: #34c759;
}

@keyframes pulse {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  50% {
    opacity: 0.25;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.status-text {
  font-size: 14px;
  color: #ff3b30;
}

.status-bar.connected .status-text {
  color: #34c759;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;  /* 占用剩余空间 */
  min-height: 0;  /* 允许内容收缩 */
  width: 100%;
  margin: 0 auto;
}

.stream-container {
  flex: 1;  /* 让视频容器占用主要空间 */
  min-height: 400px;  /* 设置最小高度 */
  max-height: 70vh;  /* 使用视口高度限制最大高度 */
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  display: flex;  /* 添加flex布局 */
  align-items: center;  /* 垂直居中 */
  justify-content: center;  /* 水平居中 */
}

.video-stream {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;  /* 填满容器 */
  border-radius: 0 !important;  /* 无圆角，完全贴合容器 */
}

.offline-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: rgba(255, 255, 255, 0.5);
}

.offline-icon {
  font-size: 48px;
}

.camera-info {
  background: white;
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;  /* 防止信息区域被压缩 */
}

.camera-info h2 {
  margin: 0 0 16px 0;
  color: #1d1d1f;
  font-size: 20px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label {
  color: #86868b;
  font-size: 14px;
}

.info-item span {
  color: #1d1d1f;
  font-size: 14px;
  font-weight: 500;
}

.status-online {
  color: #34c759 !important;
  font-weight: 600;
}

.status-offline {
  color: #ff3b30 !important;
  font-weight: 600;
}

.controls {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
}

.control-button {
  min-width: 100px;
  height: 36px;
  border-radius: 18px;
  font-weight: 500;
}

:deep(.ant-btn-primary) {
  background: #0071e3;
}

:deep(.ant-btn-primary:hover) {
  background: #0077ed;
}

@media (max-width: 768px) {
  .camera-container {
    padding: 12px;
    min-height: calc(100vh - 100px);  /* 移动端减去较小的导航栏高度 */
  }

  .main-content {
    gap: 12px;  /* 减小间距 */
  }

  .stream-container {
    flex: 1;  /* 保持flex布局 */
    min-height: 250px;  /* 设置最小高度 */
    max-height: 60vh;  /* 移动端使用视口高度限制最大高度 */
    display: flex;  /* 确保flex布局 */
    align-items: center;  /* 垂直居中 */
    justify-content: center;  /* 水平居中 */
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .controls {
    flex-direction: column;
  }

  .control-button {
    width: 100%;
  }

  .video-stream {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;  /* 移动端也填满容器 */
    border-radius: 0 !important;  /* 移动端也无圆角 */
  }
}
</style>
