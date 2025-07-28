<template>
    <el-main class="main-content" :style="{ 'padding': isMobileRef ? '40px 60px' : '40px 20px' }">
        <!-- 英雄区域 -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">
                    <span class="gradient-text">Hey, I'm Charlie</span>
                </h1>
                <p class="hero-subtitle section-title-container" @mouseenter="handle_mouse_enter('description')"
                    @mouseleave="handle_mouse_leave('description')">
                    {{ charlie.description }}
                    <el-button v-if="admin_id && hover_module === 'description'" class="add-button" size="small"
                        type="primary" icon="EditPen">修改</el-button>
                </p>
                <div class="hero-buttons">
                    <el-button type="primary" size="large" class="cta-button" @click="download_cv">
                        <el-icon class="button-icon">
                            <Star />
                        </el-icon>
                        {{ t('CV') }}
                    </el-button>
                    <el-button size="large" class="secondary-button" @click="email_me">
                        <el-icon class="button-icon">
                            <Message />
                        </el-icon>
                        {{ t('contactMe') }}
                    </el-button>
                </div>
            </div>
            <div class="hero-avatar" :style="{ 'margin-top': isMobileRef ? '100px' : '' }">
                <div class="avatar-container">
                    <div class="glass-sphere-glow"></div>
                    <div class="glass-sphere">
                        <div v-if="LANG === 'English'" class="chat-bubble">
                            Hi there my No. {{ charlie.visitorNumber }} visitor!
                        </div>
                        <div v-else class="chat-bubble">
                            欢迎我的第 {{ charlie.visitorNumber }} 位参观者！
                        </div>
                        <div class="glass-sphere-inner">
                            <div class="glass-sphere-reflection"></div>
                            <div class="glass-sphere-reflection secondary"></div>
                            <el-avatar :size="180" class="main-avatar">
                                <img src="../assets/charlie.jpg" alt="Charlie" />
                                <!-- <el-icon>
                                    <User />
                                </el-icon> -->
                            </el-avatar>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="features-section">
            <div class="section-title section-title-container" @mouseenter="handle_mouse_enter('talents')"
                @mouseleave="handle_mouse_leave('talents')">
                <h2>{{ t('aboutMe') }}</h2>
                <el-button v-if="admin_id && hover_module === 'talents'" class="add-button" size="small" type="primary"
                    icon="Plus">添加</el-button>
            </div>
            <el-row :gutter="24" class="features-grid">
                <el-col :xs="24" :sm="12" :md="8" v-for="(talent, index) in talents" :key="index">
                    <el-card class="feature-card" shadow="hover" @click="goto_page(talent.gotoUrl)"
                        :style="{ 'cursor': talent.gotoUrl ? 'pointer' : 'default', '--before-opacity': talent.gotoUrl ? '1' : '0', 'padding': talent.gotoUrl ? '30px 20px 60px 20px' : '30px 20px' }"
                        @contextmenu.prevent="(e) => handle_right_click(e, talent, 'talent')"
                        @mouseenter="talent.showDetails = true" @mouseleave="talent.showDetails = false">
                        <div class="feature-icon">
                            <el-icon :size="40">
                                <component :is="talent.icon" />
                            </el-icon>
                        </div>
                        <h3>{{ talent.title }}</h3>
                        <p style="text-align: justify;">{{ talent.description }}</p>
                        <div v-if="talent.gotoUrl" class="view-details"
                            :style="{ color: talent.showDetails ? '#ffffff' : '#A78BFA' }">
                            <span :class="{ 'show': talent.showDetails }">{{ t('detail') }}&nbsp;</span>
                            <el-icon style="vertical-align: middle">
                                <right />
                            </el-icon>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </section>

        <section style="margin-top: 120px;">
            <div class="section-title section-title-container" @mouseenter="handle_mouse_enter('achievements')"
                @mouseleave="handle_mouse_leave('achievements')">
                <h2>{{ t('myAchievements') }}</h2>
                <el-button v-if="admin_id && hover_module === 'achievements'" class="add-button" size="small"
                    type="primary" icon="Plus">添加</el-button>
            </div>
            <el-row class="stats-section" :gutter="24">
                <el-col :xs="12" :sm="6" v-for="(achievement, index) in achievements" :key="index">
                    <div class="stat-item"
                        @contextmenu.prevent="(e) => handle_right_click(e, achievement, 'achievement')">
                        <div class="stat-number">{{ achievement.number }}</div>
                        <div class="stat-label">{{ achievement.label }}</div>
                    </div>
                </el-col>
            </el-row>
        </section>

        <section style="margin-top: 120px;">
            <div class="section-title section-title-container" @mouseenter="handle_mouse_enter('growthPath')"
                @mouseleave="handle_mouse_leave('growthPath')">
                <h2>{{ t('growthPath') }}</h2>
                <el-button v-if="admin_id && hover_module === 'growthPath'" class="add-button" size="small"
                    type="primary" icon="Plus">添加</el-button>
            </div>
            <el-timeline style="max-width: 600px; margin: auto;">
                <el-timeline-item v-for="(item, index) in growthTimelines" :key="index" :timestamp="item.timestamp"
                    placement="top">
                    <div class="timeline-content"
                        @contextmenu.prevent="(e) => handle_right_click(e, item, 'growthTimeline')">
                        {{ item.content }}
                    </div>
                </el-timeline-item>
            </el-timeline>
        </section>

        <section style="margin-top: 120px;">
            <div class="section-title section-title-container" @mouseenter="handle_mouse_enter('thoughts')"
                @mouseleave="handle_mouse_leave('thoughts')">
                <h2>{{ t('thoughts') }}</h2>
                <el-button v-if="admin_id && hover_module === 'thoughts'" class="add-button" size="small" type="primary"
                    icon="Plus">添加</el-button>
            </div>
            <div class="thoughts-container">
                <el-card v-for="(bubble, index) in bubbles" :key="index" class="thought-card" shadow="hover">
                    <div @contextmenu.prevent="(e) => handle_right_click(e, bubble, 'bubble')">
                        <div class="thought-header">
                            <div class="thought-date">
                                <el-icon>
                                    <Calendar />
                                </el-icon>
                                <span>{{ bubble.date }}</span>
                            </div>
                            <div class="thought-tags">
                                <el-tag v-for="(tag, tagIndex) in bubble.tags" :key="tagIndex" size="small"
                                    effect="dark" class="thought-tag">
                                    {{ tag }}
                                </el-tag>
                            </div>
                        </div>
                        <div class="thought-content">
                            <el-icon class="quote-icon">
                                <ChatDotRound />
                            </el-icon>
                            <p style="text-align: justify;">{{ bubble.content }}</p>
                        </div>
                    </div>
                </el-card>
            </div>
        </section>

        <section style="margin-top: 120px; text-align: center;">
            <div class="section-title section-title-container" @mouseenter="handle_mouse_enter('selfDefinition')"
                @mouseleave="handle_mouse_leave('selfDefinition')">
                <h2>{{ t('selfDefinition') }}</h2>
                <el-button v-if="admin_id && hover_module === 'selfDefinition'" class="add-button" size="small"
                    type="primary" icon="Plus">添加</el-button>
            </div>
            <blockquote
                style="font-style: italic; color: rgba(255,255,255,0.8); max-width: 600px; margin: auto; font-size: 1.2rem;"
                @contextmenu.prevent="(e) => handle_right_click(e, charlie.motto, 'motto')">
                {{ charlie.motto }}
            </blockquote>
        </section>
    </el-main>

    <div v-if="showContextMenu" class="context-menu" :style="{ top: contextMenuY + 'px', left: contextMenuX + 'px' }">
        <div class="context-menu-item delete-item" @click="handle_delete">
            <el-icon>
                <Delete />
            </el-icon>
            <span>删除</span>
        </div>
    </div>

    <Modal v-model:visible="deleteDialogVisible" type="delete" title="确认删除" content="确定要删除此项吗？"
        @confirm="confirm_delete" @cancel="cancel_delete" />

</template>

<script setup>
import { ref, onMounted, reactive, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus';
import Cookies from 'js-cookie';

import { request } from '../api/request'
import { isMobile } from '../utils/utils';
import Modal from './Modal.vue'

const isMobileRef = ref(isMobile());
const LANG = localStorage.getItem("LANG") || "Chinese";
const translations = reactive({
    Chinese: {
        CV: '我的简历',
        contactMe: '与我交流',
        aboutMe: '关于我',
        detail: '查看详情',
        myAchievements: '我的成就',
        growthPath: '成长轨迹',
        thoughts: '碎碎念',
        selfDefinition: '一句话自我定义',
        CV_not_finished: '简历信息暂未完善',
    },
    English: {
        CV: 'My CV',
        contactMe: 'Contact Me',
        aboutMe: 'About Me',
        detail: 'Detail',
        myAchievements: 'My Achievements',
        growthPath: 'Growth Path',
        thoughts: 'Thoughts',
        selfDefinition: 'Self Definition',
        CV_not_finished: 'CV hasn\'t yet been finished',
    }
})
// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key
}

onMounted(async () => {
    await Promise.all([get_charlie(LANG), get_talents(LANG), get_achievements(LANG), get_growthTimeline(LANG), get_bubbles(LANG)]);
    if (Cookies.get('sessionid')) {
        await check_sessionid();
    }
})

const admin_id = ref(false);
const check_sessionid = async () => {
    try {
        const res = await request.post('/api/check_sessionid', {
            sessionid: Cookies.get('sessionid')
        });
        if (res.data.status !== 200) {
            return;
        }
        admin_id.value = res.data.admin_id;
    } catch (error) {
        console.log(error)
    }
}

// 个人信息
const charlie = ref({});
const get_charlie = async (lang) => {
    try {
        const res = await request.post('/api/get_charlie', {
            lang,
        });
        if (res.data.status !== 200) {
            ElMessage(res.data.message)
            console.log(res.data.message)
            return;
        }
        charlie.value = res.data.charlie;
    } catch (error) {
        ElMessage(error)
        console.log(error)
    }
}

// 我的专长
const talents = ref([])
const get_talents = async (lang) => {
    try {
        const res = await request.post('/api/get_talents', {
            lang
        });
        if (res.data.status !== 200) {
            ElMessage(res.data.message)
            console.log(res.data.message)
            return;
        }
        talents.value = res.data.talents;
    } catch (error) {
        ElMessage(error)
        console.log(error)
    }
}

const goto_page = (url) => {
    if (!url) {
        return;
    }
    window.open(url, '_blank')
}

// 我的成就
const achievements = ref([])
const get_achievements = async (lang) => {
    try {
        const res = await request.post('/api/get_achievements', {
            lang
        });
        if (res.data.status !== 200) {
            ElMessage(res.data.message)
            console.log(res.data.message)
            return;
        }
        achievements.value = res.data.achievements;
    } catch (error) {
        ElMessage(error)
        console.log(error)
    }
}

// 成长轨迹
const growthTimelines = ref([])
const get_growthTimeline = async (lang) => {
    try {
        const res = await request.post('/api/get_growthTimeline', {
            lang
        });
        if (res.data.status !== 200) {
            ElMessage(res.data.message)
            console.log(res.data.message)
            return;
        }
        growthTimelines.value = res.data.growthTimelines;
    } catch (error) {
        ElMessage(error)
        console.log(error)
    }
}

// 碎碎念
const bubbles = ref([])
const get_bubbles = async (lang) => {
    try {
        const res = await request.post('/api/get_bubbles', {
            lang
        });
        if (res.data.status !== 200) {
            ElMessage(res.data.message)
            console.log(res.data.message)
            return;
        }
        bubbles.value = res.data.bubbles;
    } catch (error) {
        ElMessage(error)
        console.log(error)
    }
}

const download_cv = () => {
    if (!charlie?.value?.resume) {
        ElMessage(t("CV_not_finished"))
        return;
    }
    window.location.href = charlie.value.resume;
}

const email_me = () => {
    if (!charlie?.value?.email) {
        ElMessage("请稍后再试")
        return;
    }
    window.location.href = `mailto:${charlie.value.email}`
}

// admin 管理功能
const hover_module = ref('');
const handle_mouse_enter = (module) => {
    if (!admin_id.value) return;
    hover_module.value = module;
}
const handle_mouse_leave = (module) => {
    if (!admin_id.value) return;
    hover_module.value = '';
}

// 右键菜单相关
const showContextMenu = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);
const currentItem = ref(null);
const deleteDialogVisible = ref(false);

// 处理右键点击
const handle_right_click = (event, item, type) => {
    if (!admin_id.value) return;
    event.preventDefault();

    // 保存当前项目信息
    currentItem.value = {
        item,
        type
    };

    // 设置右键菜单位置
    contextMenuX.value = event.clientX;
    contextMenuY.value = event.clientY;
    showContextMenu.value = true;

    // 添加点击其他地方关闭菜单的事件
    setTimeout(() => {
        document.addEventListener('click', close_context_menu);
    }, 0);
};

// 关闭右键菜单
const close_context_menu = () => {
    showContextMenu.value = false;
    document.removeEventListener('click', close_context_menu);
};

// 处理删除按钮点击
const handle_delete = () => {
    close_context_menu();
    deleteDialogVisible.value = true;
};

// 取消删除
const cancel_delete = () => {
    deleteDialogVisible.value = false;
    currentItem.value = null;
};

// 确认删除
const confirm_delete = async () => {
    if (!currentItem.value) return;

    try {

        const res = await request.post(`/api/delete_${currentItem.value.type}`, {
            id: currentItem.value.item.id
        });
        if (res.data.status !== 200) {
            ElMessage(res.data.message)
            console.log(res.data.message)
            return;
        }
        ElMessage.success("删除成功");

        // 根据类型刷新对应的数据
        if (currentItem.value.type === 'talent') await get_talents(LANG);
        else if (currentItem.value.type === 'achievement') await get_achievements(LANG);
        else if (currentItem.value.type === 'growthTimeline') await get_growthTimeline(LANG);
        else if (currentItem.value.type === 'bubble') await get_bubbles(LANG);
        else if (currentItem.value.type === 'motto') await get_charlie(LANG);

    } catch (error) {
        ElMessage.error('删除失败: ' + error.message);
    }
};

// 组件卸载前移除事件监听
onBeforeUnmount(() => {
    document.removeEventListener('click', close_context_menu);
});
</script>

<style scoped>
.main-content {
    max-width: 1200px;
    margin: 0 auto;
    overflow: visible;
}

/* 英雄区域 */
.hero-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 70vh;
    margin-bottom: 80px;
}

.hero-content {
    flex: 1;
    max-width: 600px;
    text-align: left;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 20px;
    line-height: 1.2;
}

.gradient-text {
    background: linear-gradient(45deg, #e674f5, #0e8add, #F59E0B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 3s ease-in-out infinite;
}

@keyframes gradient-shift {

    0%,
    100% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }
}

.hero-subtitle {
    position: relative;
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.95);
    margin-bottom: 30px;
    line-height: 1.6;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    font-weight: bold;
    padding-right: 40px;
    /* 为按钮预留空间 */
}

.hero-subtitle .add-button {
    top: 10%;
    right: -15px;
    transform: scale(0.8);
    height: 50px;
    width: 50px;
}

.hero-subtitle:hover .add-button {
    opacity: 1;
    transform: scale(1);
}

.hero-subtitle .add-button:hover {
    transform: scale(1.1);
}

.hero-subtitle .add-button:active {
    transform: scale(0.95);
}

.hero-buttons {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

.cta-button {
    background: linear-gradient(45deg, #8B5CF6, #EC4899);
    border: none;
    padding: 12px 24px;
    font-weight: 600;
    border-radius: 20px;
    transition: all 0.3s ease;
}

.hero-buttons .button-icon {
    margin-right: 5px;
}

.cta-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(139, 92, 246, 0.4);
}

.secondary-button {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(10px);
    padding: 12px 24px;
    font-weight: 600;
    border-radius: 20px;
    transition: all 0.3s ease;
}

.secondary-button:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}

/* 头像区域 */
.hero-avatar {
    flex: 0 0 auto;
    margin-right: 100px;
    perspective: 1000px;
}

.avatar-container {
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    transform-style: preserve-3d;
    width: 240px;
    height: 240px;
}

.glass-sphere-glow {
    position: absolute;
    width: 240px;
    height: 240px;
    border-radius: 50%;
    filter: blur(5px);
    opacity: 0.7;
    z-index: 0;
    animation: rotate 15s linear infinite, pulse 3s ease-in-out infinite;
}

@keyframes pulse {

    0%,
    100% {
        transform: scale(1);
        opacity: 0.7;
    }

    50% {
        transform: scale(1.1);
        opacity: 0.9;
    }
}

/* 聊天气泡样式 */
.chat-bubble {
    white-space: nowrap;
    position: absolute;
    top: -50px;
    left: 100px;
    background: linear-gradient(135deg, #8B5CF6, #EC4899);
    color: white;
    padding: 12px 16px;
    /* 增加内边距 */
    border-radius: 24px;
    /* 增加圆角 */
    font-size: 16px;
    /* 增加字体大小 */
    font-weight: 700;
    /* 加粗字体 */
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    z-index: 10;
    /* 增加最大宽度 */
    text-align: center;
    animation: bubble-pop 0.5s ease-out, bubble-float 3s ease-in-out infinite;
    transform-origin: bottom left;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
    /* 添加文字阴影 */
    letter-spacing: 0.5px;
    /* 增加字母间距 */
    /* 添加文字渐变效果 */
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    background-image: linear-gradient(to right, #fff, #f0f0f0, #fff);
    animation: text-shine 3s linear infinite, bubble-pop 0.5s ease-out, bubble-float 3s ease-in-out infinite;
}

/* 添加文字闪光动画 */
@keyframes text-shine {
    0% {
        background-position: 0%;
    }

    100% {
        background-position: 200%;
    }
}

.chat-bubble::after {
    content: '';
    position: absolute;
    bottom: -9px;
    /* 调整小尾巴位置 */
    left: 23px;
    width: 15px;
    /* 增加小尾巴大小 */
    height: 15px;
    background: inherit;
    transform: rotate(45deg);
    border-bottom: 1px solid rgba(255, 255, 255, 0.3);
    border-right: 1px solid rgba(255, 255, 255, 0.3);
}


@keyframes bubble-pop {
    0% {
        transform: scale(0);
        opacity: 0;
    }

    50% {
        transform: scale(1.2);
    }

    100% {
        transform: scale(1);
        opacity: 1;
    }
}

@keyframes bubble-float {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-5px);
    }
}

.glass-sphere {
    position: relative;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.1),
            rgba(255, 255, 255, 0.05) 40%,
            rgba(255, 255, 255, 0.02) 100%);
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 0 30px rgba(255, 255, 255, 0.1),
        inset 0 0 20px rgba(255, 255, 255, 0.08);
    overflow: visible;
    /* 修改为visible以便气泡可以超出边界 */
    transform-style: preserve-3d;
    animation: float 6s ease-in-out infinite;
    z-index: 1;
}

.glass-sphere-inner {
    position: absolute;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    transform-style: preserve-3d;
    /* 旋转 */
    /* animation: inner-rotate 20s linear infinite; */
}

.glass-sphere-reflection {
    position: absolute;
    width: 80px;
    height: 30px;
    background: rgba(255, 255, 255, 0.25);
    border-radius: 50%;
    filter: blur(3px);
    top: 40px;
    left: 40px;
    transform: rotate(-30deg);
}

.glass-sphere-reflection.secondary {
    width: 40px;
    height: 15px;
    top: 80px;
    left: 140px;
    background: rgba(255, 255, 255, 0.15);
    transform: rotate(20deg);
}

.main-avatar {
    background: linear-gradient(45deg, #8B5CF6, #EC4899);
    color: white;
    font-size: 70px;
    position: relative;
    z-index: 2;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    transform: translateZ(10px);
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0) rotateX(5deg) rotateY(5deg);
    }

    50% {
        transform: translateY(-15px) rotateX(-5deg) rotateY(-5deg);
    }
}

@keyframes inner-rotate {
    0% {
        transform: rotateY(0deg);
    }

    100% {
        transform: rotateY(360deg);
    }
}

@keyframes rotate {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

@keyframes pulse {

    0%,
    100% {
        transform: scale(1);
        opacity: 0.7;
    }

    50% {
        transform: scale(1.1);
        opacity: 0.9;
    }
}

/* 特色区域 */
.features-section {
    margin-bottom: 80px;
}

.section-title {
    text-align: center;
    margin-bottom: 50px;
    position: relative;
    display: inline-block;
}

.section-title h2 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.features-grid {
    margin-top: 40px;
    row-gap: 30px;
}

.feature-card {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 16px;
    text-align: center;
    transition: all 0.3s ease;
    height: 100%;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    position: relative;
    overflow: hidden;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 16px;
    border: 1px solid transparent;
    /* 将边框从2px改为1px，使线条更细 */
    /* 初始透明边框 */
    /* 改为高亮的白色 */
    background: #00FFFF border-box;
    mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
    -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: destination-out;
    mask-composite: exclude;
    opacity: 0;
    /* 初始不可见 */
    transition: opacity 0.3s ease;
    /* 添加过渡效果 */
    pointer-events: none;
    /* 确保不会影响鼠标事件 */
}

.feature-card:hover::before {
    opacity: var(--before-opacity);
}

.feature-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(139, 92, 246, 0.3), 0 8px 16px rgba(0, 0, 0, 0.2);
    background: rgba(255, 255, 255, 0.18);
}

.feature-icon {
    margin-bottom: 20px;
    color: #A78BFA;
    font-size: 1.2em;
    filter: drop-shadow(0 0 8px rgba(167, 139, 250, 0.5));
}

.feature-card h3 {
    color: #ffffff;
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 15px;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.feature-card p {
    color: rgba(255, 255, 255, 0.92);
    line-height: 1.6;
    margin: 0;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 统计数据区域 */
.stats-section {
    margin-bottom: 60px;
    padding: 40px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    text-align: center;
}


.stat-item {
    text-align: center;
    padding: 20px;
    overflow: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 800;
    color: #8B5CF6;
    margin-bottom: 8px;
    white-space: nowrap;
}

.stat-label {
    color: rgba(255, 255, 255, 0.92);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.9rem;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .hero-section {
        flex-direction: column;
        text-align: center;
        gap: 40px;
    }

    .hero-avatar {
        margin-left: 0;
    }

    .hero-title {
        font-size: 2.5rem;
    }

    .hero-buttons {
        justify-content: center;
    }
}

/* 成长轨迹样式 */
.el-timeline {
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-timeline-item__node) {
    background-color: #8B5CF6;
    border-color: #8B5CF6;
}

:deep(.el-timeline-item__tail) {
    border-left-color: rgba(139, 92, 246, 0.3);
}

:deep(.el-timeline-item__timestamp) {
    color: #A78BFA;
    font-weight: 700;
    font-size: 1.1rem;
}

:deep(.el-timeline-item__content) {
    color: rgba(255, 255, 255, 0.92);
    font-size: 1rem;
    padding: 10px 0;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

:deep(.el-timeline-item:hover .el-timeline-item__content) {
    transform: translateX(5px);
    transition: transform 0.3s ease;
}

:deep(.el-timeline-item:hover .el-timeline-item__node) {
    transform: scale(1.2);
    box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
    transition: all 0.3s ease;
}

/* 碎碎念样式 */
.thoughts-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    max-width: 1000px;
    margin: 0 auto;
}

.thought-card {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 16px;
    overflow: hidden;
    transition: all 0.3s ease;
    height: 100%;
}

.thought-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(139, 92, 246, 0.3), 0 8px 16px rgba(0, 0, 0, 0.2);
    background: rgba(255, 255, 255, 0.18);
}

.thought-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.thought-date {
    display: flex;
    align-items: center;
    gap: 5px;
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.9rem;
}

.thought-tags {
    display: flex;
    gap: 5px;
    flex-wrap: wrap;
}

.thought-tag {
    background: rgba(139, 92, 246, 0.3);
    border-color: rgba(139, 92, 246, 0.5);
    color: #A78BFA;
}

.thought-content {
    position: relative;
    padding: 10px 5px 5px 25px;
    color: rgba(255, 255, 255, 0.92);
    line-height: 1.6;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.quote-icon {
    position: absolute;
    left: 0;
    top: 10px;
    color: rgba(139, 92, 246, 0.5);
    font-size: 1.2rem;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .thoughts-container {
        grid-template-columns: 1fr;
    }
}

/* 查看详情按钮样式 */
.view-details {
    position: absolute;
    bottom: 30px;
    left: 0;
    right: 0;
    align-items: center;
    justify-content: center;
    color: #A78BFA;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s ease;
}


.view-details span {
    max-width: 0;
    overflow: hidden;
    margin-right: 0;
}

.section-title-container {
    position: relative;
}

.add-button {
    position: absolute;
    top: -15px;
    right: -20px;
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    transform: scale(0.8);
    z-index: 10;
    border-radius: 50%;
    padding: 8px;
    height: 50px;
    width: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #8B5CF6, #EC4899);
    border: 2px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.5), 0 8px 25px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.add-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0));
    opacity: 0;
    transition: opacity 0.3s ease;
}

.section-title:hover .add-button {
    opacity: 1;
    transform: scale(1) translateY(0);
}


.add-button:hover::before {
    opacity: 1;
}

.section-title-container .add-button:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6), 0 10px 30px rgba(0, 0, 0, 0.15);
}

.section-title-container .add-button:active {
    transform: scale(0.95);
    box-shadow: 0 2px 10px rgba(139, 92, 246, 0.4);
}

.context-menu {
    position: fixed;
    z-index: 1000;
    backdrop-filter: blur(10px);
    border-radius: 8px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1);
    padding: 8px 0;
    min-width: 120px;
    animation: menu-fade-in 0.2s ease-out;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes menu-fade-in {
    from {
        opacity: 0;
        transform: scale(0.95);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

.context-menu-item {
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: rgba(255, 255, 255, 0.9);
    cursor: pointer;
    transition: all 0.2s ease;
}

.context-menu-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

.delete-item {
    color: #f56c6c;
}

.delete-item:hover {
    background: rgba(245, 108, 108, 0.1);
}
</style>