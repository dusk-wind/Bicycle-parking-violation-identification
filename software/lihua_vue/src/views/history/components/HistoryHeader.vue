<template>
  <div class="page-header">
    <h2>违停记录查询</h2>
    <a-space>
      <a-button type="default" @click="handleExport" class="export-button">
        <template #icon><download-outlined /></template>
        导出Excel
      </a-button>
      <a-button type="primary" @click="handleRefresh" class="refresh-button">
        <template #icon><sync-outlined /></template>
        刷新数据
      </a-button>
    </a-space>
  </div>
</template>

<script setup lang="ts">
import { SyncOutlined, DownloadOutlined } from '@ant-design/icons-vue';

const emit = defineEmits<{
  refresh: [];
  export: [];
}>();

const handleRefresh = () => {
  emit('refresh');
};

const handleExport = () => {
  emit('export');
};
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: #1d1d1f;
  font-weight: 600;
  font-size: 28px;
}

@media (max-width: 768px) {
  .page-header h2 {
    font-size: 24px;
  }
}

@media (max-width: 576px) {
  .page-header h2 {
    font-size: 20px;
  }
}
</style>
