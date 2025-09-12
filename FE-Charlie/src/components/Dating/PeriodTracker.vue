<template>
  <div class="period-container">
    <h2 class="section-title">经期记录 <span class="emoji">📅</span></h2>
    
    <!-- 周期概览 -->
    <div class="period-overview">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="overview-card next-period">
            <div class="overview-icon">🩸</div>
            <div class="overview-title">下次经期</div>
            <div class="overview-value">{{ nextPeriodDate }}</div>
            <div class="overview-subtitle">还有 {{ daysUntilNextPeriod }} 天</div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="overview-card cycle-length">
            <div class="overview-icon">🔄</div>
            <div class="overview-title">平均周期</div>
            <div class="overview-value">{{ averageCycleLength }} 天</div>
            <div class="overview-subtitle">基于近 {{ cycleHistory.length }} 次记录</div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="overview-card period-length">
            <div class="overview-icon">📊</div>
            <div class="overview-title">平均经期</div>
            <div class="overview-value">{{ averagePeriodLength }} 天</div>
            <div class="overview-subtitle">上次经期 {{ lastPeriodLength }} 天</div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 日历视图 -->
    <div class="period-calendar">
      <h3>月历视图</h3>
      <el-calendar v-model="currentDate">
        <template #dateCell="{ data }">
          <div class="calendar-cell" :class="getCellClass(data.day)">
            <div class="calendar-day">{{ getDayFromDate(data.day) }}</div>
            <div v-if="isPeriodDay(data.day)" class="period-indicator">🩸</div>
            <div v-if="isOvulationDay(data.day)" class="ovulation-indicator">💗</div>
            <div v-if="isFertileDay(data.day)" class="fertile-indicator">✨</div>
          </div>
        </template>
      </el-calendar>
    </div>
    
    <!-- 记录新周期 -->
    <div class="record-period">
      <h3>记录经期</h3>
      <el-form :model="newPeriod" label-position="top">
        <el-row :gutter="20">
          <el-col :md="12" :sm="24">
            <el-form-item label="开始日期">
              <el-date-picker 
                v-model="newPeriod.startDate" 
                type="date" 
                placeholder="选择开始日期"
                format="YYYY/MM/DD"
                value-format="YYYY-MM-DD"
              ></el-date-picker>
            </el-form-item>
          </el-col>
          
          <el-col :md="12" :sm="24">
            <el-form-item label="结束日期">
              <el-date-picker 
                v-model="newPeriod.endDate" 
                type="date" 
                placeholder="选择结束日期"
                format="YYYY/MM/DD"
                value-format="YYYY-MM-DD"
                :disabled="!newPeriod.startDate"
                :min-date="newPeriod.startDate"
              ></el-date-picker>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="经期症状">
          <el-select
            v-model="newPeriod.symptoms"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="选择症状"
          >
            <el-option 
              v-for="symptom in symptoms" 
              :key="symptom.value" 
              :label="symptom.label" 
              :value="symptom.value" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="经期流量">
          <el-radio-group v-model="newPeriod.flow">
            <el-radio label="light">轻微</el-radio>
            <el-radio label="medium">中等</el-radio>
            <el-radio label="heavy">较多</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input 
            v-model="newPeriod.notes" 
            type="textarea" 
            placeholder="添加备注..."
            :rows="2"
          ></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="recordPeriod" :disabled="!newPeriod.startDate">
            <el-icon><Plus /></el-icon> 记录经期
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 历史记录 -->
    <div class="period-history">
      <h3>历史记录</h3>
      <el-table :data="sortedCycleHistory" style="width: 100%">
        <el-table-column label="周期" width="80">
          <template #default="scope">
            <div class="cycle-number">#{{ cycleHistory.length - scope.$index }}</div>
          </template>
        </el-table-column>
        
        <el-table-column label="开始日期">
          <template #default="scope">
            {{ formatDate(scope.row.startDate) }}
          </template>
        </el-table-column>
        
        <el-table-column label="结束日期">
          <template #default="scope">
            {{ scope.row.endDate ? formatDate(scope.row.endDate) : '进行中' }}
          </template>
        </el-table-column>
        
        <el-table-column label="持续天数" width="100">
          <template #default="scope">
            {{ getPeriodLength(scope.row) }} 天
          </template>
        </el-table-column>
        
        <el-table-column label="周期长度" width="100">
          <template #default="scope">
            {{ getCycleLength(scope.row, scope.$index) }} 天
          </template>
        </el-table-column>
        
        <el-table-column label="症状">
          <template #default="scope">
            <el-tag 
              v-for="symptom in scope.row.symptoms" 
              :key="symptom"
              size="small"
              class="symptom-tag"
            >
              {{ getSymptomLabel(symptom) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button type="danger" size="small" @click="deletePeriod(scope.$index)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Plus } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 症状选项
const symptoms = [
  { value: 'cramps', label: '痛经' },
  { value: 'headache', label: '头痛' },
  { value: 'bloating', label: '腹胀' },
  { value: 'fatigue', label: '疲劳' },
  { value: 'mood_swings', label: '情绪波动' },
  { value: 'breast_tenderness', label: '乳房胀痛' },
  { value: 'acne', label: '痘痘' },
  { value: 'backache', label: '背痛' },
  { value: 'nausea', label: '恶心' }
];

// 状态管理
const cycleHistory = ref([
  {
    startDate: '2023-04-05',
    endDate: '2023-04-10',
    symptoms: ['cramps', 'headache'],
    flow: 'medium',
    notes: '这个月经期比较准时'
  },
  {
    startDate: '2023-05-03',
    endDate: '2023-05-08',
    symptoms: ['cramps', 'mood_swings'],
    flow: 'heavy',
    notes: '这次痛经比较严重'
  },
  {
    startDate: '2023-06-01',
    endDate: '2023-06-06',
    symptoms: ['fatigue', 'bloating'],
    flow: 'medium',
    notes: ''
  }
]);

// 当前日期
const currentDate = ref(new Date());

// 新周期表单
const newPeriod = ref({
  startDate: '',
  endDate: '',
  symptoms: [],
  flow: 'medium',
  notes: ''
});

// 记录新周期
const recordPeriod = () => {
  if (!newPeriod.value.startDate) {
    ElMessage.warning('请选择开始日期');
    return;
  }
  
  // 验证日期
  if (newPeriod.value.endDate && new Date(newPeriod.value.endDate) < new Date(newPeriod.value.startDate)) {
    ElMessage.error('结束日期不能早于开始日期');
    return;
  }
  
  const period = { ...newPeriod.value };
  cycleHistory.value.push(period);
  ElMessage.success('记录成功!');
  
  // 重置表单
  newPeriod.value = {
    startDate: '',
    endDate: '',
    symptoms: [],
    flow: 'medium',
    notes: ''
  };
};

// 删除周期记录
const deletePeriod = (index) => {
  cycleHistory.value.splice(index, 1);
  ElMessage.success('删除成功!');
};

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
};

// 获取症状标签
const getSymptomLabel = (symptomValue) => {
  const symptom = symptoms.find(s => s.value === symptomValue);
  return symptom ? symptom.label : symptomValue;
};

// 获取经期长度
const getPeriodLength = (period) => {
  if (!period.startDate) return 0;
  if (!period.endDate) {
    // 如果没有结束日期，计算到今天的天数
    const start = new Date(period.startDate);
    const today = new Date();
    return Math.floor((today - start) / (1000 * 60 * 60 * 24)) + 1;
  }
  
  const start = new Date(period.startDate);
  const end = new Date(period.endDate);
  return Math.floor((end - start) / (1000 * 60 * 60 * 24)) + 1;
};

// 获取周期长度
const getCycleLength = (period, index) => {
  if (index === cycleHistory.value.length - 1) return '-'; // 第一条记录
  
  const currentStart = new Date(period.startDate);
  const nextStart = new Date(cycleHistory.value[index + 1].startDate);
  return Math.floor((nextStart - currentStart) / (1000 * 60 * 60 * 24));
};

// 从日期获取日
const getDayFromDate = (dateStr) => {
  return new Date(dateStr).getDate();
};

// 判断是否是经期日
const isPeriodDay = (dateStr) => {
  const date = new Date(dateStr);
  date.setHours(0, 0, 0, 0);
  
  return cycleHistory.value.some(period => {
    if (!period.startDate) return false;
    
    const start = new Date(period.startDate);
    start.setHours(0, 0, 0, 0);
    
    let end;
    if (period.endDate) {
      end = new Date(period.endDate);
      end.setHours(0, 0, 0, 0);
    } else {
      // 如果没有结束日期，假设持续5天
      end = new Date(period.startDate);
      end.setDate(end.getDate() + 4);
      end.setHours(0, 0, 0, 0);
    }
    
    return date >= start && date <= end;
  });
};

// 判断是否是排卵日
const isOvulationDay = (dateStr) => {
  const date = new Date(dateStr);
  date.setHours(0, 0, 0, 0);
  
  // 预测下一次经期
  const nextPeriodStartDate = predictNextPeriod();
  if (!nextPeriodStartDate) return false;
  
  // 排卵日通常是下次经期前14天
  const ovulationDate = new Date(nextPeriodStartDate);
  ovulationDate.setDate(ovulationDate.getDate() - 14);
  ovulationDate.setHours(0, 0, 0, 0);
  
  return date.getTime() === ovulationDate.getTime();
};

// 判断是否是易孕期
const isFertileDay = (dateStr) => {
  const date = new Date(dateStr);
  date.setHours(0, 0, 0, 0);
  
  // 预测下一次经期
  const nextPeriodStartDate = predictNextPeriod();
  if (!nextPeriodStartDate) return false;
  
  // 排卵日通常是下次经期前14天
  const ovulationDate = new Date(nextPeriodStartDate);
  ovulationDate.setDate(ovulationDate.getDate() - 14);
  ovulationDate.setHours(0, 0, 0, 0);
  
  // 易孕期是排卵日前5天到后4天
  const fertileStart = new Date(ovulationDate);
  fertileStart.setDate(fertileStart.getDate() - 5);
  
  const fertileEnd = new Date(ovulationDate);
  fertileEnd.setDate(fertileEnd.getDate() + 4);
  
  return date >= fertileStart && date <= fertileEnd;
};

// 预测下一次经期
const predictNextPeriod = () => {
  if (cycleHistory.value.length === 0) return null;
  
  // 获取最近一次经期
  const lastPeriod = cycleHistory.value[0];
  const lastStart = new Date(lastPeriod.startDate);
  
  // 使用平均周期长度预测
  const nextStart = new Date(lastStart);
  nextStart.setDate(nextStart.getDate() + averageCycleLength.value);
  
  return nextStart;
};

// 获取日历单元格的类名
const getCellClass = (dateStr) => {
  const classes = [];
  
  if (isPeriodDay(dateStr)) {
    classes.push('period-day');
  }
  
  if (isOvulationDay(dateStr)) {
    classes.push('ovulation-day');
  } else if (isFertileDay(dateStr)) {
    classes.push('fertile-day');
  }
  
  return classes;
};

// 计算属性：排序后的周期历史
const sortedCycleHistory = computed(() => {
  return [...cycleHistory.value].sort((a, b) => {
    return new Date(b.startDate) - new Date(a.startDate);
  });
});

// 计算属性：平均周期长度
const averageCycleLength = computed(() => {
  if (cycleHistory.value.length <= 1) return 28; // 默认28天
  
  let totalDays = 0;
  let count = 0;
  
  for (let i = 0; i < cycleHistory.value.length - 1; i++) {
    const currentStart = new Date(cycleHistory.value[i].startDate);
    const nextStart = new Date(cycleHistory.value[i + 1].startDate);
    const days = Math.floor((nextStart - currentStart) / (1000 * 60 * 60 * 24));
    
    if (days > 0 && days < 60) { // 过滤异常值
      totalDays += days;
      count++;
    }
  }
  
  return count > 0 ? Math.round(totalDays / count) : 28;
});

// 计算属性：平均经期长度
const averagePeriodLength = computed(() => {
  if (cycleHistory.value.length === 0) return 5; // 默认5天
  
  let totalDays = 0;
  let count = 0;
  
  for (const period of cycleHistory.value) {
    if (period.startDate && period.endDate) {
      const days = getPeriodLength(period);
      if (days > 0 && days < 15) { // 过滤异常值
        totalDays += days;
        count++;
      }
    }
  }
  
  return count > 0 ? Math.round(totalDays / count) : 5;
});

// 计算属性：最近一次经期长度
const lastPeriodLength = computed(() => {
  if (cycleHistory.value.length === 0) return 0;
  return getPeriodLength(cycleHistory.value[0]);
});

// 计算属性：下次经期日期
const nextPeriodDate = computed(() => {
  const nextDate = predictNextPeriod();
  return nextDate ? formatDate(nextDate.toISOString().split('T')[0]) : '暂无数据';
});

// 计算属性：距离下次经期的天数
const daysUntilNextPeriod = computed(() => {
  const nextDate = predictNextPeriod();
  if (!nextDate) return '?';
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const days = Math.ceil((nextDate - today) / (1000 * 60 * 60 * 24));
  return days > 0 ? days : 0;
});
</script>

<style scoped>
.period-container {
  max-width: 900px;
  margin: 0 auto;
}

.section-title {
  color: #ec4899;
  font-size: 2rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.emoji {
  font-size: 1.8rem;
}

/* 概览卡片 */
.period-overview {
  margin-bottom: 30px;
}

.overview-card {
  height: 100%;
  text-align: center;
  padding: 20px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.overview-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.overview-title {
  color: #6b7280;
  font-size: 1rem;
  margin-bottom: 5px;
}

.overview-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #ec4899;
  margin-bottom: 5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.overview-subtitle {
  color: #9ca3af;
  font-size: 0.9rem;
}

.next-period {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.cycle-length {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.period-length {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.12);
}

/* 日历视图 */
.period-calendar {
  margin-bottom: 30px;
}

.period-calendar h3 {
  color: #ec4899;
  margin-bottom: 15px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.calendar-cell {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 5px;
}

.calendar-day {
  font-size: 1.2rem;
  margin-bottom: 5px;
}

.period-day {
  background-color: #fdf2f8;
  border-radius: 50%;
}

.ovulation-day {
  background-color: #fff7ed;
  border: 2px solid #fdba74;
  border-radius: 50%;
}

.fertile-day {
  background-color: #fef3c7;
  border-radius: 50%;
}

.period-indicator {
  font-size: 1rem;
}

.ovulation-indicator {
  font-size: 1rem;
  color: #f97316;
}

.fertile-indicator {
  font-size: 1rem;
  color: #f59e0b;
}

/* 记录表单 */
.record-period {
  background: rgba(255, 255, 255, 0.08);
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 30px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.record-period h3 {
  color: #ec4899;
  margin-top: 0;
  margin-bottom: 20px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 历史记录 */
.period-history {
  margin-bottom: 30px;
}

.period-history h3 {
  color: #ec4899;
  margin-bottom: 15px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.cycle-number {
  font-weight: bold;
  color: #ec4899;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.symptom-tag {
  margin-right: 5px;
  margin-bottom: 5px;
  background: rgba(236, 72, 153, 0.1);
  color: #ec4899;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(236, 72, 153, 0.3);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .period-overview .el-col {
    margin-bottom: 15px;
  }
}
</style>