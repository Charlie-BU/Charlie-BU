<template>
    <el-main class="main-content">
        <section class="activities-section">
            <div class="section-title">
                <h2>100 件小事 <span class="emoji">🎯</span>
                    <span class="corner-count">已完成 {{ completedActivities.length }}/{{ activities.length }} 件</span>
                </h2>
            </div>
            <!-- 添加新活动表单 -->
            <!-- <div class="add-activity-form">
            <h3>添加新活动</h3>
            <el-form :model="newActivity" label-position="top">
                <el-form-item label="活动名称">
                    <el-input v-model="newActivity.title" placeholder="例如：一起去看电影"></el-input>
                </el-form-item>

                <el-form-item label="活动描述">
                    <el-input v-model="newActivity.description" type="textarea" placeholder="描述一下这个活动..."
                        :rows="3"></el-input>
                </el-form-item>

                <el-form-item label="活动日期">
                    <el-date-picker v-model="newActivity.date" type="date" placeholder="选择日期" format="YYYY/MM/DD"
                        value-format="YYYY-MM-DD"></el-date-picker>
                </el-form-item>

                <el-form-item label="活动图片">
                    <el-upload class="activity-uploader" action="#" :auto-upload="false" :on-change="handleImageChange"
                        :limit="1" list-type="picture-card">
                        <el-icon>
                            <Plus />
                        </el-icon>
                        <template #file="{ file }">
                            <div class="upload-image-preview">
                                <img class="upload-image" :src="file.url" alt="活动图片" />
                            </div>
                        </template>
</el-upload>
</el-form-item>

<el-form-item label="完成状态">
    <el-switch v-model="newActivity.completed" active-text="已完成" inactive-text="计划中" inline-prompt></el-switch>
</el-form-item>

<el-form-item>
    <el-button type="primary" @click="addActivity" :disabled="!newActivity.title">
        <el-icon>
            <Plus />
        </el-icon> 添加活动
    </el-button>
</el-form-item>
</el-form>
</div> -->

            <el-row :gutter="24" class="activities-grid">
                <el-col :xs="24" :sm="12" :md="6" v-for="(activity, index) in activities" :key="index"
                    style="margin-top: 50px;">
                    <el-card class="activity-card" shadow="hover" @click.stop="showActivityDetails(activity)"
                        ref="activityCards">
                        <div class="activity-header">
                            <h3>{{ activity.title }}</h3>
                            <div class="activity-date">{{ formatDateRange(activity.date, null, LANG) }}</div>
                        </div>
                        <p class="activity-description">{{ activity.description }}</p>
                        <div class="activity-photos" v-if="activity.image"
                            :style="{ padding: isMobileRef ? '0 25px' : '0 35px', display: 'flex', justifyContent: 'center', alignItems: 'center', flexWrap: 'wrap' }">
                            <el-image :key="activity.image" :src="activity.image" fit="cover" class="activity-photo"
                                lazy @click.stop="openPhotoPreview(activity, 0)"></el-image>
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
                    <img v-if="currentActivity && currentActivity.image" :src="currentActivity.image"
                        class="preview-image" />
                </div>
            </div>
        </Modal>
    </el-main>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { Plus, ArrowLeft, ArrowRight } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { isMobile, formatDateRange, getDate } from '../../utils/utils';
import Modal from '../Modal.vue';

const isMobileRef = ref(isMobile());

// 语言设置
const LANG = localStorage.getItem("LANG") || "Chinese";

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

onMounted(() => {
    // 获取活动数据
    fetchActivities();

    // 在下一个tick中设置观察者，确保DOM已经更新
    setTimeout(() => {
        observeActivityCards();
    }, 100);
});

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
    },
    {
        id: 4,
        title: '一起去爬山',
        description: '登上山顶，俯瞰城市美景',
        date: '2024-01-15',
        image: 'https://picsum.photos/id/29/800/400',
        completed: false
    },
    {
        id: 5,
        title: '去海边度假',
        description: '享受阳光、沙滩和海浪',
        date: '2024-02-10',
        image: 'https://picsum.photos/id/42/800/400',
        completed: false
    },
    {
        id: 6,
        title: '一起学做甜点',
        description: '尝试制作马卡龙和提拉米苏',
        date: '2024-03-05',
        image: 'https://picsum.photos/id/431/800/400',
        completed: false
    }
]);

// 监听activities数组变化，当有新的活动数据加载时重新设置观察者
watch(() => activities.value.length, async (newLength, oldLength) => {
    if (newLength > oldLength) {
        // 等待DOM更新
        await nextTick();
        // 重新设置观察者
        observeActivityCards();
    }
});

// 显示活动详情
const showActivityDetails = (activity) => {
    console.log('Activity details:', activity);
    // 这里可以添加显示详情的逻辑，比如打开一个对话框
};

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
const fetchActivities = async () => {
    try {
        // 模拟API请求
        // const response = await request.post("/api/dating/getActivities", {
        //     lang: LANG,
        // });
        // activities.value = response.data.activities || [];

        // 这里使用的是静态数据，实际项目中应该替换为API调用
        console.log('Activities loaded:', activities.value.length);
    } catch (error) {
        console.error('Failed to fetch activities data:', error);
        ElMessage.error('获取活动数据失败');
    }
};

// 计算属性：过滤活动列表
const allActivities = computed(() => activities.value);
const completedActivities = computed(() => activities.value.filter(item => item.completed));
const plannedActivities = computed(() => activities.value.filter(item => !item.completed));
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