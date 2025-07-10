<template>
  <a-card class="data-table-card">
    <a-table
        :columns="columns"
        :data-source="data"
        :loading="loading"
        :pagination="pagination"
        @change="handleChange"
        class="data-table"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'confidence'">
          <span :class="['confidence-tag', getConfidenceLevel(record.confidence)]">
            {{ formatConfidence(record.confidence) }}%
          </span>
        </template>
        <template v-if="column.key === 'action'">
          <a-button type="link" @click="handleViewDetail(record)" class="view-button">
            查看详情
          </a-button>
        </template>
      </template>
    </a-table>
  </a-card>
</template>

<script setup lang="ts">
import type { ViolationRecord } from '@/api/history/type/violation';

defineProps<{
  data: ViolationRecord[];
  loading: boolean;
  pagination: any;
}>();

const emit = defineEmits<{
  change: [pagination: any, filters: any, sorter: any];
  'view-detail': [record: ViolationRecord];
}>();

// 表格列定义
const columns = [
  {
    title: '记录编号',
    dataIndex: 'id',
    width: 100,
    customRender: ({ text }: { text: number }) => `#${text}`
  },
  {
    title: '违停时间',
    dataIndex: 'uploadTime',
    width: 180
  },
  {
    title: '违停地点',
    dataIndex: 'location',
    width: 200
  },
  {
    title: '置信度',
    dataIndex: 'confidence',
    key: 'confidence',
    width: 120
  },
  {
    title: '操作',
    key: 'action',
    width: 100,
    align: 'center'
  }
];

// 导入格式化函数
import { formatConfidence, getConfidenceLevel } from '@/utils/format';

const handleChange = (pagination: any, filters: any, sorter: any) => {
  emit('change', pagination, filters, sorter);
};

const handleViewDetail = (record: ViolationRecord) => {
  emit('view-detail', record);
};
</script>

<style scoped>
.data-table-card {
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.data-table {
  :deep(.ant-table) {
    background: transparent;
  }

  :deep(.ant-table-thead > tr > th) {
    background: #f5f5f7;
    color: #1d1d1f;
    font-weight: 600;
  }

  :deep(.ant-table-tbody > tr > td) {
    border-bottom: 1px solid #f0f0f0;
  }

  :deep(.ant-table-tbody > tr:hover > td) {
    background: #f5f5f7;
  }
}

.confidence-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 500;
}

.confidence-tag.high {
  background: #e8f5e9;
  color: #34c759;
  border: 1px solid #34c759;
}

.confidence-tag.medium {
  background: #fff8e1;
  color: #ff9800;
  border: 1px solid #ff9800;
}

.confidence-tag.low {
  background: #fef0f0;
  color: #ff3b30;
  border: 1px solid #ff3b30;
}

.view-button {
  color: #0071e3;
  font-weight: 500;
}
</style>
