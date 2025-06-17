<template>
    <el-main class="main-content">
        <!-- 英雄区域 -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">
                    <span class="gradient-text">Hey, I'm Charlie</span>
                </h1>
                <p class="hero-subtitle">
                    {{ charlie.description }}
                </p>
                <div class="hero-buttons">
                    <el-button type="primary" size="large" class="cta-button" @click="goto_github">
                        <el-icon class="button-icon">
                            <Star />
                        </el-icon>
                        {{ t('viewProjects') }}
                    </el-button>
                    <el-button size="large" class="secondary-button" @click="email_me">
                        <el-icon class="button-icon">
                            <Message />
                        </el-icon>
                        {{ t('contactMe') }}
                    </el-button>
                </div>
            </div>
            <div class="hero-avatar">
                <div class="avatar-container">
                    <div class="glass-sphere-glow"></div>
                    <div class="glass-sphere">
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
            <div class="section-title">
                <h2>{{ t('myTalents') }}</h2>
            </div>
            <el-row :gutter="24" class="features-grid">
                <el-col :xs="24" :sm="12" :md="8" v-for="(talent, index) in talents" :key="index">
                    <el-card class="feature-card" shadow="hover">
                        <div class="feature-icon">
                            <el-icon :size="40">
                                <component :is="talent.icon" />
                            </el-icon>
                        </div>
                        <h3>{{ talent.title }}</h3>
                        <p>{{ talent.description }}</p>
                    </el-card>
                </el-col>
            </el-row>
        </section>

        <section style="margin-top: 120px;">
            <div class="section-title">
                <h2>{{ t('myAchievements') }}</h2>
            </div>
            <el-row class="stats-section" :gutter="24">
                <el-col :xs="12" :sm="6" v-for="(achievement, index) in achievements" :key="index">
                    <div class="stat-item">
                        <div class="stat-number">{{ achievement.number }}</div>
                        <div class="stat-label">{{ achievement.label }}</div>
                    </div>
                </el-col>
            </el-row>
        </section>

        <section style="margin-top: 120px;">
            <div class="section-title">
                <h2>{{ t('growthPath') }}</h2>
            </div>
            <el-timeline style="max-width: 600px; margin: auto;">
                <el-timeline-item v-for="(item, index) in growthTimelines" :key="index" :timestamp="item.timestamp"
                    placement="top">
                    {{ item.content }}
                </el-timeline-item>
            </el-timeline>
        </section>

        <section style="margin-top: 120px;">
            <div class="section-title">
                <h2>{{ t('thoughts') }}</h2>
            </div>
            <div class="thoughts-container">
                <el-card v-for="(bubble, index) in bubbles" :key="index" class="thought-card" shadow="hover">
                    <div class="thought-header">
                        <div class="thought-date">
                            <el-icon>
                                <Calendar />
                            </el-icon>
                            <span>{{ bubble.date }}</span>
                        </div>
                        <div class="thought-tags">
                            <el-tag v-for="(tag, tagIndex) in bubble.tags" :key="tagIndex" size="small" effect="dark"
                                class="thought-tag">
                                {{ tag }}
                            </el-tag>
                        </div>
                    </div>
                    <div class="thought-content">
                        <el-icon class="quote-icon">
                            <ChatDotRound />
                        </el-icon>
                        <p>{{ bubble.content }}</p>
                    </div>
                </el-card>
            </div>
        </section>

        <section style="margin-top: 120px; text-align: center;">
            <div class="section-title">
                <h2>{{ t('selfDefinition') }}</h2>
            </div>
            <blockquote
                style="font-style: italic; color: rgba(255,255,255,0.8); max-width: 600px; margin: auto; font-size: 1.2rem;">
                {{ charlie.motto }}
            </blockquote>
        </section>
    </el-main>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import {
    Star,
    Message
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus';
import Cookies from 'js-cookie';

import { request } from '../api/request'

const LANG = localStorage.getItem("LANG") || "Chinese";
const translations = reactive({
    Chinese: {
        viewProjects: '查看我的项目',
        contactMe: '与我交流',
        myTalents: '我的专长',
        myAchievements: '我的成就',
        growthPath: '成长轨迹',
        thoughts: '碎碎念',
        selfDefinition: '一句话自我定义'
    },
    English: {
        viewProjects: 'View My Projects',
        contactMe: 'Contact Me',
        myTalents: 'My Talents',
        myAchievements: 'My Achievements',
        growthPath: 'Growth Path',
        thoughts: 'Thoughts',
        selfDefinition: 'Self Definition'
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
        if (res.status !== 200) {
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
            lang
        });
        if (res.status !== 200) {
            ElMessage(res.message)
            console.log(res.message)
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
        if (res.status !== 200) {
            ElMessage(res.message)
            console.log(res.message)
            return;
        }
        talents.value = res.data.talents;
    } catch (error) {
        ElMessage(error)
        console.log(error)
    }
}

// 我的成就
const achievements = ref([])
const get_achievements = async (lang) => {
    try {
        const res = await request.post('/api/get_achievements', {
            lang
        });
        if (res.status !== 200) {
            ElMessage(res.message)
            console.log(res.message)
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
        if (res.status !== 200) {
            ElMessage(res.message)
            console.log(res.message)
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
        if (res.status !== 200) {
            ElMessage(res.message)
            console.log(res.message)
            return;
        }
        bubbles.value = res.data.bubbles;
    } catch (error) {
        ElMessage(error)
        console.log(error)
    }
}

const goto_github = () => {
    if (!charlie?.value?.github) {
        ElMessage("Github暂无法访问")
        return;
    }
    window.open(charlie.value.github, '_blank')
}

const email_me = () => {
    if (!charlie?.value?.email) {
        ElMessage("请稍后再试")
        return;
    }
    window.location.href = `mailto:${charlie.value.email}`
}
</script>


<style scoped>
/* 主要内容 */
.main-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
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
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.95);
    margin-bottom: 30px;
    line-height: 1.6;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    font-weight: bold;
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
    transition: all 0.3s ease;
}

.secondary-button:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}

/* 头像区域 */
.hero-avatar {
    flex: 0 0 auto;
    margin-left: 40px;
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
    overflow: hidden;
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
    padding: 30px 20px;
    transition: all 0.3s ease;
    height: 100%;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
}

.stat-item {
    text-align: center;
    padding: 20px;
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 800;
    color: #8B5CF6;
    margin-bottom: 8px;
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
</style>

<style scoped>
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
</style>