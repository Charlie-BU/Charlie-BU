<template>
  <div class="diary-container">
    <h2 class="section-title">心情日记 <span class="emoji">📝</span></h2>
    
    <!-- 添加新日记 -->
    <div class="add-diary-form">
      <h3>今天的心情</h3>
      <el-form :model="newDiary" label-position="top">
        <el-form-item label="日期">
          <el-date-picker 
            v-model="newDiary.date" 
            type="date" 
            placeholder="选择日期"
            format="YYYY/MM/DD"
            value-format="YYYY-MM-DD"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="心情">
          <div class="mood-selector">
            <div 
              v-for="mood in moods" 
              :key="mood.value"
              class="mood-item"
              :class="{ active: newDiary.mood === mood.value }"
              @click="newDiary.mood = mood.value"
            >
              <div class="mood-emoji">{{ mood.emoji }}</div>
              <div class="mood-label">{{ mood.label }}</div>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="标题">
          <el-input v-model="newDiary.title" placeholder="给今天的心情起个标题"></el-input>
        </el-form-item>
        
        <el-form-item label="内容">
          <el-input 
            v-model="newDiary.content" 
            type="textarea" 
            placeholder="写下今天的心情..."
            :rows="5"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="天气">
          <el-select v-model="newDiary.weather" placeholder="今天的天气">
            <el-option label="晴朗 ☀️" value="sunny" />
            <el-option label="多云 ⛅" value="cloudy" />
            <el-option label="雨天 🌧️" value="rainy" />
            <el-option label="雪天 ❄️" value="snowy" />
            <el-option label="雾天 🌫️" value="foggy" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select
            v-model="newDiary.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="添加标签"
          >
            <el-option 
              v-for="tag in availableTags" 
              :key="tag" 
              :label="tag" 
              :value="tag" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="addDiary" :disabled="!newDiary.title || !newDiary.content || !newDiary.mood">
            <el-icon><Plus /></el-icon> 保存日记
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 日记列表 -->
    <div class="diary-list">
      <h3>我的日记本</h3>
      
      <div class="diary-filter">
        <el-input
          v-model="searchQuery"
          placeholder="搜索日记..."
          prefix-icon="Search"
          clearable
          class="search-input"
        ></el-input>
        
        <el-select
          v-model="moodFilter"
          placeholder="按心情筛选"
          clearable
          class="mood-filter"
        >
          <el-option 
            v-for="mood in moods" 
            :key="mood.value" 
            :label="mood.label" 
            :value="mood.value">
            <div style="display: flex; align-items: center;">
              <span style="margin-right: 8px;">{{ mood.emoji }}</span>
              <span>{{ mood.label }}</span>
            </div>
          </el-option>
        </el-select>
      </div>
      
      <div class="diary-timeline">
        <el-timeline>
          <el-empty v-if="filteredDiaries.length === 0" description="暂无日记" />
          
          <el-timeline-item 
            v-for="diary in filteredDiaries" 
            :key="diary.id"
            :timestamp="formatDate(diary.date)"
            :type="getMoodColor(diary.mood)"
          >
            <el-card class="diary-card">
              <template #header>
                <div class="diary-header">
                  <div class="diary-title-section">
                    <span class="diary-mood-emoji">{{ getMoodEmoji(diary.mood) }}</span>
                    <h4>{{ diary.title }}</h4>
                  </div>
                  <div class="diary-actions">
                    <el-button type="primary" size="small" @click="viewDiary(diary)">
                      查看
                    </el-button>
                    <el-button type="danger" size="small" @click="deleteDiary(diary.id)">
                      删除
                    </el-button>
                  </div>
                </div>
              </template>
              
              <div class="diary-preview">
                <p class="diary-weather">{{ getWeatherLabel(diary.weather) }}</p>
                <p class="diary-content-preview">{{ truncateContent(diary.content) }}</p>
                
                <div v-if="diary.tags && diary.tags.length" class="diary-tags">
                  <el-tag 
                    v-for="tag in diary.tags" 
                    :key="tag"
                    size="small"
                    class="diary-tag"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>
    
    <!-- 日记详情弹窗 -->
    <el-dialog
      v-model="diaryDetailVisible"
      :title="selectedDiary?.title || '日记详情'"
      width="70%"
      class="diary-detail-dialog"
    >
      <div v-if="selectedDiary" class="diary-detail">
        <div class="diary-detail-header">
          <div class="diary-detail-date">{{ formatDate(selectedDiary.date) }}</div>
          <div class="diary-detail-mood">
            <span class="mood-emoji">{{ getMoodEmoji(selectedDiary.mood) }}</span>
            <span class="mood-label">{{ getMoodLabel(selectedDiary.mood) }}</span>
          </div>
          <div class="diary-detail-weather">{{ getWeatherLabel(selectedDiary.weather) }}</div>
        </div>
        
        <div class="diary-detail-content">
          {{ selectedDiary.content }}
        </div>
        
        <div v-if="selectedDiary.tags && selectedDiary.tags.length" class="diary-detail-tags">
          <el-tag 
            v-for="tag in selectedDiary.tags" 
            :key="tag"
            size="small"
            class="diary-tag"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Plus, Search } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 心情选项
const moods = [
  { value: 'happy', label: '开心', emoji: '😄', color: 'success' },
  { value: 'excited', label: '兴奋', emoji: '🤩', color: 'success' },
  { value: 'loved', label: '被爱', emoji: '❤️', color: 'danger' },
  { value: 'calm', label: '平静', emoji: '😌', color: 'info' },
  { value: 'tired', label: '疲惫', emoji: '😪', color: 'info' },
  { value: 'sad', label: '难过', emoji: '😢', color: 'warning' },
  { value: 'angry', label: '生气', emoji: '😠', color: 'danger' },
];

// 状态管理
const diaries = ref([
  {
    id: 1,
    date: '2023-05-20',
    mood: 'happy',
    title: '美好的一天',
    content: '今天和TA一起去了公园，天气很好，我们野餐、散步，聊了很多有趣的事情。这样的日子真希望能一直持续下去。',
    weather: 'sunny',
    tags: ['约会', '野餐']
  },
  {
    id: 2,
    date: '2023-05-25',
    mood: 'loved',
    title: '惊喜礼物',
    content: 'TA今天送了我一个惊喜礼物，是我一直想要的那本书。虽然不是什么贵重的东西，但能感受到TA一直在关注我的喜好，很温暖。',
    weather: 'cloudy',
    tags: ['礼物', '感动']
  },
  {
    id: 3,
    date: '2023-06-01',
    mood: 'sad',
    title: '小争执',
    content: '今天因为一点小事和TA吵架了，其实想想也不是什么大问题，但当时就是控制不住情绪。希望明天能和好。',
    weather: 'rainy',
    tags: ['争吵', '反思']
  }
]);

// 新日记表单
const newDiary = ref({
  date: new Date().toISOString().split('T')[0], // 默认今天
  mood: '',
  title: '',
  content: '',
  weather: 'sunny',
  tags: []
});

// 可用标签
const availableTags = ref(['开心', '难过', '约会', '惊喜', '思念', '反思', '计划', '回忆']);

// 搜索和筛选
const searchQuery = ref('');
const moodFilter = ref('');

// 日记详情
const selectedDiary = ref(null);
const diaryDetailVisible = ref(false);

// 添加新日记
const addDiary = () => {
  if (!newDiary.value.title || !newDiary.content || !newDiary.mood) {
    ElMessage.warning('请填写标题、内容和心情');
    return;
  }
  
  const diary = {
    ...newDiary.value,
    id: Date.now() // 简单生成ID
  };
  
  diaries.value.unshift(diary);
  ElMessage.success('保存成功!');
  
  // 更新可用标签
  updateAvailableTags(diary.tags);
  
  // 重置表单
  newDiary.value = {
    date: new Date().toISOString().split('T')[0], // 默认今天
    mood: '',
    title: '',
    content: '',
    weather: 'sunny',
    tags: []
  };
};

// 更新可用标签
const updateAvailableTags = (newTags) => {
  if (!newTags || newTags.length === 0) return;
  
  newTags.forEach(tag => {
    if (!availableTags.value.includes(tag)) {
      availableTags.value.push(tag);
    }
  });
};

// 删除日记
const deleteDiary = (id) => {
  const index = diaries.value.findIndex(item => item.id === id);
  if (index !== -1) {
    diaries.value.splice(index, 1);
    ElMessage.success('删除成功!');
  }
};

// 查看日记详情
const viewDiary = (diary) => {
  selectedDiary.value = diary;
  diaryDetailVisible.value = true;
};

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
};

// 获取心情表情
const getMoodEmoji = (moodValue) => {
  const mood = moods.find(m => m.value === moodValue);
  return mood ? mood.emoji : '😐';
};

// 获取心情标签
const getMoodLabel = (moodValue) => {
  const mood = moods.find(m => m.value === moodValue);
  return mood ? mood.label : '未知';
};

// 获取心情颜色
const getMoodColor = (moodValue) => {
  const mood = moods.find(m => m.value === moodValue);
  return mood ? mood.color : '';
};

// 获取天气标签
const getWeatherLabel = (weather) => {
  const weatherLabels = {
    sunny: '晴朗 ☀️',
    cloudy: '多云 ⛅',
    rainy: '雨天 🌧️',
    snowy: '雪天 ❄️',
    foggy: '雾天 🌫️'
  };
  return weatherLabels[weather] || '';
};

// 截断内容预览
const truncateContent = (content, maxLength = 100) => {
  if (!content) return '';
  return content.length > maxLength ? content.substring(0, maxLength) + '...' : content;
};

// 计算属性：过滤后的日记
const filteredDiaries = computed(() => {
  return diaries.value.filter(diary => {
    // 标题或内容匹配搜索关键词
    const matchesSearch = searchQuery.value === '' || 
      diary.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      diary.content.toLowerCase().includes(searchQuery.value.toLowerCase());
    
    // 心情匹配选中的心情
    const matchesMood = moodFilter.value === '' || diary.mood === moodFilter.value;
    
    return matchesSearch && matchesMood;
  });
});
</script>

<style scoped>
.diary-container {
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

.add-diary-form {
  background: rgba(255, 255, 255, 0.08);
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 30px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.add-diary-form h3 {
  color: #ec4899;
  margin-top: 0;
  margin-bottom: 20px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.mood-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 10px;
}

.mood-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  padding: 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.mood-item:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.mood-item.active {
  background: rgba(255, 255, 255, 0.08);
  border-color: #ec4899;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(236, 72, 153, 0.3);
  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.2);
}

.mood-emoji {
  font-size: 2rem;
  margin-bottom: 5px;
}

.mood-label {
  font-size: 0.9rem;
}

.diary-list h3 {
  color: #ec4899;
  margin-bottom: 20px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.diary-filter {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
}

.mood-filter {
  width: 150px;
}

.diary-timeline {
  padding: 20px 0;
}

.diary-card {
  margin-bottom: 10px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.diary-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.diary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.diary-title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.diary-title-section h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #ec4899;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.diary-mood-emoji {
  font-size: 1.5rem;
}

.diary-actions {
  display: flex;
  gap: 10px;
}

.diary-preview {
  color: #4b5563;
}

.diary-weather {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.diary-content-preview {
  line-height: 1.6;
  margin-bottom: 15px;
}

.diary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.diary-tag {
  background-color: rgba(236, 72, 153, 0.1);
  color: #ec4899;
  border-color: rgba(236, 72, 153, 0.3);
}

/* 日记详情 */
.diary-detail {
  padding: 10px;
}

.diary-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f3f4f6;
}

.diary-detail-date {
  color: #6b7280;
  font-size: 0.9rem;
}

.diary-detail-mood {
  display: flex;
  align-items: center;
  gap: 8px;
}

.diary-detail-mood .mood-emoji {
  font-size: 1.5rem;
}

.diary-detail-mood .mood-label {
  font-size: 1rem;
  color: #4b5563;
}

.diary-detail-weather {
  color: #6b7280;
  font-size: 0.9rem;
}

.diary-detail-content {
  line-height: 1.8;
  margin-bottom: 20px;
  white-space: pre-line;
}

.diary-detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 20px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .diary-filter {
    flex-direction: column;
  }
  
  .mood-filter {
    width: 100%;
  }
  
  .diary-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .diary-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .diary-detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>