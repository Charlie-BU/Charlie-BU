<template>
    <el-main class="main-content">
        <section class="activities-section">
            <div class="section-title">
                <h2>{{ t('activities') }} <span class="emoji">🎯</span>
                    <span class="corner-count">{{ t('completed') }} {{activities.filter(item =>
                        item.imageUrl).length}}/{{ activities.length }} {{ t('items') }}</span>
                </h2>
            </div>

            <el-row :gutter="24" class="activities-grid">
                <el-col :xs="24" :sm="12" :md="6" v-for="(activity, index) in activities" :key="index"
                    style="margin-top: 50px;">
                    <el-card class="activity-card" shadow="hover" ref="activityCards">
                        <div class="activity-header">
                            <h3>{{ activity.title }}</h3>
                            <div v-if="activity.date" class="activity-date">{{ formatDateRange(activity.date, null,
                                LANG) }}</div>
                            <div v-else class="activity-date">{{ t("futureDay") }}</div>
                        </div>
                        <p v-if="activity.description" class="activity-description">{{ activity.description }}</p>
                        <p v-else class="activity-description">{{ t("waiting") }}</p>
                        <div class="activity-photos" v-if="activity.imageUrl"
                            :style="{ padding: isMobileRef ? '0 25px' : '0 35px', display: 'flex', justifyContent: 'center', alignItems: 'center', flexWrap: 'wrap' }">
                            <el-image :key="activity.thumb_url" :src="activity.thumb_url" fit="cover"
                                class="activity-photo" lazy @click.stop="openPhotoPreview(activity, 0)"></el-image>
                        </div>
                        <div class="activity-photos" v-else
                            :style="{ padding: isMobileRef ? '0 25px' : '0 35px', display: 'flex', justifyContent: 'center', alignItems: 'center', flexWrap: 'wrap' }">
                            <div class="activity-photo placeholder" @click.stop="openAddModal(activity)">
                                <el-icon :size="48">
                                    <Unlock />
                                </el-icon>
                                <div class="placeholder-text">{{ t('clickToUnlock') }}</div>
                            </div>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </section>

        <!-- 图片预览模态弹框 -->
        <Modal v-model:visible="photoPreviewVisible" type="custom" :title="currentActivity?.title || ''"
            :showCancel="false" :showConfirm="false">
            <div class="photo-preview-container">
                <div class="photo-preview-image-container">
                    <img v-if="currentActivity && currentActivity.imageUrl" :src="currentActivity.imageUrl"
                        class="preview-image" />
                </div>
            </div>
        </Modal>

        <!-- 添加图片/信息表单弹窗 -->
        <Modal v-model:visible="addFormVisible" type="form" :title="currentActivityTitle" :confirm-text="t('unlock')"
            @confirm="handleAddConfirm">
            <template #form>
                <el-form :model="addForm">
                    <el-form-item :label="t('date')">
                        <el-date-picker v-model="addForm.date" type="date" :placeholder="t('datePlaceholder')"
                            format="YYYY/MM/DD" value-format="YYYY-MM-DD" />
                    </el-form-item>
                    <el-form-item :label="t('description')">
                        <el-input v-model="addForm.description" type="textarea" :rows="3"
                            :placeholder="t('descriptionPlaceholder')" />
                    </el-form-item>
                    <el-form-item :label="t('image')">
                        <el-upload class="activity-uploader" action="#" :auto-upload="false"
                            :on-change="handleAddImageChange" :limit="1" list-type="picture-card">
                        </el-upload>
                    </el-form-item>
                </el-form>
            </template>
        </Modal>
    </el-main>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { Unlock } from '@element-plus/icons-vue'
import { request } from '../../api/request'
import { isMobile, formatDateRange, getDate } from '../../utils/utils';
import Modal from '../Modal.vue';

const isMobileRef = ref(isMobile());

// 语言设置
const LANG = localStorage.getItem("LANG") || "Chinese";

// 多语言支持
const translations = {
    Chinese: {
        futureDay: "未来的某天",
        waiting: "待解锁",
        activities: "100 件小事",
        completed: "已完成",
        items: "件",
        date: "日期",
        datePlaceholder: "选择日期",
        description: "留言",
        descriptionPlaceholder: "一些甜蜜瞬间...",
        image: "图片",
        unlock: "解锁",
        cancel: "取消",
        clickToUnlock: "点击解锁",
        pleaseCompleteForm: "请填写完整",
        unlockSuccess: "解锁成功"
    },
    English: {
        futureDay: "Some Day in the Future",
        waiting: "Waiting to Unlock",
        activities: "100 Moments",
        completed: "Completed",
        items: "",
        date: "Date",
        datePlaceholder: "Pick a date",
        description: "Description",
        descriptionPlaceholder: "Some sweet moments...",
        image: "Image",
        unlock: "Unlock",
        cancel: "Cancel",
        clickToUnlock: "Click to Unlock",
        pleaseCompleteForm: "Please complete the form",
        unlockSuccess: "Unlock Success"
    }
}

// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key
}

onMounted(async () => {
    // 获取活动数据
    await getAllActivities();
    // 在下一个tick中设置观察者，确保DOM已经更新
    observeActivityCards();
});

const activities = ref([]);

// 创建一个Map来存储已经观察的元素，避免重复观察
const observedActivities = new Map();
// 存储observer实例，以便在组件卸载时清理
let activityObserver = null;

// 创建Intersection Observer实例
const createObserver = () => {
    const options = {
        root: null, // 使用视口作为根元素
        rootMargin: isMobileRef.value ? '50px' : '0px',
        threshold: 0 // 元素一进入视口立刻触发回调
    };

    return new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // 获取对应的activity数据
                const index = Number(entry.target.dataset.index);
                const activity = activities.value[index];

                if (activity && !observedActivities.get(activity.id)) {
                    // 标记该activity已经被观察过，避免重复请求
                    observedActivities.set(activity.id, true);
                    // 这里可以添加加载图片或其他资源的逻辑
                    // 例如: fetchActivityImages(activity);
                }

                // 停止观察该元素
                observer.unobserve(entry.target);
            }
        });
    }, options);
};

// 观察元素的函数
const observeActivityCards = () => {
    // 如果已经有observer实例，先断开连接
    if (activityObserver) {
        activityObserver.disconnect();
    }
    // 创建新的observer
    activityObserver = createObserver();
    const activityCardElements = document.querySelectorAll('.activity-card');
    activityCardElements.forEach((card, index) => {
        // 为每个card添加索引属性，用于在回调中找到对应的activity数据
        card.dataset.index = index;
        activityObserver.observe(card);
    });
};

// 监听activities数组变化，当有新的活动数据加载时重新设置观察者
watch(() => activities.value.length, async (newLength, oldLength) => {
    if (newLength > oldLength) {
        // 等待DOM更新
        await nextTick();
        // 重新设置观察者
        observeActivityCards();
    }
});

// 图片预览相关
const photoPreviewVisible = ref(false);
const currentActivity = ref(null);
const currentPhotoIndex = ref(0);

// 打开图片预览
const openPhotoPreview = (activity, photoIndex) => {
    currentActivity.value = activity;
    currentPhotoIndex.value = photoIndex;
    photoPreviewVisible.value = true;
    // 添加键盘事件监听
    document.addEventListener('keydown', handleKeyDown);
};

// 关闭图片预览
const closePhotoPreview = () => {
    photoPreviewVisible.value = false;
    // 移除键盘事件监听
    document.removeEventListener('keydown', handleKeyDown);
};

// 处理键盘事件
const handleKeyDown = (event) => {
    if (!photoPreviewVisible.value) return;

    if (event.key === 'Escape') {
        closePhotoPreview();
    }
};

// 组件卸载前移除事件监听和清理observer
onBeforeUnmount(() => {
    document.removeEventListener('keydown', handleKeyDown);

    // 清理Intersection Observer
    if (activityObserver) {
        activityObserver.disconnect();
        activityObserver = null;
    }
});

// 获取活动数据的函数，实际项目中可以从API获取
const getAllActivities = async () => {
    try {
        const res = await request.post("/dating/getAllActivities", {
            lang: LANG,
        });
        activities.value = res.data.activities.map((item) => ({
            ...item,
            thumb_url: item.imageUrl ? `${item.imageUrl}?x-oss-process=image/resize,w_300` : ''
        })) || [];

        // 这里使用的是静态数据，实际项目中应该替换为API调用
        console.log('Activities loaded:', activities.value.length);
    } catch (error) {
        console.error('Failed to fetch activities data:', error);
        ElMessage.error('获取活动数据失败');
    }
};

// 添加图片/信息 - 弹窗与表单
const addFormVisible = ref(false)
const selectedActivity = ref(null)
const addForm = ref({
    date: '',
    description: '',
    imageFile: null,
})

const currentActivityTitle = ref("")
const openAddModal = (activity) => {
    selectedActivity.value = activity
    addForm.value = {
        date: activity.date || '',
        description: activity.description || '',
        imageFile: null,
    }
    currentActivityTitle.value = activity.title
    addFormVisible.value = true
}

const handleAddImageChange = (file) => {
    addForm.value.imageFile = file?.raw || null
}

const handleAddConfirm = async () => {
    if (!addForm.value.date || !addForm.value.description || !addForm.value.imageFile) {
        ElMessage.warning(t('pleaseCompleteForm'))
        return
    }
    // 本地更新，后续可接入后端保存
    const idx = activities.value.findIndex(a => a.id === selectedActivity.value.id)
    if (idx !== -1) {
        const previewUrl = URL.createObjectURL(addForm.value.imageFile)
        const updated = {
            ...activities.value[idx],
            date: addForm.value.date,
            description: addForm.value.description,
            imageUrl: previewUrl,
            thumb_url: previewUrl,
        }
        activities.value.splice(idx, 1, updated)
    }
    addFormVisible.value = false
    ElMessage.success(t('unlockSuccess'))
}

// 计算属性：过滤活动列表
const completedActivities = computed(() => activities.value.filter(item => item.completed));
</script>

<style scoped>
.main-content {
    padding: 2rem;
    max-width: 1500px;
    margin: 0 auto;
}

.section-title {
    margin-bottom: 2rem;
    text-align: center;
}

.section-title h2 {
    font-size: 2rem;
    color: #fff;
    margin: 0;
    padding: 0;
    position: relative;
    display: inline-block;
}

.emoji {
    font-size: 1.8rem;
}

.section-title h2 .corner-count {
    font-size: 0.6em;
    font-weight: 400;
    font-style: italic;
    margin-left: 5px;
    vertical-align: middle;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #c084fc, #e9d5ff);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 0px 8px rgba(192, 132, 252, 0.5);
}

.section-title h2::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #8E2DE2, #4A00E0);
    border-radius: 3px;
}

.activities-section {
    margin-bottom: 4rem;
}

.activities-grid {
    margin-top: -30px;
}

.activity-card {
    height: 100%;
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 12px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
    color: #fff;
    max-height: 350px;
    overflow: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
}

.activity-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
}

.activity-header {
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.activity-header h3 {
    margin: 0;
    font-size: 1.5rem;
    color: #fff;
}

.activity-date {
    font-size: 0.9rem;
    color: #a78bfa;
}

.activity-description {
    margin-bottom: 1rem;
    color: rgba(255, 255, 255, 0.8);
}

.activity-photos {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 1rem;
}

.activity-photo {
    width: 120px;
    height: 120px;
    border-radius: 8px;
    object-fit: cover;
    cursor: pointer;
    transition: transform 0.2s ease;
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

.activity-photo:hover {
    transform: scale(1.05);
}

.activity-photo.placeholder {
    display: flex;
    justify-content: center;
    align-items: center;
    border: 2px dashed rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.05);
    color: #fff;
    flex-direction: column;
    gap: 8px;
}

.placeholder-text {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
}

/* 图片预览样式 */
.photo-preview-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

.photo-preview-image-container {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 20px;
}

.preview-image {
    max-width: 100%;
    max-height: 70vh;
    object-fit: contain;
    border-radius: 8px;
}

.photo-preview-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 20px;
}

.preview-nav-button {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.preview-nav-button:hover {
    background: rgba(255, 255, 255, 0.2);
}

.preview-nav-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.photo-preview-counter {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
}

/* 使添加图片上传区域背景透明 */
.activity-uploader :deep(.el-upload--picture-card) {
    background-color: transparent;
}

.activity-uploader :deep(.el-upload-list__item) {
    background-color: transparent;
}

.activity-uploader :deep(.el-upload-list__item-thumbnail) {
    background-color: transparent;
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