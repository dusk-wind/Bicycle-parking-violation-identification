<template>
  <div class="statistic-card">
    <div class="statistic-header">
      <div class="statistic-icon">
        <component :is="getIcon()" />
      </div>
      <div class="statistic-title">{{ title }}</div>
    </div>
    <div class="statistic-content">
      <div class="statistic-value">
        {{ value }}
        <span v-if="suffix" class="statistic-suffix">{{ suffix }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  DatabaseOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  VideoCameraOutlined
} from '@ant-design/icons-vue';

interface Props {
  title: string;
  value: number | string;
  suffix?: string;
  icon: string;
}

const props = withDefaults(defineProps<Props>(), {
  suffix: ''
});

const getIcon = () => {
  switch (props.icon) {
    case 'database':
      return DatabaseOutlined;
    case 'calendar':
      return CalendarOutlined;
    case 'check-circle':
      return CheckCircleOutlined;
    case 'video-camera':
      return VideoCameraOutlined;
    default:
      return DatabaseOutlined;
  }
};
</script>

<style scoped>
.statistic-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.statistic-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.statistic-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.statistic-icon {
  font-size: 24px;
  color: #0071e3;
}

.statistic-title {
  font-size: 14px;
  color: #86868b;
  font-weight: 500;
}

.statistic-content {
  flex: 1;
  display: flex;
  align-items: center;
}

.statistic-value {
  font-size: 32px;
  font-weight: 600;
  color: #1d1d1f;
  font-feature-settings: "tnum";
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.statistic-suffix {
  font-size: 16px;
  color: #86868b;
  font-weight: 500;
  margin-left: 4px;
}

@media (max-width: 768px) {
  .statistic-card {
    padding: 16px;
  }
  
  .statistic-value {
    font-size: 24px;
  }
  
  .statistic-title {
    font-size: 12px;
  }
}
</style> 