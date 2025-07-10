<template>
  <a-modal
      :open="visible"
      title="违停记录详情"
      width="800px"
      @cancel="handleClose"
      :footer="null"
      class="detail-modal"
  >
    <div class="detail-content" v-if="detail">
      <div class="detail-info">
        <a-descriptions bordered>
          <a-descriptions-item label="记录编号" :span="3">
            <database-outlined /> #{{ detail.id }}
          </a-descriptions-item>
          <a-descriptions-item label="违停时间" :span="3">
            <clock-circle-outlined /> {{ detail.uploadTime }}
          </a-descriptions-item>
          <a-descriptions-item label="违停地点" :span="3">
            <environment-outlined /> {{ detail.location }}
          </a-descriptions-item>
          <a-descriptions-item label="摄像头" :span="3">
            <camera-outlined /> {{ `摄像头-${detail.cameraId}` }}
          </a-descriptions-item>
          <a-descriptions-item label="置信度" :span="3">
            <aim-outlined />
            <span :class="['confidence-text', getConfidenceLevel(detail.confidence)]">
              {{ formatConfidence(detail.confidence) }}%
            </span>
          </a-descriptions-item>
        </a-descriptions>
      </div>

      <div class="detail-image">
        <template v-if="detail.imagePath">
          <div class="image-container">
            <a-image
                :src="getImageUrl(detail.imagePath)"
                class="violation-image"
                :fallback="'/assets/images/placeholder.jpg'"
            />
          </div>
        </template>
        <template v-else>
          <div class="no-image">
            <inbox-outlined />
            <p>暂无图片</p>
          </div>
        </template>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import {
  DatabaseOutlined,
  ClockCircleOutlined,
  EnvironmentOutlined,
  CameraOutlined,
  AimOutlined,
  InboxOutlined
} from '@ant-design/icons-vue';
import type { ViolationRecord } from '@/api/history/type/violation';

defineProps<{
  visible: boolean;
  detail: ViolationRecord | null;
}>();

const emit = defineEmits<{
  'update:visible': [value: boolean];
  close: [];
}>();

// 图片基础路径
const IMAGE_BASE_PATH = '/assets/images/';

// 导入格式化函数
import { formatConfidence, getConfidenceLevel } from '@/utils/format';

// 获取图片完整URL
const getImageUrl = (imagePath: string) => {
  if (!imagePath) return '';
  
  // 如果是完整URL，直接返回
  if (imagePath.startsWith('http')) {
    return imagePath;
  }
  
  // 如果是相对路径，拼接基础路径
  return `${IMAGE_BASE_PATH}${imagePath}`;
};

const handleClose = () => {
  emit('update:visible', false);
  emit('close');
};
</script>

<style scoped>
.detail-modal {
  :deep(.ant-modal-content) {
    padding: 24px;
    background: #fff;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  }

  :deep(.ant-modal-header) {
    margin-bottom: 24px;
  }

  :deep(.ant-modal-title) {
    font-size: 20px;
    font-weight: 600;
    color: #1d1d1f;
  }
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-info {
  :deep(.ant-descriptions) {
    background: #f5f5f7;
    border-radius: 12px;
    overflow: hidden;
  }

  :deep(.ant-descriptions-item-label) {
    width: 100px;
    background: rgba(0, 0, 0, 0.02);
    color: #1d1d1f;
    font-weight: 500;
  }

  :deep(.ant-descriptions-item-content) {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #1d1d1f;
    font-size: 14px;
  }
}

.confidence-text {
  font-weight: 500;
}

.confidence-text.high {
  color: #34c759;
  font-weight: 600;
}

.confidence-text.medium {
  color: #ff9800;
  font-weight: 600;
}

.confidence-text.low {
  color: #ff3b30;
  font-weight: 600;
}

.detail-image {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f5f7;
  border-radius: 12px;
  padding: 24px;
}

.image-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.violation-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
  border-radius: 8px;
}

.no-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #86868b;
}

.no-image :deep(.anticon) {
  font-size: 48px;
  margin-bottom: 16px;
}

.no-image p {
  margin: 0;
  font-size: 14px;
}
</style>
