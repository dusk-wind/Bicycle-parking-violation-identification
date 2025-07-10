<template>
  <div class="illegal-parking-history">
    <HistoryHeader @refresh="handleRefresh" @export="handleExport" />
    <StatCards :stats="stats" :loading="statsLoading" />
    <SearchForm
        :searchForm="searchForm"
        @search="handleSearch"
        @reset="handleReset"
    />
    <ViolationTable
        :data="tableData"
        :loading="loading"
        :pagination="paginationConfig"
        @change="handleTableChange"
        @view-detail="handleViewDetail"
    />
    <DetailModal
        v-model:visible="detailVisible"
        :detail="currentDetail"
        @close="handleCloseDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, onBeforeUnmount } from 'vue';
import { message } from 'ant-design-vue';
import HistoryHeader from './components/HistoryHeader.vue';
import StatCards from './components/StatCards.vue';
import SearchForm from './components/SearchForm.vue';
import ViolationTable from './components/ViolationTable.vue';
import DetailModal from './components/DetailModal.vue';
import { getViolationList, getViolationStats, getViolationDetail, exportViolationRecords } from '@/api/history/violation';
import type {
  ViolationRecord,
  StatisticsData,
  ViolationQueryParams,
  SearchFormState,
  TablePagination,
  PaginationConfig,
  ResponseType
} from '@/api/history/type/violation';
// 组件挂载时获取数据
onMounted(() => {
  fetchStats();
  fetchTableData();
});

// 统计数据
const stats = ref<StatisticsData>({
  totalRecords: 0,
  todayRecords: 0,
  avgConfidence: 0,
  totalCameras: 0
});
const statsLoading = ref(false);

// 搜索表单
const searchForm = ref<SearchFormState>({
  location: '',
  dateRange: null,
  cameraId: undefined
});

// 查询参数
const queryParams = reactive<ViolationQueryParams>({
  pageNum: 1,
  pageSize: 10,
  location: '',
  startDate: '',
  endDate: '',
  cameraId: undefined
});

// 表格数据
const loading = ref(false);
const tableData = ref<ViolationRecord[]>([]);
const total = ref(0);

// 详情弹窗
const detailVisible = ref(false);
const currentDetail = ref<ViolationRecord | null>(null);

// 分页配置
const paginationConfig = computed<PaginationConfig>(() => ({
  current: queryParams.pageNum || 1,
  pageSize: queryParams.pageSize || 10,
  total: total.value,
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50', '100'],
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条记录`
}));

// 获取统计数据
const fetchStats = async () => {
  try {
    statsLoading.value = true;
    const response = await getViolationStats();
    if (response.code === 200) {
      stats.value = response.data;
    } else {
      message.error(response.msg || '获取统计数据失败');
    }
  } catch (error: unknown) {
    console.error('获取统计数据失败:', error);
    message.error('获取统计数据失败');
  } finally {
    statsLoading.value = false;
  }
};

// 获取表格数据
const fetchTableData = async () => {
  try {
    loading.value = true;
    const response = await getViolationList(queryParams);
    if (response.code === 200) {
      tableData.value = response.data.records;
      total.value = response.data.total;
    } else {
      message.error(response.msg || '获取违停记录失败');
    }
  } catch (error: unknown) {
    console.error('获取违停记录失败:', error);
    message.error('获取违停记录失败');
  } finally {
    loading.value = false;
  }
};

// 处理刷新
const handleRefresh = async () => {
  try {
    await Promise.all([fetchStats(), fetchTableData()]);
    message.success('数据已刷新');
  } catch (error) {
    message.error('刷新失败');
  }
};

// 处理导出Excel
const handleExport = async () => {
  try {
    message.loading('正在导出Excel文件...', 0);
    
    // 使用当前查询参数导出
    const exportParams = {
      ...queryParams,
      pageNum: 1,
      pageSize: 9999 // 导出所有数据
    };
    
    console.log('导出参数:', exportParams);
    
    // 调用导出API
    const response = await exportViolationRecords(exportParams);
    
    console.log('导出响应:', response);
    
    // 检查响应数据
    if (!response.data) {
      throw new Error('导出数据为空');
    }
    
    // 检查响应是否为blob类型
    if (response.data instanceof Blob) {
      // 处理Blob响应
      const blob = response.data;
      
      // 检查blob大小
      if (blob.size === 0) {
        throw new Error('生成的文件为空');
      }
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // 设置文件名
      const now = new Date();
      const dateStr = now.getFullYear() + 
                     (now.getMonth() + 1).toString().padStart(2, '0') + 
                     now.getDate().toString().padStart(2, '0');
      link.download = `违规记录_${dateStr}.xlsx`;
      
      // 触发下载
      document.body.appendChild(link);
      link.click();
      
      // 清理资源
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.destroy();
      message.success('导出成功');
    } else {
      // 处理其他类型响应（可能是错误消息）
      console.error('响应不是Blob类型:', typeof response.data);
      throw new Error('服务器返回了非Excel格式的数据');
    }
  } catch (error: any) {
    message.destroy();
    console.error('导出失败:', error);
    
    // 检查是否是网络错误或服务器错误
    if (error.response) {
      const status = error.response.status;
      if (status === 500) {
        message.error('服务器内部错误，请稍后重试');
      } else if (status === 404) {
        message.error('导出接口不存在');
      } else {
        message.error(`服务器错误 (${status})`);
      }
    } else if (error.message) {
      message.error(error.message);
    } else {
      message.error('导出失败，请重试');
    }
  }
};

// 处理搜索
const handleSearch = (form: SearchFormState) => {
  // 同步searchForm状态
  Object.assign(searchForm.value, form);
  
  queryParams.pageNum = 1;
  queryParams.location = form.location || '';
  queryParams.cameraId = form.cameraId;

  if (form.dateRange && Array.isArray(form.dateRange) && form.dateRange.length === 2) {
    queryParams.startDate = form.dateRange[0]?.format('YYYY-MM-DD') || '';
    queryParams.endDate = form.dateRange[1]?.format('YYYY-MM-DD') || '';
  } else {
    queryParams.startDate = '';
    queryParams.endDate = '';
  }

  fetchTableData();
};

// 处理重置
const handleReset = () => {
  // 直接重置searchForm，避免不必要的响应式更新
  Object.assign(searchForm.value, {
    location: '',
    dateRange: null,
    cameraId: undefined
  });

  Object.assign(queryParams, {
    pageNum: 1,
    pageSize: 10,
    location: '',
    startDate: '',
    endDate: '',
    cameraId: undefined
  });

  fetchTableData();
};

// 表格变化处理
const handleTableChange = (pagination: any, filters: any, sorter: any) => {
  queryParams.pageNum = pagination.current;
  queryParams.pageSize = pagination.pageSize;
  fetchTableData();
};

// 查看详情
const handleViewDetail = async (record: ViolationRecord) => {
  try {
    const response = await getViolationDetail(record.id);
    if (response.code === 200) {
      currentDetail.value = response.data;
      detailVisible.value = true;
    } else {
      message.error(response.msg || '获取详情失败');
    }
  } catch (error: unknown) {
    console.error('获取详情失败:', error);
    message.error('获取详情失败');
  }
};

// 关闭详情
const handleCloseDetail = () => {
  detailVisible.value = false;
  currentDetail.value = null;
};
</script>

<style scoped>
.illegal-parking-history {
  padding: 24px;
  background: #f5f5f7;
  min-height: 100vh;
}

@media (max-width: 768px) {
  .illegal-parking-history {
    padding: 16px;
  }
}

@media (max-width: 576px) {
  .illegal-parking-history {
    padding: 12px;
  }
}
</style>
