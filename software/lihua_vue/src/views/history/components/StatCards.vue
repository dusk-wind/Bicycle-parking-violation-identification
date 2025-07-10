<template>
  <div class="stat-cards">
    <a-card class="stat-card" :loading="loading">
      <template #title>
        <database-outlined /> 总记录数
      </template>
      <h3 class="stat-number">{{ stats.totalRecords }}</h3>

    </a-card>
    <a-card class="stat-card" :loading="loading">
      <template #title>
        <calendar-outlined /> 今日记录
      </template>
      <h3 class="stat-number">{{ stats.todayRecords }}</h3>

    </a-card>
    <a-card class="stat-card" :loading="loading">
      <template #title>
        <check-circle-outlined /> 平均置信度
      </template>
      <h3 class="stat-number">{{ formatConfidence(stats.avgConfidence) }}%</h3>

    </a-card>
    <a-card class="stat-card" :loading="loading">
      <template #title>
        <video-camera-outlined /> 监控点位
      </template>
      <h3 class="stat-number">{{ stats.totalCameras }}</h3>

    </a-card>
  </div>
</template>

<script setup lang="ts">
import {
  DatabaseOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  VideoCameraOutlined
} from '@ant-design/icons-vue';
import type { StatisticsData } from '@/api/history/type/violation';
import { formatConfidence } from '@/utils/format';

defineProps<{
  stats: StatisticsData;
  loading?: boolean;
}>();
</script>

<style scoped>
.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.stat-card :deep(.ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
  padding: 16px 24px;
}

.stat-card :deep(.ant-card-head-title) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  color: #1d1d1f;
}

.stat-card :deep(.ant-card-body) {
  padding: 24px;
}

.stat-number {
  font-size: 36px;
  color: #1d1d1f;
  margin: 0 0 8px;
  font-weight: 600;
}

.stat-trend {
  margin: 0;
  font-size: 14px;
  color: #86868b;
}

.increase {
  color: #34c759;
}

.decrease {
  color: #ff3b30;
}

.normal {
  color: #0071e3;
}

@media (max-width: 1200px) {
  .stat-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stat-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .stat-card :deep(.ant-card-head) {
    padding: 12px 16px;
  }

  .stat-card :deep(.ant-card-body) {
    padding: 16px;
  }

  .stat-number {
    font-size: 28px;
  }
}
</style>
