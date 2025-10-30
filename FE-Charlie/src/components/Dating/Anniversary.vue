<template>
  <div class="anniversary-container">
    <h2 class="section-title">纪念日 <span class="emoji">🎂</span></h2>
    
    <!-- 添加新纪念日表单 -->
    <div class="add-anniversary-form">
      <h3>添加新纪念日</h3>
      <el-form :model="newAnniversary" label-position="top">
        <el-form-item label="纪念日名称">
          <el-input v-model="newAnniversary.title" placeholder="例如：相识纪念日"></el-input>
        </el-form-item>
        
        <el-form-item label="纪念日类型">
          <el-select v-model="newAnniversary.type" placeholder="选择类型">
            <el-option label="相识纪念" value="meet" />
            <el-option label="恋爱纪念" value="love" />
            <el-option label="结婚纪念" value="marriage" />
            <el-option label="生日" value="birthday" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期">
          <el-date-picker 
            v-model="newAnniversary.date" 
            type="date" 
            placeholder="选择日期"
            format="YYYY/MM/DD"
            value-format="YYYY-MM-DD"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="是否每年重复">
          <el-switch
            v-model="newAnniversary.isYearly"
            active-text="每年重复"
            inactive-text="仅一次"
            inline-prompt
          ></el-switch>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input 
            v-model="newAnniversary.note" 
            type="textarea" 
            placeholder="添加一些备注..."
            :rows="2"
          ></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="addAnniversary" :disabled="!newAnniversary.title || !newAnniversary.date">
            <el-icon><Plus /></el-icon> 添加纪念日
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 纪念日列表 -->
    <div class="anniversary-list">
      <h3>我们的纪念日</h3>
      
      <!-- 即将到来的纪念日 -->
      <div class="upcoming-anniversaries">
        <h4>即将到来</h4>
        <div class="anniversary-cards">
          <el-empty v-if="upcomingAnniversaries.length === 0" description="暂无即将到来的纪念日" />
          <el-card 
            v-for="item in upcomingAnniversaries" 
            :key="item.id"
            class="anniversary-card upcoming"
          >
            <div class="anniversary-icon" :class="item.type">
              {{ getTypeIcon(item.type) }}
            </div>
            <div class="anniversary-content">
              <h4>{{ item.title }}</h4>
              <p class="anniversary-date">{{ formatDate(item.date) }}</p>
              <p class="anniversary-note" v-if="item.note">{{ item.note }}</p>
              
              <div class="countdown">
                <div class="countdown-value">
                  {{ calculateDaysLeft(item.date, item.isYearly) }}
                </div>
                <div class="countdown-label">天</div>
              </div>
            </div>
            <div class="anniversary-actions">
              <el-button type="danger" size="small" circle @click="deleteAnniversary(item.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
      
      <!-- 所有纪念日 -->
      <div class="all-anniversaries">
        <h4>所有纪念日</h4>
        <el-table :data="sortedAnniversaries" style="width: 100%">
          <el-table-column prop="title" label="名称" />
          <el-table-column label="类型">
            <template #default="scope">
              <el-tag :type="getTypeColor(scope.row.type)">
                {{ getTypeName(scope.row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="date" label="日期" />
          <el-table-column label="倒计时">
            <template #default="scope">
              <div class="table-countdown">
                {{ calculateDaysLeft(scope.row.date, scope.row.isYearly) }} 天
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button type="danger" size="small" @click="deleteAnniversary(scope.row.id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Message } from "@arco-design/web-vue";

// 状态管理
const anniversaries = ref([
  {
    id: 1,
    title: '相识纪念日',
    type: 'meet',
    date: '2022-05-20',
    isYearly: true,
    note: '我们第一次见面的日子'
  },
  {
    id: 2,
    title: '恋爱纪念日',
    type: 'love',
    date: '2022-07-07',
    isYearly: true,
    note: '我们在一起的日子'
  },
  {
    id: 3,
    title: '她的生日',
    type: 'birthday',
    date: '2023-09-15',
    isYearly: true,
    note: '别忘了准备礼物'
  }
]);

// 新纪念日表单
const newAnniversary = ref({
  title: '',
  type: 'love',
  date: '',
  isYearly: true,
  note: ''
});

// 添加新纪念日
const addAnniversary = () => {
  if (!newAnniversary.value.title || !newAnniversary.value.date) {
    Message.warning('请填写纪念日名称和日期');
    return;
  }
  
  const anniversary = {
    ...newAnniversary.value,
    id: Date.now() // 简单生成ID
  };
  
  anniversaries.value.push(anniversary);
  Message.success('添加成功!');
  
  // 重置表单
  newAnniversary.value = {
    title: '',
    type: 'love',
    date: '',
    isYearly: true,
    note: ''
  };
};

// 删除纪念日
const deleteAnniversary = (id) => {
  const index = anniversaries.value.findIndex(item => item.id === id);
  if (index !== -1) {
    anniversaries.value.splice(index, 1);
    Message.success('删除成功!');
  }
};

// 计算天数差
const calculateDaysLeft = (dateStr, isYearly) => {
  const today = new Date();
  let targetDate = new Date(dateStr);
  
  if (isYearly) {
    // 如果是每年重复的纪念日，计算今年的日期
    targetDate.setFullYear(today.getFullYear());
    
    // 如果今年的日期已经过了，计算明年的日期
    if (targetDate < today) {
      targetDate.setFullYear(today.getFullYear() + 1);
    }
  } else if (targetDate < today) {
    // 如果是一次性纪念日且已经过了，显示已过去的天数
    return `已过去 ${Math.floor((today - targetDate) / (1000 * 60 * 60 * 24))} 天`;
  }
  
  // 计算剩余天数
  const daysLeft = Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24));
  return daysLeft;
};

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
};

// 获取类型图标
const getTypeIcon = (type) => {
  const icons = {
    meet: '👋',
    love: '❤️',
    marriage: '💍',
    birthday: '🎂',
    other: '🎯'
  };
  return icons[type] || icons.other;
};

// 获取类型名称
const getTypeName = (type) => {
  const names = {
    meet: '相识纪念',
    love: '恋爱纪念',
    marriage: '结婚纪念',
    birthday: '生日',
    other: '其他'
  };
  return names[type] || names.other;
};

// 获取类型颜色
const getTypeColor = (type) => {
  const colors = {
    meet: 'info',
    love: 'danger',
    marriage: 'success',
    birthday: 'warning',
    other: ''
  };
  return colors[type] || colors.other;
};

// 计算属性：排序后的纪念日列表
const sortedAnniversaries = computed(() => {
  return [...anniversaries.value].sort((a, b) => {
    // 按日期排序
    return new Date(a.date) - new Date(b.date);
  });
});

// 计算属性：即将到来的纪念日
const upcomingAnniversaries = computed(() => {
  const today = new Date();
  
  // 过滤并计算最近的纪念日
  return anniversaries.value
    .map(item => {
      const daysLeft = calculateDaysLeft(item.date, item.isYearly);
      return { ...item, daysLeft };
    })
    .filter(item => {
      // 只显示未来30天内的纪念日
      return typeof item.daysLeft === 'number' && item.daysLeft <= 30;
    })
    .sort((a, b) => a.daysLeft - b.daysLeft)
    .slice(0, 3); // 最多显示3个
});
</script>

<style scoped>
.anniversary-container {
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

.add-anniversary-form {
  background: rgba(255, 255, 255, 0.08);
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 30px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.add-anniversary-form h3 {
  color: #ec4899;
  margin-top: 0;
  margin-bottom: 20px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.anniversary-list h3 {
  color: #ec4899;
  margin-bottom: 20px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.anniversary-list h4 {
  color: #ec4899;
  margin-top: 30px;
  margin-bottom: 15px;
  font-size: 1.2rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.anniversary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.anniversary-card {
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.anniversary-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.anniversary-card.upcoming {
  background: rgba(255, 255, 255, 0.12);
}

.anniversary-icon {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 2rem;
  opacity: 0.7;
}

.anniversary-content {
  padding-right: 40px;
}

.anniversary-content h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #ec4899;
  font-size: 1.2rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.anniversary-date {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.anniversary-note {
  margin-bottom: 15px;
  font-style: italic;
  color: #4b5563;
}

.countdown {
  display: flex;
  align-items: baseline;
  margin-top: 15px;
}

.countdown-value {
  font-size: 2rem;
  font-weight: bold;
  color: #ec4899;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.countdown-label {
  font-size: 1rem;
  color: #6b7280;
  margin-left: 5px;
}

.anniversary-actions {
  position: absolute;
  bottom: 15px;
  right: 15px;
}

.table-countdown {
  font-weight: bold;
  color: #ec4899;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 类型颜色 */
.anniversary-icon.meet {
  color: #0ea5e9;
}

.anniversary-icon.love {
  color: #ec4899;
}

.anniversary-icon.marriage {
  color: #10b981;
}

.anniversary-icon.birthday {
  color: #f59e0b;
}

.anniversary-icon.other {
  color: #8b5cf6;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .anniversary-cards {
    grid-template-columns: 1fr;
  }
  
  .add-anniversary-form {
    padding: 15px;
  }
}
</style>