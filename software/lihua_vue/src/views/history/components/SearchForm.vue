<template>
  <a-card class="search-card">
    <a-form
        ref="formRef"
        :model="formData"
        layout="inline"
        class="search-form"
    >
      <a-form-item name="location" label="违停地点">
        <a-input
            v-model:value="formData.location"
            placeholder="请输入地点"
            allowClear
            class="search-input"
        />
      </a-form-item>
      <a-form-item name="dateRange" label="时间范围">
        <a-range-picker
            v-model:value="formData.dateRange"
            :show-time="false"
            format="YYYY-MM-DD"
            class="date-picker"
        />
      </a-form-item>
      <a-form-item>
        <a-space>
          <a-button type="primary" @click="handleSearch" class="search-button">
            <template #icon><search-outlined /></template>
            搜索
          </a-button>
          <a-button @click="handleReset" class="reset-button">
            <template #icon><clear-outlined /></template>
            重置
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </a-card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { SearchOutlined, ClearOutlined } from '@ant-design/icons-vue';
import type { SearchFormState } from '@/api/history/type/violation';

const props = defineProps<{
  searchForm: SearchFormState;
}>();

const emit = defineEmits<{
  search: [form: SearchFormState];
  reset: [];
}>();

const formRef = ref();
const formData = ref<SearchFormState>({ ...props.searchForm });

// 只监听外部数据变化，避免循环更新
watch(() => props.searchForm, (newVal) => {
  formData.value = { ...newVal };
}, { deep: true });

const handleSearch = () => {
  emit('search', { ...formData.value });
};

const handleReset = () => {
  formRef.value?.resetFields();
  formData.value = {
    location: '',
    dateRange: null,
    cameraId: undefined
  };
  emit('reset');
};
</script>

<style scoped>
.search-card {
  margin-bottom: 24px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.search-form {
  padding: 24px;
}

.search-input,
.date-picker {
  min-width: 200px;
}

@media (max-width: 768px) {
  .search-form {
    padding: 16px;
  }

  .search-input,
  .date-picker {
    min-width: 100%;
  }
}
</style>
