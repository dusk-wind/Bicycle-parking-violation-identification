<template>
  <div class="data-analytics-container">
    <!-- 头部区域 -->
    <div class="header-section">
      <div class="header-content">
        <div class="title-area">
          <p class="description">基于AI视觉识别的校园违停监测与数据分析平台</p>
          <h1 class="page-title">智慧校园违停数据分析</h1>
        </div>
        <div class="action-area">
          <a-button type="primary" @click="refreshData" :loading="refreshing" size="large">
            <template #icon>
              <ReloadOutlined />
            </template>
          刷新数据
        </a-button>
          </div>
        </div>
      </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <!-- 主要趋势图 -->
      <div class="chart-container main-chart">
        <div class="chart-header">
          <div class="chart-title">
            <h3>学期违停趋势</h3>
            <p>18周数据统计分析</p>
        </div>
          <div class="chart-controls">
            <a-radio-group v-model:value="chartType" button-style="solid" size="small">
              <a-radio-button value="line">趋势</a-radio-button>
              <a-radio-button value="bar">柱状</a-radio-button>
              <a-radio-button value="area">面积</a-radio-button>
            </a-radio-group>
          </div>
        </div>
        <div class="chart-content">
          <div id="weekly-trend-chart" class="chart"></div>
        </div>
      </div>

      <!-- 分析图表组 -->
      <div class="analysis-charts">
        <!-- 地点分布图 -->
        <div class="chart-container">
          <div class="chart-header">
            <div class="chart-title">
              <h4>违停高发区域</h4>
              <p>校园地点分析</p>
          </div>
          </div>
          <div class="chart-content">
            <div id="location-chart" class="chart"></div>
        </div>
      </div>

        <!-- 最近7天趋势 -->
          <div class="chart-container">
          <div class="chart-header">
            <div class="chart-title">
              <h4>最近7天趋势</h4>
              <p>每日违停数量变化</p>
          </div>
          </div>
          <div class="chart-content">
            <div id="daily-trend-chart" class="chart"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch, onUnmounted } from 'vue';
import { WarningOutlined, CalendarOutlined, CheckCircleOutlined, VideoCameraOutlined, ReloadOutlined } from '@ant-design/icons-vue';
import * as echarts from 'echarts/core';
import {
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  EffectScatterChart
} from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  ToolboxComponent,
  VisualMapComponent,
  GeoComponent,
  DataZoomComponent
} from 'echarts/components';
import { LabelLayout, UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';
import { getOverviewStats, getAllStats } from '@/api/system/data/Data';
import { message } from 'ant-design-vue';
import { useCameraStore } from '@/stores/camera';

// 注册echarts组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  ToolboxComponent,
  VisualMapComponent,
  GeoComponent,
  DataZoomComponent,
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  EffectScatterChart,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer
]);

// 响应式状态
const chartType = ref('line'); // 图表类型切换
const cameraStore = useCameraStore();

// 图表实例
const charts = {
  weeklyTrend: null,
  location: null,
  dailyTrend: null
};

// 所有数据
let allData = null;

// 定时刷新机制 - 每10分钟刷新一次数据
let dataRefreshInterval = null;

// 刷新状态
const refreshing = ref(false);

// 初始化图表
onMounted(() => {
  // 初始化摄像头状态
  cameraStore.initCameraStatus();
  
  // 初始化各个图表
  initCharts();

  // 获取数据并渲染图表
  fetchDataAndRenderCharts();

  // 窗口调整大小时重新调整图表
  window.addEventListener('resize', handleResize);

  // 开始时间更新
  // updateDateTime(); // 移除不再使用的时间更新
  // 每秒更新时间
  // timeUpdateInterval = setInterval(updateDateTime, 1000); // 移除不再使用的时间更新

  // 设置数据刷新定时器 - 每10分钟
  dataRefreshInterval = setInterval(() => {
    fetchDataAndRenderCharts();
    // 同时更新摄像头状态
    cameraStore.fetchCameraStatus();
  }, 10 * 60 * 1000); // 10分钟
});

// 重置图表大小
const resizeAllCharts = () => {
  // 延迟执行以确保DOM已完全更新
  setTimeout(() => {
    Object.values(charts).forEach(chart => {
      if (chart) {
        chart.resize();
      }
    });
  }, 200);
};

// 组件卸载时清除定时器
onUnmounted(() => {
  if (dataRefreshInterval) {
    clearInterval(dataRefreshInterval);
    dataRefreshInterval = null;
  }

  window.removeEventListener('resize', handleResize);
});

// 初始化所有图表
const initCharts = () => {
  charts.weeklyTrend = echarts.init(document.getElementById('weekly-trend-chart'));
  charts.location = echarts.init(document.getElementById('location-chart'));
  charts.dailyTrend = echarts.init(document.getElementById('daily-trend-chart'));
};

// 获取数据并渲染图表
const fetchDataAndRenderCharts = async () => {
  refreshing.value = true;
  try {
    message.loading('正在获取数据...', 0);

    // 获取所有统计数据
    const response = await getAllStats();
    if (response.code === 200) {
      const data = response.data;

      // 使用真实统计数据
      allData = {
        weeklyTrend: data.weeklyTrend,
        typeDistribution: data.violationType,
        locationDistribution: data.locationDistribution,
        dailyTrend: generateDailyTrendData() // 生成最近7天数据
      };

      // 渲染所有图表
      renderCharts();

      message.destroy();
      message.success('数据加载成功');
    } else {
      message.destroy();
      message.error(response.msg || '获取数据失败');
    }
  } catch (error) {
    message.destroy();
    console.error('获取数据失败:', error);
    message.error('获取数据出错，请稍后重试');
  } finally {
    refreshing.value = false;
  }
};

// 刷新数据
const refreshData = () => {
  fetchDataAndRenderCharts();
};

// 生成最近7天趋势数据
const generateDailyTrendData = () => {
  const today = new Date();
  const dailyData = [];
  for (let i = 6; i >= 0; i--) { // 倒序生成，最近的在右边
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    const dayOfWeek = date.getDay();
    const dayName = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dayOfWeek];
    const dateString = `${date.getMonth() + 1}/${date.getDate()}`;

    // 模拟获取每日违停数量，考虑周末可能较少
    let violationCount;
    if (dayOfWeek === 0 || dayOfWeek === 6) { // 周末
      violationCount = Math.floor(Math.random() * 5) + 1; // 1-5之间
    } else { // 工作日
      violationCount = Math.floor(Math.random() * 8) + 3; // 3-10之间
    }
    
    dailyData.push({
      date: dateString,
      dayOfWeek: dayName,
      violationCount: violationCount
    });
  }
  return dailyData;
};


// 渲染所有图表
const renderCharts = () => {
  renderWeeklyTrendChart();
  renderLocationChart();
  renderDailyTrendChart();
  resizeAllCharts();
};

// 渲染18周趋势图
const renderWeeklyTrendChart = () => {
  const weeklyData = allData?.weeklyTrend || [];

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: 'rgba(0,0,0,0.1)',
      padding: [12, 16],
      textStyle: {
        color: '#1d1d1f',
        fontSize: 14
      },
      extraCssText: 'border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.12);',
      formatter: function(params) {
        const data = params[0];
        return `<div style="font-weight: 600; margin-bottom: 8px;">第${data.dataIndex + 1}周</div>
                <div style="color: #0071e3;">违停数量：${data.value} 起</div>`;
      }
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '5%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: weeklyData.map((_, index) => `第${index + 1}周`),
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#86868b',
        fontSize: 12,
        margin: 16
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(0,0,0,0.06)',
          type: 'dashed'
        }
      },
      axisLabel: {
        color: '#86868b',
        fontSize: 12
      }
    },
    series: getSeries(weeklyData)
  };

  charts.weeklyTrend.setOption(option, true);
};

// 根据图表类型获取系列配置
const getSeries = (data) => {
  const values = data.map(item => item.violationCount || 0);
  
  const commonStyle = {
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: '#007AFF' },
        { offset: 1, color: '#5AC8FA' }
      ])
    }
  };

  switch (chartType.value) {
    case 'bar':
      return [{
        type: 'bar',
        data: values,
        barWidth: '60%',
        ...commonStyle,
        itemStyle: {
          ...commonStyle.itemStyle,
          borderRadius: [6, 6, 0, 0]
          }
      }];
    case 'area':
      return [{
        type: 'line',
        data: values,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: '#007AFF'
        },
        itemStyle: {
          color: '#007AFF',
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 122, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 122, 255, 0.05)' }
          ])
        }
      }];
    default: // line
      return [{
        type: 'line',
        data: values,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: '#007AFF'
        },
        itemStyle: {
          color: '#007AFF',
          borderWidth: 2,
          borderColor: '#fff'
        }
      }];
  }
};

// 渲染地点分布图
const renderLocationChart = () => {
  const locationData = allData?.locationDistribution || [];
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: 'rgba(0,0,0,0.1)',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01],
      axisLine: { show: false },
      splitLine: {
        lineStyle: {
          color: 'rgba(0,0,0,0.06)'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: locationData.map(item => item.location),
      axisLine: { show: false },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      data: locationData.map(item => item.count),
          itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#FF6B6B' },
          { offset: 1, color: '#FF8E53' }
        ]),
        borderRadius: [0, 6, 6, 0]
      }
    }]
  };

  charts.location.setOption(option);
};

// 渲染每日趋势图
const renderDailyTrendChart = () => {
  const dailyData = allData?.dailyTrend || [];

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: 'rgba(0,0,0,0.1)',
      padding: [12, 16],
      textStyle: {
        color: '#1d1d1f',
        fontSize: 14
      },
      extraCssText: 'border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.12);',
      formatter: function(params) {
        const data = params[0];
        return `<div style="font-weight: 600; margin-bottom: 8px;">${data.name}</div>
                <div style="color: #0071e3;">违停数量：${data.value} 起</div>`;
      }
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '5%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dailyData.map(item => `${item.dayOfWeek}`),
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#86868b',
        fontSize: 12,
        margin: 16
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(0,0,0,0.06)',
          type: 'dashed'
        }
      },
      axisLabel: {
        color: '#86868b',
        fontSize: 12
      }
    },
    series: [{
      type: 'line',
      data: dailyData.map(item => item.violationCount),
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        width: 3,
        color: '#007AFF'
      },
          itemStyle: {
        color: '#007AFF',
        borderWidth: 2,
        borderColor: '#fff'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 122, 255, 0.3)' },
          { offset: 1, color: 'rgba(0, 122, 255, 0.05)' }
        ])
      }
    }]
  };

  charts.dailyTrend.setOption(option, true);
};

// 监听图表类型变化
watch(chartType, () => {
  renderWeeklyTrendChart();
});

// 处理窗口大小调整事件
const handleResize = () => {
  // 调整所有图表大小
  Object.values(charts).forEach(chart => {
    chart && chart.resize();
  });
};


</script>

<style scoped>
/* 基础容器样式 */
.data-analytics-container {
  min-height: 100vh;
  background: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
  padding: 40px;
}

/* 头部区域 */
.header-section {
  margin-bottom: 40px;
  text-align: center;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40px;
}

.title-area {
  text-align: left;
}

.description {
  font-size: 17px;
  color: #86868b;
  margin-bottom: 8px;
  line-height: 1.4;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
  letter-spacing: -0.5px;
}

.action-area {
  text-align: right;
  }

/* 图表区域 */
.charts-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.chart-container {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  overflow: hidden;
}

.chart-container:hover {
  border-color: #d2d2d7;
}

.main-chart {
  margin-bottom: 32px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px 32px 0 32px;
  margin-bottom: 24px;
}

.chart-title h3 {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 4px 0;
  letter-spacing: -0.5px;
}

.chart-title h4 {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 4px 0;
  letter-spacing: -0.5px;
}

.chart-title p {
  font-size: 15px;
  color: #86868b;
  margin: 0;
}

.chart-controls {
  display: flex;
  align-items: center;
}

.chart-content {
  padding: 0 32px 32px 32px;
}

.chart {
  width: 100%;
  height: 400px;
}

.main-chart .chart {
  height: 500px;
}

/* 分析图表网格 */
.analysis-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
  gap: 32px;
}

.analysis-charts .chart {
  height: 350px;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .analysis-charts {
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  }
}

@media (max-width: 1024px) {
  .data-analytics-container {
    padding: 32px;
}

  .header-content {
    flex-direction: column;
    gap: 24px;
    text-align: center;
}

  .title-area {
    text-align: center;
  }
  
  .action-area {
    text-align: center;
}

  .analysis-charts {
    grid-template-columns: 1fr;
    gap: 24px;
}
}

@media (max-width: 768px) {
  .data-analytics-container {
    padding: 24px;
}

  .header-content {
    padding: 32px;
}

  .analysis-charts {
    grid-template-columns: 1fr;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .chart-content {
    padding: 0 24px 24px 24px;
  }
  
  .chart-header {
    padding: 24px 24px 0 24px;
  }
}

/* 自定义单选按钮样式 */
:deep(.ant-radio-group) {
  background: #f5f5f7;
  border-radius: 8px;
  padding: 4px;
}

:deep(.ant-radio-button-wrapper) {
  background: transparent;
  border: none;
  border-radius: 6px;
  font-weight: 400;
  transition: all 0.2s ease;
  color: #1d1d1f;
  }

:deep(.ant-radio-button-wrapper-checked) {
  background: #ffffff;
  color: #1d1d1f;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }

:deep(.ant-radio-button-wrapper:hover) {
  color: #1d1d1f;
  }

:deep(.ant-radio-button-wrapper-checked:hover) {
  color: #1d1d1f;
}
</style>


