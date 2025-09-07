<template>
  <div class="activities-container">
    <h2 class="section-title">一起做的事 <span class="emoji">🎯</span></h2>
    
    <!-- 添加新活动表单 -->
    <div class="add-activity-form">
      <h3>添加新活动</h3>
      <el-form :model="newActivity" label-position="top">
        <el-form-item label="活动名称">
          <el-input v-model="newActivity.title" placeholder="例如：一起去看电影"></el-input>
        </el-form-item>
        
        <el-form-item label="活动描述">
          <el-input 
            v-model="newActivity.description" 
            type="textarea" 
            placeholder="描述一下这个活动..."
            :rows="3"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="活动日期">
          <el-date-picker 
            v-model="newActivity.date" 
            type="date" 
            placeholder="选择日期"
            format="YYYY/MM/DD"
            value-format="YYYY-MM-DD"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="活动图片">
          <el-upload
            class="activity-uploader"
            action="#"
            :auto-upload="false"
            :on-change="handleImageChange"
            :limit="1"
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
            <template #file="{file}">
              <div class="upload-image-preview">
                <img class="upload-image" :src="file.url" alt="活动图片" />
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="完成状态">
          <el-switch
            v-model="newActivity.completed"
            active-text="已完成"
            inactive-text="计划中"
            inline-prompt
          ></el-switch>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="addActivity" :disabled="!newActivity.title">
            <el-icon><Plus /></el-icon> 添加活动
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 活动列表 -->
    <div class="activities-list">
      <h3>我们的活动清单</h3>
      
      <el-tabs v-model="activeTab" class="activity-tabs">
        <el-tab-pane label="全部活动" name="all">
          <activity-list :activities="allActivities" @delete="deleteActivity" />
        </el-tab-pane>
        <el-tab-pane label="已完成" name="completed">
          <activity-list :activities="completedActivities" @delete="deleteActivity" />
        </el-tab-pane>
        <el-tab-pane label="计划中" name="planned">
          <activity-list :activities="plannedActivities" @delete="deleteActivity" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Plus } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 活动列表组件
const ActivityList = {
  props: {
    activities: {
      type: Array,
      required: true
    }
  },
  emits: ['delete'],
  setup(props, { emit }) {
    const deleteItem = (id) => {
      emit('delete', id);
    };
    
    return {
      deleteItem
    };
  },
  template: `
    <div class="activity-list-container">
      <div v-if="activities.length === 0" class="empty-list">
        <p>暂无活动</p>
      </div>
      <el-card 
        v-for="activity in activities" 
        :key="activity.id"
        class="activity-card"
        :class="{ 'completed': activity.completed }"
      >
        <div class="activity-header">
          <h4>{{ activity.title }}</h4>
          <div class="activity-actions">
            <el-tag :type="activity.completed ? 'success' : 'info'">
              {{ activity.completed ? '已完成' : '计划中' }}
            </el-tag>
            <el-button type="danger" size="small" circle @click="deleteItem(activity.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
        
        <p class="activity-date">{{ activity.date }}</p>
        <p class="activity-description">{{ activity.description }}</p>
        
        <div v-if="activity.image" class="activity-image">
          <img :src="activity.image" alt="活动图片" />
        </div>
      </el-card>
    </div>
  `
};

// 状态管理
const activities = ref([
  {
    id: 1,
    title: '一起去看日出',
    description: '在海边看日出，感受新的一天开始',
    date: '2023-05-20',
    image: 'https://picsum.photos/id/110/800/400',
    completed: true
  },
  {
    id: 2,
    title: '一起做一顿晚餐',
    description: '尝试做意大利面和沙拉',
    date: '2023-06-15',
    image: 'https://picsum.photos/id/292/800/400',
    completed: true
  },
  {
    id: 3,
    title: '去环球影城',
    description: '体验各种刺激的游乐设施',
    date: '2023-12-25',
    image: null,
    completed: false
  }
]);

const activeTab = ref('all');

// 新活动表单
const newActivity = ref({
  title: '',
  description: '',
  date: '',
  image: null,
  completed: false
});

// 处理图片上传
const handleImageChange = (file) => {
  const isImage = file.raw.type.startsWith('image/');
  if (!isImage) {
    ElMessage.error('只能上传图片文件!');
    return false;
  }
  
  // 在实际应用中，这里应该调用API上传图片
  // 这里简单处理为本地URL
  newActivity.value.image = URL.createObjectURL(file.raw);
};

// 添加新活动
const addActivity = () => {
  if (!newActivity.value.title) {
    ElMessage.warning('请输入活动名称');
    return;
  }
  
  const activity = {
    ...newActivity.value,
    id: Date.now() // 简单生成ID
  };
  
  activities.value.unshift(activity);
  ElMessage.success('添加成功!');
  
  // 重置表单
  newActivity.value = {
    title: '',
    description: '',
    date: '',
    image: null,
    completed: false
  };
};

// 删除活动
const deleteActivity = (id) => {
  const index = activities.value.findIndex(item => item.id === id);
  if (index !== -1) {
    activities.value.splice(index, 1);
    ElMessage.success('删除成功!');
  }
};

// 计算属性：过滤活动列表
const allActivities = computed(() => activities.value);
const completedActivities = computed(() => activities.value.filter(item => item.completed));
const plannedActivities = computed(() => activities.value.filter(item => !item.completed));
</script>

<style scoped>
.activities-container {
  max-width: 900px;
  margin: 0 auto;
}

.section-title {
  color: #be185d;
  font-size: 2rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.emoji {
  font-size: 1.8rem;
}

.add-activity-form {
  background: rgba(255, 255, 255, 0.08);
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 30px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.add-activity-form h3 {
  color: #be185d;
  margin-top: 0;
  margin-bottom: 20px;
}

.activity-uploader {
  width: 100%;
}

.upload-image-preview {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.upload-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.activities-list h3 {
  color: #be185d;
  margin-bottom: 20px;
}

.activity-tabs {
  margin-bottom: 20px;
}

.activity-list-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.empty-list {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  color: #9ca3af;
  font-style: italic;
}

.activity-card {
  transition: all 0.3s ease;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.activity-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.activity-card.completed {
  border-left: 4px solid #10b981;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.activity-header h4 {
  margin: 0;
  font-size: 1.2rem;
  color: #be185d;
}

.activity-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.activity-date {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.activity-description {
  margin-bottom: 15px;
  line-height: 1.5;
}

.activity-image {
  margin-top: 15px;
  border-radius: 8px;
  overflow: hidden;
}

.activity-image img {
  width: 100%;
  height: auto;
  display: block;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .activity-list-container {
    grid-template-columns: 1fr;
  }
  
  .add-activity-form {
    padding: 15px;
  }
}
</style>