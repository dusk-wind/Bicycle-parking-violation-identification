<template>
  <div class="index-container">
    <!-- 统计数据部分 -->
    <div class="stats-section">
      <a-row :gutter="[16, 16]">
        <a-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6" v-for="stat in stats" :key="stat.title">
          <statistic-card v-bind="stat" />
        </a-col>
      </a-row>
    </div>

    <!-- 功能导航卡片 -->
    <div class="features-section">
      <a-row :gutter="[16, 16]">
        <a-col :xs="12" :sm="12" :md="6" :lg="6" :xl="6" v-for="feature in features" :key="feature.title">
          <a-card
              class="feature-card"
              :bordered="false"
              @click="navigateTo(feature.path)"
          >
            <template #cover>
              <component :is="feature.icon" class="feature-icon" />
            </template>
            <a-card-meta :title="feature.title">
              <template #description>
                <p>{{ feature.description }}</p>
              </template>
            </a-card-meta>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <a-row :gutter="[16, 16]">
        <!-- 违规记录部分 -->
        <a-col :xs="24" :sm="24" :md="16" :lg="16" :xl="16">
          <div class="records-section">
            <div class="section-header">
              <h2>最新违停记录</h2>
              <a-spin :spinning="recordsLoading" />
            </div>
            <a-row :gutter="[16, 16]" v-if="!recordsLoading">
              <a-col
                  :xs="24"
                  :sm="12"
                  :md="12"
                  :lg="8"
                  :xl="8"
                  v-for="record in recentRecords"
                  :key="record.id"
              >
                <a-card
                    class="event-card"
                    :bordered="false"
                    @click="showDetail(record)"
                >
                  <template #cover>
                    <div class="record-number">
                      <span>记录 #{{ record.id }}</span>
                    </div>
                  </template>
                  <a-card-meta>
                    <template #description>
                      <div class="card-description">
                        <p class="time">
                          <clock-circle-outlined /> {{ record.uploadTime }}
                        </p>
                        <p class="location">
                          <environment-outlined /> {{ record.location }}
                        </p>
                        <div class="confidence">
                          <aim-outlined /> 置信度：{{ formatConfidence(record.confidence) }}%
                        </div>
                      </div>
                    </template>
                  </a-card-meta>
                </a-card>
              </a-col>
            </a-row>
            <a-empty v-if="!recordsLoading && recentRecords.length === 0" description="暂无违停记录" />
          </div>
        </a-col>

        <!-- 系统更新部分 -->
        <a-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
          <a-card
              class="updates-card"
              title="系统更新"
              :bordered="false"
          >
            <a-spin :spinning="updatesLoading">
              <a-list
                  :data-source="updates"
                  :split="true"
                  class="updates-list"
              >
                <template #renderItem="{ item }">
                  <a-list-item>
                    <div class="update-content">
                      <div class="update-header">
                        <span :class="['update-tag', item.type]">{{ getUpdateTag(item.type) }}</span>
                        <span class="update-time">{{ item.time }}</span>
                      </div>
                      <div class="update-title">{{ item.title }}</div>
                    </div>
                  </a-list-item>
                </template>
              </a-list>
            </a-spin>
            <a-empty v-if="!updatesLoading && updates.length === 0" description="暂无更新记录" />
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 详情弹窗 -->
    <a-modal
        v-model:open="detailVisible"
        title="违停记录详情"
        width="800px"
        @cancel="closeDetail"
        :footer="null"
        class="detail-modal"
    >
      <a-spin :spinning="detailLoading">
        <div class="detail-content" v-if="selectedRecord">
          <div class="detail-info">
            <a-descriptions bordered>
              <a-descriptions-item label="记录编号" :span="3">
                <database-outlined /> #{{ selectedRecord.id }}
              </a-descriptions-item>
              <a-descriptions-item label="时间" :span="3">
                <clock-circle-outlined /> {{ selectedRecord.uploadTime }}
              </a-descriptions-item>
              <a-descriptions-item label="地点" :span="3">
                <environment-outlined /> {{ selectedRecord.location }}
              </a-descriptions-item>
              <a-descriptions-item label="摄像头" :span="3">
                <camera-outlined /> {{ `摄像头-${selectedRecord.cameraId}` }}
              </a-descriptions-item>
              <a-descriptions-item label="置信度" :span="3">
                <aim-outlined /> {{ formatConfidence(selectedRecord.confidence) }}%
              </a-descriptions-item>
            </a-descriptions>
          </div>

          <div class="detail-image" v-if="selectedRecord.imagePath">
            <img
                :src="getImageUrl(selectedRecord.imagePath)"
                :alt="'违停记录-' + selectedRecord.id"
                class="violation-image"
                @error="handleImageError"
            />
          </div>
        </div>
      </a-spin>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  ClockCircleOutlined,
  CameraOutlined,
  EnvironmentOutlined,
  AimOutlined,
  SearchOutlined,
  CloudServerOutlined,
  VideoCameraOutlined,
  BarChartOutlined,
  DatabaseOutlined,
  CalendarOutlined,
  CheckCircleOutlined
} from '@ant-design/icons-vue';

// 导入统计卡片组件
import StatisticCard from '@/components/statistic-card/index.vue';

// API导入
import {
  getIndexStatistics,
  getLatestRecords,
  getSystemUpdates,
  getViolationDetail
} from '@/api/index/Index.ts';

// 类型导入
import type {
  ViolationRecord,
  StatisticsData,
  SystemUpdate,
  StatisticData
} from '@/api/index/type/IndexType';

// 导入格式化函数
import { formatConfidence } from '@/utils/format';
import { useCameraStore } from '@/stores/camera';

// 图片基础路径
const IMAGE_BASE_PATH = '/assets/images/';

interface Feature {
  title: string;
  description: string;
  icon: any;
  path: string;
}

const router = useRouter();
const cameraStore = useCameraStore();

// 响应式数据
const detailVisible = ref(false);
const selectedRecord = ref<ViolationRecord | null>(null);

// Loading状态
const statsLoading = ref(false);
const recordsLoading = ref(false);
const updatesLoading = ref(false);
const detailLoading = ref(false);

// 数据存储
const statisticsData = ref<StatisticsData | null>(null);
const recentRecords = ref<ViolationRecord[]>([]);
const updates = ref<SystemUpdate[]>([]);

// 功能导航 - 静态数据
const features = ref<Feature[]>([
  {
    title: '违规记录查询',
    description: '支持按时间、地点等多维度查询违规记录，提供详细的违规信息和图片证据。',
    icon: SearchOutlined,
    path: '/history'
  },
  {
    title: '模型在线调用',
    description: '提供YOLOv8目标检测模型的在线调用服务，支持实时图片上传和检测。',
    icon: CloudServerOutlined,
    path: '/model'
  },
  {
    title: '摄像头管理',
    description: '集中管理所有监控摄像头，支持实时预览、状态监控和参数配置。',
    icon: VideoCameraOutlined,
    path: '/camera'
  },
  {
    title: '数据可视化',
    description: '提供丰富的数据统计和分析功能，通过图表直观展示违规趋势。',
    icon: BarChartOutlined,
    path: '/data'
  }
]);

// 计算属性：将后端统计数据转换为卡片显示格式
const stats = computed<StatisticData[]>(() => {
  if (!statisticsData.value) {
    return [
      { title: '总记录数', value: 0, icon: 'database' },
      { title: '今日记录', value: 0, icon: 'calendar' },
      { title: '平均置信度', value: 0, suffix: '%', icon: 'check-circle' },
      { title: '摄像头状态', value: `${cameraStore.onlineCameras}/${cameraStore.totalCameras}`, icon: 'video-camera' }
    ];
  }

  const data = statisticsData.value;
  return [
    {
      title: '总记录数',
      value: data.totalRecords,
      icon: 'database'
    },
    {
      title: '今日记录',
      value: data.todayRecords,
      icon: 'calendar'
    },
    {
      title: '平均置信度',
      // 后端返回的是 0-1 的小数，需要转换为百分比
      value: parseFloat(formatConfidence(data.avgConfidence || 0)),
      suffix: '%',
      icon: 'check-circle'
    },
    {
      title: '摄像头状态',
      value: `${cameraStore.onlineCameras}/${cameraStore.totalCameras}`,
      icon: 'video-camera'
    }
  ];
});

// 更新标签映射
const updateTagMap: Record<SystemUpdate['type'], string> = {
  update: '更新',
  feature: '新功能',
  notice: '通知',
  optimize: '优化'
};

// API调用函数
const fetchStatistics = async () => {
  statsLoading.value = true;
  try {
    const response = await getIndexStatistics();
    if (response.code === 200) {
      statisticsData.value = response.data;
    } else {
      message.error(response.msg || '获取统计数据失败');
    }
  } catch (error) {
    console.error('获取统计数据失败：', error);
    message.error('获取统计数据失败');
  } finally {
    statsLoading.value = false;
  }
};

const fetchLatestRecords = async () => {
  recordsLoading.value = true;
  try {
    const response = await getLatestRecords(6);
    if (response.code === 200) {
      recentRecords.value = response.data;
    } else {
      message.error(response.msg || '获取最新记录失败');
    }
  } catch (error) {
    console.error('获取最新记录失败：', error);
    message.error('获取最新记录失败');
  } finally {
    recordsLoading.value = false;
  }
};

const fetchSystemUpdates = async () => {
  updatesLoading.value = true;
  try {
    const response = await getSystemUpdates();
    if (response.code === 200) {
      updates.value = response.data;
    } else {
      message.error(response.msg || '获取系统更新失败');
    }
  } catch (error) {
    console.error('获取系统更新失败：', error);
    message.error('获取系统更新失败');
  } finally {
    updatesLoading.value = false;
  }
};

const fetchRecordDetail = async (id: number) => {
  detailLoading.value = true;
  try {
    const response = await getViolationDetail(id);
    if (response.code === 200) {
      selectedRecord.value = response.data;
    } else {
      message.error(response.msg || '获取记录详情失败');
    }
  } catch (error) {
    console.error('获取详情失败：', error);
    message.error('获取记录详情失败');
  } finally {
    detailLoading.value = false;
  }
};

// 工具函数
const getImageUrl = (imagePath: string) => {
  if (!imagePath) return '';

  // 如果是完整URL，直接返回
  if (imagePath.startsWith('http')) {
    return imagePath;
  }

  // 如果是相对路径，拼接基础路径
  return `${IMAGE_BASE_PATH}${imagePath}`;
};

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  // 设置一个简单的占位图片或隐藏图片
  img.style.display = 'none';
  console.warn('图片加载失败:', img.src);
  
  // 可选：显示一个错误提示
  message.warning(`图片加载失败: ${selectedRecord.value?.imagePath}`);
};

const getUpdateTag = (type: SystemUpdate['type']): string => {
  return updateTagMap[type] || '未知';
};

// 事件处理函数
function navigateTo(path: string) {
  router.push(path);
}

async function showDetail(record: ViolationRecord) {
  detailVisible.value = true;
  await fetchRecordDetail(record.id);
}

function closeDetail() {
  detailVisible.value = false;
  selectedRecord.value = null;
}

// 生命周期
onMounted(() => {
  // 初始化摄像头状态
  cameraStore.initCameraStatus();
  
  // 并行请求所有数据
  Promise.all([
    fetchStatistics(),
    fetchLatestRecords(),
    fetchSystemUpdates()
  ]).catch(error => {
    console.error('初始化数据加载失败：', error);
  });

  // 定期更新摄像头状态 - 每5分钟
  setInterval(() => {
    cameraStore.fetchCameraStatus();
  }, 5 * 60 * 1000); // 5分钟
});
</script>

<style scoped>
.index-container {
  padding: 16px;
  min-height: 100%;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
  background: #f5f5f7;
}

.stats-section {
  margin-bottom: 24px;
}

.features-section {
  margin-bottom: 24px;
}

.main-content {
  margin-bottom: 24px;
}

/* 功能卡片样式 */
.feature-card {
  background: #fff;
  border-radius: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.feature-card :deep(.ant-card-cover) {
  padding: 24px 24px 12px;
  display: flex;
  justify-content: center;
}

.feature-icon {
  font-size: 32px;
  color: #0071e3;
}

.feature-card :deep(.ant-card-body) {
  padding: 0 24px 24px;
}

.feature-card :deep(.ant-card-meta-title) {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 8px;
  text-align: center;
}

.feature-card :deep(.ant-card-meta-description) {
  color: #86868b;
  font-size: 14px;
  line-height: 1.4;
  text-align: center;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 记录区域样式 */
.records-section {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  height: 100%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 4px;
}

.section-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
}

/* 违规记录卡片样式 */
.event-card {
  height: 100%;
  min-height: 180px;
  background: #fff;
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #e5e5e7;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.record-number {
  padding: 16px;
  background: #f5f5f7;
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  text-align: center;
  border-bottom: 1px solid #e5e5e7;
}

.card-description {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-description p {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #1d1d1f;
}

.confidence {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #0071e3;
  font-weight: 500;
}

.card-description .anticon {
  font-size: 16px;
  color: #86868b;
}

/* 更新动态卡片 */
.updates-card {
  height: 100%;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.updates-card :deep(.ant-card-head) {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e5e7;
}

.updates-card :deep(.ant-card-head-title) {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
}

.updates-card :deep(.ant-card-body) {
  padding: 0;
}

.updates-list {
  padding: 12px 24px;
}

.update-content {
  width: 100%;
  padding: 12px 0;
}

.update-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.update-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  color: #fff;
}

.update-tag.update {
  background-color: #0071e3;
}

.update-tag.feature {
  background-color: #34c759;
}

.update-tag.notice {
  background-color: #ff9f0a;
}

.update-tag.optimize {
  background-color: #5856d6;
}

.update-title {
  font-size: 14px;
  color: #1d1d1f;
}

.update-time {
  font-size: 13px;
  color: #86868b;
}

.violation-image {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
  border-radius: 8px;
  margin-top: 16px;
}

.detail-image {
  text-align: center;
}

:deep(.ant-list-item) {
  padding: 0;
  border-bottom: 1px solid #e5e5e7;
}

:deep(.ant-list-item:last-child) {
  border-bottom: none;
}

/* 响应式调整 */
@media (max-width: 1600px) {
  .index-container {
    padding: 16px 24px;
  }
}

@media (max-width: 1200px) {
  .index-container {
    padding: 16px 20px;
  }

  .feature-card :deep(.ant-card-cover) {
    padding: 20px 20px 10px;
  }

  .feature-card :deep(.ant-card-body) {
    padding: 0 20px 20px;
  }

  .feature-icon {
    font-size: 28px;
  }
}

@media (max-width: 768px) {
  .index-container {
    padding: 12px;
  }

  .records-section,
  .updates-card {
    padding: 16px;
  }

  .section-header h2,
  .updates-card :deep(.ant-card-head-title) {
    font-size: 16px;
  }

  .feature-card :deep(.ant-card-cover) {
    padding: 16px 16px 8px;
  }

  .feature-card :deep(.ant-card-body) {
    padding: 0 16px 16px;
  }

  .feature-icon {
    font-size: 24px;
  }

  .feature-card :deep(.ant-card-meta-title) {
    font-size: 14px;
  }

  .feature-card :deep(.ant-card-meta-description) {
    font-size: 12px;
  }
}

@media (max-width: 576px) {
  .index-container {
    padding: 8px;
  }

  .records-section {
    padding: 12px;
  }

  .record-number {
    padding: 12px;
    font-size: 16px;
  }

  .card-description {
    padding: 12px;
    gap: 8px;
  }

  .card-description p {
    font-size: 13px;
  }
}
</style>
