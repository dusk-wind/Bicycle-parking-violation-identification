<template>
  <div class="model-container">
    <div class="content-wrapper">
      <!-- 标题区域 -->
      <h1 class="page-title">YOLOv8 目标检测</h1>

      <!-- 图片预览区域 -->
      <div class="preview-grid">
        <div class="preview-card">
          <div class="preview-title">原始图片</div>
          <div class="image-preview">
            <img
                v-if="uploadedImage"
                :src="uploadedImage"
                alt="原图"
                @click="showImagePreview(uploadedImage)"
            />
            <div v-else class="upload-hint">
              <picture-outlined class="upload-icon"/>
              <p>请选择要检测的图片</p>
            </div>
          </div>
        </div>

        <div class="preview-card">
          <div class="preview-title">检测结果</div>
          <div class="image-preview">
            <img
                v-if="resultImage"
                :src="resultImage"
                alt="检测结果"
                @click="showImagePreview(resultImage)"
                @error="handleImageError"
                @load="handleImageLoad"
            />
            <div v-else class="upload-hint">
              <file-search-outlined class="upload-icon"/>
              <p>{{ loading ? '正在检测中...' : '等待检测' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作区域 -->
      <div class="operation-area">
        <!-- 文件上传和检测按钮 -->
        <div class="button-group">
          <a-upload
              :beforeUpload="handleBeforeUpload"
              :showUploadList="false"
              accept="image/*"
          >
            <a-button type="primary">
              <template #icon><upload-outlined /></template>
              选择图片
            </a-button>
          </a-upload>
          <a-button
              type="primary"
              :loading="loading"
              @click="startDetection"
              :disabled="!uploadedImage"
          >
            <template #icon><scan-outlined /></template>
            开始检测
          </a-button>
          <a-button
              type="default"
              @click="clearAll"
              :disabled="!uploadedImage && !resultImage"
          >
            <template #icon><clear-outlined /></template>
            清空
          </a-button>
        </div>

        <!-- 位置选择区域 -->
        <div class="location-area">
          <div class="location-title">选择位置</div>
          <div class="location-options">
            <a-radio-group v-model:value="manualLocation" button-style="solid">
              <a-radio-button value="东门邮局">东门邮局</a-radio-button>
              <a-radio-button value="教学楼三">教学楼三</a-radio-button>
              <a-radio-button value="图书馆">图书馆</a-radio-button>
              <a-radio-button value="南二食堂">南二食堂</a-radio-button>
              <a-radio-button value="北体育馆">北体育馆</a-radio-button>
              <a-radio-button value="其他">其他</a-radio-button>
            </a-radio-group>

            <div v-if="manualLocation === '其他'" class="custom-location">
              <a-input
                  v-model:value="customLocation"
                  placeholder="请输入具体位置"
                  style="width: 300px;"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 检测结果统计 -->
      <div class="detection-summary" v-if="detectionResults.length > 0">
        <div class="summary-header">
          <div class="summary-title">检测结果统计</div>
          <a-tag :color="'success'" class="detection-status">
            {{ detectionMessage }}
          </a-tag>
        </div>

        <div class="detection-info">
          <div class="info-item">
            <clock-circle-outlined />
            <span>检测时间：{{ detectionTime }}</span>
          </div>
          <div class="info-item">
            <environment-outlined />
            <span>检测地点：{{ getDisplayLocation }}</span>
          </div>
        </div>

        <div class="summary-grid">
          <div v-for="(category, index) in detectionSummary"
               :key="index"
               class="category-item">
            <div class="category-name">
              <div class="color-dot" :style="{ backgroundColor: category.color }"></div>
              {{ category.name }}
            </div>
            <div class="category-count">数量：{{ category.count }}</div>
            <div class="confidence">置信度：{{ category.avgConfidence.toFixed(2) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片预览模态框 -->
    <a-modal
        v-model:open="previewVisible"
        :footer="null"
        @cancel="handlePreviewCancel"
        width="80%"
        class="image-preview-modal"
    >
      <img :src="previewImage" alt="预览图片" style="width: 100%;" />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { message as antMessage } from 'ant-design-vue';
import {
  UploadOutlined,
  ScanOutlined,
  ClearOutlined,
  PictureOutlined,
  FileSearchOutlined,
  InfoCircleOutlined,
  EnvironmentOutlined,
  ClockCircleOutlined
} from '@ant-design/icons-vue';
import dayjs from 'dayjs';

interface DetectionResult {
  className: string;
  confidence: number;
  color: string;
}

const uploadedImage = ref<string>('');
const resultImage = ref<string>('');
const loading = ref(false);
const detectionResults = ref<DetectionResult[]>([]);
const detectionMessage = ref<string>('等待检测');
let uploadedFile: File | null = null;

// 计算检测结果汇总
const detectionSummary = computed(() => {
  const summary = new Map();

  detectionResults.value.forEach(result => {
    if (!summary.has(result.className)) {
      summary.set(result.className, {
        name: result.className,
        count: 0,
        totalConfidence: 0,
        color: result.color
      });
    }
    const item = summary.get(result.className);
    item.count++;
    item.totalConfidence += result.confidence;
  });

  return Array.from(summary.values()).map(item => ({
    name: item.name,
    count: item.count,
    avgConfidence: item.totalConfidence / item.count,
    color: item.color
  }));
});

// 图片预览相关
const previewVisible = ref(false);
const previewImage = ref('');

const showImagePreview = (imageUrl: string) => {
  previewImage.value = imageUrl;
  previewVisible.value = true;
};

const handlePreviewCancel = () => {
  previewVisible.value = false;
};

// 位置相关状态
const manualLocation = ref('');
const customLocation = ref('');
const detectionTime = ref('');

// 计算显示位置
const getDisplayLocation = computed(() => {
  if (manualLocation.value === '其他') {
    return customLocation.value || '未指定位置';
  }
  return manualLocation.value;
});

const handleBeforeUpload = (file: File) => {
  // 检查文件类型
  const isImage = file.type.startsWith('image/');
  if (!isImage) {
    antMessage.error('只能上传图片文件！');
    return false;
  }

  // 检查文件大小（限制为10MB）
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isLt10M) {
    antMessage.error('图片大小不能超过10MB！');
    return false;
  }

  uploadedFile = file;
  const reader = new FileReader();
  reader.onload = e => {
    uploadedImage.value = e.target?.result as string;
    resultImage.value = ''; // 清除之前的检测结果
    detectionResults.value = []; // 清除之前的检测信息
    detectionMessage.value = '等待检测';
  };
  reader.onerror = () => {
    antMessage.error('图片读取失败，请重试');
    uploadedFile = null;
    uploadedImage.value = '';
  };
  reader.readAsDataURL(file);
  return false;
};

const startDetection = async () => {
  if (!uploadedFile) {
    antMessage.error('请先上传图片');
    return;
  }

  // 检查位置信息
  const location = manualLocation.value === '其他' ? customLocation.value : manualLocation.value;
  if (!location) {
    antMessage.error('请选择或输入位置信息');
    return;
  }

  const formData = new FormData();
  formData.append('file', uploadedFile);
  formData.append('location', location);

  loading.value = true;
  resultImage.value = '';
  detectionResults.value = [];
  detectionMessage.value = '正在检测...';

  try {
    const response = await fetch('http://localhost:5000/detect', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (data.error) {
      antMessage.error(data.error);
      return;
    }

    // 更新图片和检测结果
    if (data.original_image) {
      uploadedImage.value = data.original_image;
    }
    
    if (data.result_image) {
      resultImage.value = data.result_image;
      console.log('结果图片已设置，长度:', data.result_image.length);
    } else {
      console.warn('未收到结果图片数据');
      // 如果没有结果图片，可以显示原图
      if (data.original_image) {
        resultImage.value = data.original_image;
        console.log('使用原图作为结果图片');
      }
    }
    
    detectionResults.value = data.detection_results || [];
    detectionMessage.value = data.message || '检测完成';
    
    // 调试日志
    console.log('检测响应数据:', {
      has_detections: data.has_detections,
      result_image_exists: !!data.result_image,
      result_image_type: typeof data.result_image,
      result_image_length: data.result_image ? data.result_image.length : 0,
      detection_count: data.detection_results ? data.detection_results.length : 0
    });

    // 更新检测时间和地点
    detectionTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss');

    // 显示检测结果提示
    if (data.has_detections) {
      antMessage.success(data.message);
    } else {
      antMessage.warning(data.message);
    }
  } catch (err) {
    console.error('Detection error:', err);
    antMessage.error(err instanceof Error ? err.message : '请求失败，请检查后端服务');
    detectionMessage.value = '检测失败';
  } finally {
    loading.value = false;
  }
};

// 清空所有状态的函数
const clearAll = () => {
  uploadedImage.value = '';
  resultImage.value = '';
  detectionResults.value = [];
  detectionMessage.value = '等待检测';
  uploadedFile = null;
  manualLocation.value = '';
  customLocation.value = '';
  detectionTime.value = '';
  antMessage.success('已清空所有内容');
};

// 图片加载和错误处理
const handleImageError = (event: Event) => {
  console.error('结果图片加载失败:', event);
  antMessage.error('结果图片显示失败');
  const target = event.target as HTMLImageElement;
  if (target) {
    target.style.display = 'none';
  }
};

const handleImageLoad = (event: Event) => {
  console.log('结果图片加载成功');
  const target = event.target as HTMLImageElement;
  if (target) {
    target.style.display = 'block';
  }
};
</script>

<style scoped>
.model-container {
  min-height: 100vh;
  background: #fff;
  padding: 32px;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 32px;
  text-align: left;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
  margin-bottom: 32px;
  min-height: 500px;
}

.preview-card {
  background: white;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.preview-title {
  font-size: 24px;
  font-weight: 500;
  color: #1d1d1f;
  margin-bottom: 24px;
  flex-shrink: 0;
}

.image-preview {
  flex: 1;
  position: relative;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.image-preview img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.upload-hint {
  text-align: center;
  color: #86868b;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #86868b;
}

.operation-area {
  background: white;
  border-radius: 24px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.button-group {
  display: flex;
  gap: 16px;
}

.button-group :deep(.ant-btn) {
  height: 40px;
  padding: 0 24px;
  font-size: 16px;
  border-radius: 20px;
}

.location-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.location-title {
  font-size: 20px;
  font-weight: 500;
  color: #1d1d1f;
  margin-bottom: 24px;
}

.location-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

:deep(.ant-radio-group) {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

:deep(.ant-radio-button-wrapper) {
  height: 36px;
  line-height: 34px;
  padding: 0 16px;
  font-size: 14px;
  border-radius: 18px;
  border: 1px solid #d9d9d9;
  background: #fff;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.ant-radio-button-wrapper::before) {
  display: none !important;
}

:deep(.ant-radio-button-wrapper-checked) {
  border-color: #0071e3;
  background: #0071e3;
  color: #fff;
}

:deep(.ant-radio-button-wrapper:hover) {
  color: #0071e3;
}

:deep(.ant-radio-button-wrapper-checked:hover) {
  color: #fff;
  background: #0071e3;
}

.custom-location {
  margin-top: 8px;
  max-width: 400px;
}

.custom-location :deep(.ant-input) {
  height: 36px;
  border-radius: 18px;
  font-size: 14px;
  text-align: center;
}

.detection-summary {
  background: white;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.summary-title {
  font-size: 24px;
  font-weight: 500;
  color: #1d1d1f;
}

.detection-info {
  border: 1px solid #e5e5e5;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 32px;
  background: #fff;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #1d1d1f;
  font-size: 16px;
  margin-bottom: 12px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 24px;
}

.category-item {
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e5e5e5;
  background: #fff;
}

.category-name {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 12px;
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.category-count,
.confidence {
  font-size: 16px;
  color: #666;
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .model-container {
    padding: 16px;
    min-height: 100vh;
  }

  .page-title {
    font-size: 24px;
    margin-bottom: 24px;
  }

  .preview-grid {
    grid-template-columns: 1fr;
    min-height: auto;
    gap: 24px;
  }

  .preview-card {
    min-height: 350px;
    padding: 24px;
  }

  .preview-title {
    font-size: 20px;
    margin-bottom: 16px;
  }

  .image-preview {
    border-radius: 12px;
  }

  .operation-area {
    padding: 24px;
    gap: 24px;
  }

  .button-group {
    flex-direction: column;
  }

  :deep(.ant-radio-group) {
    grid-template-columns: repeat(2, 1fr);
  }

  :deep(.ant-radio-button-wrapper) {
    width: 100%;
  }
}
</style>