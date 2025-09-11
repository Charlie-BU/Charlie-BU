<template>
  <div class="gallery-container">
    <h2 class="section-title">恋爱相册 <span class="emoji">📷</span></h2>
    
    <!-- 添加新照片 -->
    <div class="add-photo-form">
      <h3>添加新照片</h3>
      <el-form :model="newPhoto" label-position="top">
        <el-form-item label="照片标题">
          <el-input v-model="newPhoto.title" placeholder="给这张照片起个名字"></el-input>
        </el-form-item>
        
        <el-form-item label="照片描述">
          <el-input 
            v-model="newPhoto.description" 
            type="textarea" 
            placeholder="描述一下这张照片..."
            :rows="2"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="拍摄日期">
          <el-date-picker 
            v-model="newPhoto.date" 
            type="date" 
            placeholder="选择日期"
            format="YYYY/MM/DD"
            value-format="YYYY-MM-DD"
          ></el-date-picker>
        </el-form-item>
        
        <el-form-item label="照片">
          <el-upload
            class="photo-uploader"
            action="#"
            :auto-upload="false"
            :on-change="handlePhotoChange"
            :limit="1"
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
            <template #file="{file}">
              <div class="upload-photo-preview">
                <img class="upload-photo" :src="file.url" alt="照片预览" />
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select
            v-model="newPhoto.tags"
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
          <el-button type="primary" @click="addPhoto" :disabled="!newPhoto.title || !newPhoto.imageUrl">
            <el-icon><Plus /></el-icon> 添加照片
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- 照片筛选 -->
    <div class="gallery-filter">
      <h3>照片墙</h3>
      <div class="filter-controls">
        <el-input
          v-model="searchQuery"
          placeholder="搜索照片..."
          prefix-icon="Search"
          clearable
          class="search-input"
        ></el-input>
        
        <el-select
          v-model="selectedTags"
          multiple
          collapse-tags
          collapse-tags-tooltip
          placeholder="按标签筛选"
          class="tag-filter"
        >
          <el-option 
            v-for="tag in allTags" 
            :key="tag" 
            :label="tag" 
            :value="tag" 
          />
        </el-select>
      </div>
    </div>
    
    <!-- 照片墙 -->
    <div class="photo-gallery">
      <el-empty v-if="filteredPhotos.length === 0" description="暂无照片" />
      
      <div v-else class="masonry-gallery">
        <div 
          v-for="photo in filteredPhotos" 
          :key="photo.id"
          class="gallery-item"
          @click="openPhotoDetail(photo)"
        >
          <div class="gallery-image">
            <img :src="photo.imageUrl" :alt="photo.title" />
          </div>
          <div class="gallery-overlay">
            <h4>{{ photo.title }}</h4>
            <p class="gallery-date">{{ photo.date }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 照片详情弹窗 -->
    <el-dialog
      v-model="photoDetailVisible"
      :title="selectedPhoto?.title || '照片详情'"
      width="80%"
      class="photo-detail-dialog"
    >
      <div v-if="selectedPhoto" class="photo-detail">
        <div class="photo-detail-image">
          <img :src="selectedPhoto.imageUrl" :alt="selectedPhoto.title" />
        </div>
        <div class="photo-detail-info">
          <p class="photo-detail-date">{{ formatDate(selectedPhoto.date) }}</p>
          <p class="photo-detail-description">{{ selectedPhoto.description }}</p>
          
          <div class="photo-detail-tags">
            <el-tag 
              v-for="tag in selectedPhoto.tags" 
              :key="tag"
              size="small"
              class="photo-tag"
            >
              {{ tag }}
            </el-tag>
          </div>
          
          <div class="photo-detail-actions">
            <el-button type="danger" @click="deletePhoto(selectedPhoto.id)">
              <el-icon><Delete /></el-icon> 删除照片
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { Plus, Delete, Search } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 状态管理
const photos = ref([
  {
    id: 1,
    title: '海边日落',
    description: '我们一起看的第一次日落',
    date: '2022-08-15',
    imageUrl: 'https://picsum.photos/id/1015/800/600',
    tags: ['海边', '日落', '浪漫']
  },
  {
    id: 2,
    title: '咖啡馆约会',
    description: '在那家很喜欢的咖啡馆',
    date: '2022-09-20',
    imageUrl: 'https://picsum.photos/id/1060/800/600',
    tags: ['咖啡', '约会']
  },
  {
    id: 3,
    title: '生日惊喜',
    description: '给你准备的生日派对',
    date: '2022-10-10',
    imageUrl: 'https://picsum.photos/id/145/800/600',
    tags: ['生日', '派对', '惊喜']
  },
  {
    id: 4,
    title: '公园野餐',
    description: '春天的野餐真美好',
    date: '2023-04-05',
    imageUrl: 'https://picsum.photos/id/355/800/600',
    tags: ['野餐', '公园', '春天']
  },
  {
    id: 5,
    title: '旅行合影',
    description: '我们的第一次旅行',
    date: '2023-05-20',
    imageUrl: 'https://picsum.photos/id/304/800/600',
    tags: ['旅行', '合影']
  }
]);

// 新照片表单
const newPhoto = ref({
  title: '',
  description: '',
  date: '',
  imageUrl: null,
  tags: []
});

// 可用标签
const availableTags = ref(['旅行', '约会', '浪漫', '生日', '纪念日', '日常', '美食', '风景']);

// 搜索和筛选
const searchQuery = ref('');
const selectedTags = ref([]);

// 照片详情
const selectedPhoto = ref(null);
const photoDetailVisible = ref(false);

// 处理照片上传
const handlePhotoChange = (file) => {
  const isImage = file.raw.type.startsWith('image/');
  if (!isImage) {
    ElMessage.error('只能上传图片文件!');
    return false;
  }
  
  // 在实际应用中，这里应该调用API上传图片
  // 这里简单处理为本地URL
  newPhoto.value.imageUrl = URL.createObjectURL(file.raw);
};

// 添加新照片
const addPhoto = () => {
  if (!newPhoto.value.title || !newPhoto.value.imageUrl) {
    ElMessage.warning('请输入照片标题并上传照片');
    return;
  }
  
  const photo = {
    ...newPhoto.value,
    id: Date.now(), // 简单生成ID
    date: newPhoto.value.date || new Date().toISOString().split('T')[0] // 如果没有选择日期，使用今天
  };
  
  photos.value.unshift(photo);
  ElMessage.success('添加成功!');
  
  // 更新可用标签
  updateAvailableTags(photo.tags);
  
  // 重置表单
  newPhoto.value = {
    title: '',
    description: '',
    date: '',
    imageUrl: null,
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

// 删除照片
const deletePhoto = (id) => {
  const index = photos.value.findIndex(item => item.id === id);
  if (index !== -1) {
    photos.value.splice(index, 1);
    ElMessage.success('删除成功!');
    photoDetailVisible.value = false;
  }
};

// 打开照片详情
const openPhotoDetail = (photo) => {
  selectedPhoto.value = photo;
  photoDetailVisible.value = true;
};

// 格式化日期
const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
};

// 计算属性：所有标签
const allTags = computed(() => {
  const tags = new Set();
  photos.value.forEach(photo => {
    if (photo.tags && photo.tags.length) {
      photo.tags.forEach(tag => tags.add(tag));
    }
  });
  return Array.from(tags);
});

// 计算属性：过滤后的照片
const filteredPhotos = computed(() => {
  return photos.value.filter(photo => {
    // 标题或描述匹配搜索关键词
    const matchesSearch = searchQuery.value === '' || 
      photo.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (photo.description && photo.description.toLowerCase().includes(searchQuery.value.toLowerCase()));
    
    // 标签匹配选中的标签
    const matchesTags = selectedTags.value.length === 0 || 
      selectedTags.value.some(tag => photo.tags && photo.tags.includes(tag));
    
    return matchesSearch && matchesTags;
  });
});
</script>

<style scoped>
.gallery-container {
  max-width: 1000px;
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

.add-photo-form {
  background: rgba(255, 255, 255, 0.08);
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 30px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.add-photo-form h3 {
  color: #ec4899;
  margin-top: 0;
  margin-bottom: 20px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.photo-uploader {
  width: 100%;
}

.upload-photo-preview {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.upload-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.gallery-filter {
  margin-bottom: 20px;
}

.gallery-filter h3 {
  color: #ec4899;
  margin-bottom: 15px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.filter-controls {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
}

.tag-filter {
  width: 200px;
}

.masonry-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  grid-gap: 15px;
  grid-auto-rows: 0;
}

.gallery-item {
  position: relative;
  overflow: hidden;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.gallery-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.gallery-item:hover .gallery-overlay {
  opacity: 1;
}

.gallery-image {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.gallery-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.gallery-item:hover .gallery-image img {
  transform: scale(1.1);
}

.gallery-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  color: white;
  padding: 15px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.gallery-overlay h4 {
  margin: 0 0 5px;
  font-size: 1.1rem;
}

.gallery-date {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

/* 照片详情弹窗 */
.photo-detail {
  display: flex;
  gap: 20px;
}

.photo-detail-image {
  flex: 2;
  max-height: 70vh;
  overflow: hidden;
  border-radius: 8px;
}

.photo-detail-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.photo-detail-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.photo-detail-date {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.photo-detail-description {
  margin-bottom: 20px;
  line-height: 1.6;
  flex-grow: 1;
}

.photo-detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.photo-tag {
  background: rgba(236, 72, 153, 0.1);
  color: #ec4899;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(236, 72, 153, 0.3);
}

.photo-detail-actions {
  margin-top: auto;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
  }
  
  .tag-filter {
    width: 100%;
  }
  
  .photo-detail {
    flex-direction: column;
  }
  
  .photo-detail-image {
    max-height: 50vh;
  }
}

/* 确保图片网格正确显示 */
@media (min-width: 768px) {
  .masonry-gallery {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .masonry-gallery {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>