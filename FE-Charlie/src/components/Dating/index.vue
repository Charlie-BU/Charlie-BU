<template>
    <div class="dating-container">
        <!-- 左侧导航栏 -->
        <div class="dating-sidebar">
            <div class="dating-logo">
                <img :src="inLoveIcon" alt="In Love Icon" class="in-love-icon" />
                <h3 style="font-family: 'Times New Roman'; font-style: italic;">Charlie & Judy</h3>
            </div>
            <div class="dating-tabs">
                <div v-for="(tab, index) in tabs" :key="index" class="dating-tab-item"
                    :class="{ active: activeTab === tab.name }" @click="handleTabClick(tab.name)">
                    <div class="tab-icon">
                        <img :src="tab.icon" :alt="tab.label + ' Icon'" class="tab-icon-img" />
                    </div>
                    <div class="tab-name">{{ tab.label }}</div>
                </div>
            </div>
        </div>

        <!-- 右侧内容区 -->
        <div class="dating-content">
            <transition name="fade" mode="out-in">
                <component :is="activeComponent"></component>
            </transition>
        </div>

        <!-- 敬请期待弹窗 -->
        <div v-if="showWaitingModal" class="waiting-modal-overlay" @click="closeWaitingModal">
            <div class="waiting-modal" @click.stop>
                <div class="waiting-modal-close" @click="closeWaitingModal">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                
                <div class="waiting-modal-content">
                    <div class="waiting-icon-container">
                        <div class="waiting-icon-bg"></div>
                        <!-- <div class="waiting-icon">🚀</div> -->
                        <img :src="inLoveIcon" alt="In Love Icon" class="waiting-icon" />
                    </div>
                    
                    <h3 class="waiting-title">{{ waitingTitle }}</h3>
                    <p class="waiting-subtitle">{{ waitingMessage }}</p>
                    
                    <div class="waiting-progress">
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <span class="progress-text">开发进度 20%</span>
                    </div>
                                        
                    <button class="waiting-notify-btn" @click="closeWaitingModal">
                        <span>我知道了</span>
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, defineAsyncComponent } from 'vue';

import inLoveIcon from '@/assets/in-love.png';
import activitiesIcon from '@/assets/activities.png';
import anniversaryIcon from '@/assets/anniversary.png';
import galleryIcon from '@/assets/gallery.png';
import diaryIcon from '@/assets/diary.png';
import periodIcon from '@/assets/period.png';

const activityLength = ref(100)
onMounted(async()=>{
    await getActivityLength()
})

// 多语言支持
const LANG = localStorage.getItem("LANG") || "Chinese";
const translations = {
    Chinese: {
        activities: `${activityLength.value}件小事`,
        anniversaryies: "纪念日",
        album: "恋爱相册",
        diary: "心情日记",
        period: "经期记录",
        close: "关闭",
        comingSoon: "敬请期待",
        featureInDevelopment: "功能开发中"
    },
    English: {
        activities: `${activityLength.value} Moments`,
        anniversaryies: "Anniversaries",
        album: "Album",
        diary: "Diary",
        period: "Period Tracker",
        close: "Close",
        comingSoon: "Coming Soon",
        featureInDevelopment: "Feature in Development"
    }
}
// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key
}

// 异步加载子组件
const Activities = defineAsyncComponent(() => import('./Activities.vue'));
const Anniversary = defineAsyncComponent(() => import('./Anniversary.vue'));
const Gallery = defineAsyncComponent(() => import('./Gallery.vue'));
const Diary = defineAsyncComponent(() => import('./Diary.vue'));
const PeriodTracker = defineAsyncComponent(() => import('./PeriodTracker.vue'));

// 弹窗状态管理
const showWaitingModal = ref(false);
const waitingTitle = computed(() => t('comingSoon'));
const waitingMessage = computed(() => t('featureInDevelopment')); 

// 定义标签页
const tabs = [
    { 
        name: 'activities',
        label: t('activities'),
        icon: activitiesIcon,
        component: Activities
    },
    { 
        name: 'anniversary',
        label: t('anniversaryies'),
        icon: anniversaryIcon,
        component: Anniversary 
    },
    { 
        name: 'gallery',
        label: t('album'),
        icon: galleryIcon,
        component: Gallery 
    },
    { 
        name: 'diary',
        label: t('diary'),
        icon: diaryIcon,
        component: Diary 
    },
    { 
        name: 'period',
        label: t('period'),
        icon: periodIcon,
        component: PeriodTracker 
    },
];

const waitList = [
    "anniversary",
    "gallery",
    "diary",
    "period",
]

// 当前激活的标签页
const activeTab = ref('activities');
// 处理标签页点击
const handleTabClick = (tabName) => {
    if (waitList.includes(tabName)) {
        showWaitingModal.value = true;
    } else {
        activeTab.value = tabName;
    }
};

// 关闭弹窗
const closeWaitingModal = () => {
    showWaitingModal.value = false;
};

// 计算当前应该显示的组件
const activeComponent = computed(() => {
    const tab = tabs.find(tab => tab.name === activeTab.value);
    return tab ? tab.component : Activities;
});

const getActivityLength = async () => {
    try {
        const res = await request.post("/dating/get_activity_length");
        activityLength.value = res.data.activity_length
    } catch (error) {
        console.error('Failed to fetch activity length:', error);
        ElMessage.error('获取活动数量失败');
    }
}
</script>

<style scoped>
.dating-container {
    display: flex;
    height: calc(100vh - 60px);
    /* 减去顶部导航栏的高度 */
    color: #f472b6;
    /* 亮粉色文字，适合深色背景 */
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dating-sidebar {
    width: 200px;
    padding: 20px 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 10;
}

.dating-logo {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 30px;
}

.in-love-icon {
    width: 48px;
    height: 48px;
    animation: pulse 1.5s infinite;
}

.dating-logo h3 {
    margin: 10px 0 0;
    font-size: 1.4rem;
    font-weight: 600;
    color: #f472b6;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.dating-tabs {
    width: 100%;
    display: flex;
    flex-direction: column;
}

.dating-tab-item {
    padding: 15px 20px;
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 5px 0;
    border-radius: 0 25px 25px 0;
}

.dating-tab-item:hover {
    background-color: rgba(255, 255, 255, 0.5);
    transform: translateX(5px);
}

.dating-tab-item.active {
    background: rgba(255, 255, 255, 0.08);
    color: #ec4899;
    font-weight: 600;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(236, 72, 153, 0.3);
    box-shadow: 0 4px 12px rgba(236, 72, 153, 0.2);
}

.tab-icon {
    font-size: 1.5rem;
    margin-right: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.tab-icon-img {
    width: 22px;
    height: 22px;
    object-fit: contain;
}

.dating-content {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
    border-radius: 0;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
    transform: translateY(10px);
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }

    100% {
        transform: scale(1);
    }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .dating-container {
        flex-direction: column;
        height: auto;
        min-height: calc(100vh - 60px);
    }

    .dating-sidebar {
        width: 100%;
        padding: 10px 0;
        flex-direction: row;
        justify-content: center;
        overflow-x: auto;
    }

    .dating-logo {
        display: none;
    }

    .dating-tabs {
        flex-direction: row;
        width: auto;
    }

    .dating-tab-item {
        flex-direction: column;
        padding: 10px;
        border-radius: 10px;
        margin: 0 5px;
    }

    .dating-tab-item.active {
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    .tab-icon {
        margin-right: 0;
        margin-bottom: 5px;
    }

    .tab-icon-img {
        width: 20px;
        height: 20px;
    }

    .dating-content {
        padding: 20px;
    }
}

/* 敬请期待弹窗样式 - 现代化设计 */
.waiting-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.6));
    backdrop-filter: blur(12px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: overlayFadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.waiting-modal {
    background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
    border-radius: 24px;
    padding: 0;
    max-width: 480px;
    width: 90%;
    max-height: 90vh;
    overflow: hidden;
    position: relative;
    box-shadow: 
        0 25px 80px rgba(0, 0, 0, 0.15),
        0 10px 30px rgba(0, 0, 0, 0.1),
        0 0 0 1px rgba(255, 255, 255, 0.9),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    animation: modalSlideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
    backdrop-filter: blur(20px);
}

.waiting-modal-close {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    z-index: 10;
    color: #6b7280;
}

.waiting-modal-close:hover {
    background: rgba(0, 0, 0, 0.1);
    transform: scale(1.1);
    color: #374151;
}

.waiting-modal-content {
    padding: 40px 32px 32px;
    text-align: center;
}

.waiting-icon-container {
    position: relative;
    display: inline-block;
    margin-bottom: 24px;
}

.waiting-icon-bg {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, #ff6b9d, #c44569);
    border-radius: 50%;
    opacity: 0.15;
    z-index: 1;
}

.waiting-icon {
    position: relative;
    font-size: 2.5rem;
    z-index: 2;
    animation: iconBgPulse 2.5s ease-in-out infinite;
    width: 50px;
    height: 50px;
}

.waiting-title {
    margin: 0 0 8px 0;
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ec4899, #be185d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.025em;
}

.waiting-subtitle {
    margin: 0 0 32px 0;
    font-size: 1rem;
    color: #6b7280;
    line-height: 1.5;
    font-weight: 400;
}

.waiting-progress {
    margin-bottom: 32px;
}

.progress-bar {
    width: 100%;
    height: 6px;
    background: #f3f4f6;
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-fill {
    height: 100%;
    width: 75%;
    background: linear-gradient(90deg, #ec4899, #f472b6);
    border-radius: 3px;
    position: relative;
    overflow: hidden;
    animation: progressFill 1.5s ease-out 0.3s both;
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    animation: shimmer 2s infinite 1.8s;
}

.progress-text {
    font-size: 0.875rem;
    color: #9ca3af;
    font-weight: 500;
}

.feature-card span {
    font-size: 0.875rem;
    color: #374151;
    font-weight: 500;
    display: block;
}

.waiting-notify-btn {
    background: linear-gradient(135deg, #ec4899, #be185d);
    color: white;
    border: none;
    padding: 16px 32px;
    border-radius: 16px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 14px rgba(236, 72, 153, 0.3);
}

.waiting-notify-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(236, 72, 153, 0.4);
    background: linear-gradient(135deg, #be185d, #9d174d);
}

.waiting-notify-btn:active {
    transform: translateY(0);
    transition: transform 0.1s ease;
}

/* 现代化弹窗动画 */
@keyframes overlayFadeIn {
    from {
        opacity: 0;
        backdrop-filter: blur(0px);
    }
    to {
        opacity: 1;
        backdrop-filter: blur(12px);
    }
}

@keyframes modalSlideUp {
    from {
        opacity: 0;
        transform: translateY(40px) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes iconBgPulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
}

@keyframes iconFloat {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-8px);
    }
}

@keyframes progressFill {
    from {
        width: 0%;
        opacity: 0.5;
    }
    to {
        width: 20%;
        opacity: 1;
    }
}

@keyframes shimmer {
    0% {
        left: -100%;
    }
    100% {
        left: 100%;
    }
}

/* 响应式弹窗设计 */
@media (max-width: 768px) {
    .waiting-modal {
        max-width: 360px;
        margin: 16px;
        border-radius: 20px;
    }
    
    .waiting-modal-content {
        padding: 32px 24px 24px;
    }
    
    .waiting-modal-close {
        top: 16px;
        right: 16px;
        width: 36px;
        height: 36px;
    }
    
    .waiting-icon-bg {
        width: 70px;
        height: 70px;
    }
    
    .waiting-icon {
        font-size: 2rem;
    }
    
    .waiting-title {
        font-size: 1.5rem;
    }
    
    .waiting-subtitle {
        font-size: 0.9rem;
        margin-bottom: 24px;
    }
    
    .waiting-progress {
        margin-bottom: 24px;
    }
    
    .waiting-features {
        grid-template-columns: 1fr;
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .feature-card {
        padding: 16px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        text-align: left;
    }
    
    .feature-icon {
        margin-bottom: 0;
        font-size: 1.25rem;
    }
    
    .waiting-notify-btn {
        padding: 14px 28px;
        border-radius: 14px;
        font-size: 0.95rem;
    }
}
</style>