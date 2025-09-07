<template>
    <div class="dating-container">
        <!-- 左侧导航栏 -->
        <div class="dating-sidebar">
            <div class="dating-logo">
                <div class="heart-icon">❤️</div>
                <h3>甜蜜空间</h3>
            </div>
            <div class="dating-tabs">
                <div v-for="(tab, index) in tabs" :key="index" class="dating-tab-item"
                    :class="{ active: activeTab === tab.name }" @click="activeTab = tab.name">
                    <div class="tab-icon">{{ tab.icon }}</div>
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
    </div>
</template>

<script setup>
import { ref, computed, defineAsyncComponent } from 'vue';

// 异步加载子组件
const Activities = defineAsyncComponent(() => import('./Activities.vue'));
const Anniversary = defineAsyncComponent(() => import('./Anniversary.vue'));
const Gallery = defineAsyncComponent(() => import('./Gallery.vue'));
const Diary = defineAsyncComponent(() => import('./Diary.vue'));
const PeriodTracker = defineAsyncComponent(() => import('./PeriodTracker.vue'));

// 定义标签页
const tabs = [
    { name: 'activities', label: '一起做的事', icon: '🎯', component: Activities },
    { name: 'anniversary', label: '纪念日', icon: '🎂', component: Anniversary },
    { name: 'gallery', label: '恋爱相册', icon: '📷', component: Gallery },
    { name: 'diary', label: '心情日记', icon: '📝', component: Diary },
    { name: 'period', label: '经期记录', icon: '📅', component: PeriodTracker },
];

// 当前激活的标签页
const activeTab = ref('activities');

// 计算当前应该显示的组件
const activeComponent = computed(() => {
    const tab = tabs.find(tab => tab.name === activeTab.value);
    return tab ? tab.component : null;
});
</script>

<style scoped>
.dating-container {
    display: flex;
    height: calc(100vh - 60px);
    /* 减去顶部导航栏的高度 */
    color: #831843;
    /* 深粉色文字 */
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

.heart-icon {
    font-size: 32px;
    animation: pulse 1.5s infinite;
}

.dating-logo h3 {
    margin: 10px 0 0;
    font-size: 1.4rem;
    font-weight: 600;
    color: #831843;
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
    color: #be185d;
    font-weight: 600;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tab-icon {
    font-size: 1.5rem;
    margin-right: 12px;
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

    .dating-content {
        padding: 20px;
    }
}
</style>