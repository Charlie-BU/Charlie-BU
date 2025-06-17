<template>
    <el-header class="header">
        <div class="nav-container">
            <div class="logo">
                <h2>Charlie's Blog</h2>
            </div>
            <el-menu mode="horizontal" :default-active="activeIndex" class="nav-menu" router>
                <el-menu-item index="/">{{ t('home') }}</el-menu-item>
                <el-menu-item index="/articles">{{ t('articles') }}</el-menu-item>
                <el-menu-item index="/projects">{{ t('projects') }}</el-menu-item>
                <el-menu-item index="/daily">{{ t('daily') }}</el-menu-item>
                <el-menu-item index="/gallery">{{ t('gallery') }}</el-menu-item>
            </el-menu>
            <!-- 自定义语言切换按钮 -->
            <div class="language-toggle" @click="toggleLanguage">
                <span class="toggle-text">{{ LANG === 'Chinese' ? 'English' : '中文' }}</span>
                <span class="toggle-icon">🌐</span>
            </div>
        </div>
    </el-header>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeIndex = ref('/')
const LANG = ref(localStorage.getItem("LANG") || "Chinese")
// 监听路由变化，更新activeIndex
watch(() => route.path, (newPath) => {
    activeIndex.value = newPath
}, { immediate: true })

const translations = reactive({
    Chinese: {
        home: '首页',
        articles: '文章',
        projects: '项目',
        daily: '日常',
        gallery: '图集',
    },
    English: {
        home: 'Home',
        articles: 'Articles',
        projects: 'Projects',
        daily: 'Daily',
        gallery: 'Gallery',
    }
})
// 翻译函数
const t = (key) => {
    return translations[LANG.value][key] || key
}

const toggleLanguage = () => {
    LANG.value = LANG.value === 'Chinese' ? 'English' : 'Chinese'
    localStorage.setItem('LANG', LANG.value)
    location.reload()
}

</script>

<style scoped>
.header {
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    position: sticky;
    top: 0;
    z-index: 1000;
}

.nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 20px;
    min-width: 800px;
    overflow: visible;
}

.logo h2 {
    color: white;
    margin: 0;
    font-weight: 700;
    background: linear-gradient(45deg, #8B5CF6, #EC4899, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.nav-menu {
    background: transparent;
    border: none;
    flex: 1;
    justify-content: flex-end;
    min-width: 0;
}

.nav-menu .el-menu-item {
    color: rgba(255, 255, 255, 0.8);
    border: none;
    font-weight: 700;
    transition: all 0.3s ease;
    white-space: nowrap;
    flex-shrink: 0;
}

/* 防止菜单项被折叠 */
.nav-menu .el-menu {
    display: flex !important;
    flex-wrap: nowrap !important;
}

.nav-menu .el-menu-item {
    display: flex !important;
}

.nav-menu .el-menu-item:hover {
    color: white;
    background: transparent;
    border-radius: 8px;
}

.nav-menu .el-menu-item.is-active {
    color: white;
    background: transparent;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .nav-container {
        flex-direction: column;
        gap: 20px;
        min-width: auto;
    }

    .nav-menu {
        width: 100%;
        justify-content: center;
    }

    .nav-menu .el-menu {
        justify-content: center !important;
    }

    .language-toggle {
        margin: 10px auto;
    }
}

.lang-switch {
    display: none;
}

/* 新的语言切换按钮样式 */
.language-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: 20px;
    padding: 6px 12px;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.5), rgba(236, 72, 153, 0.5));
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.language-toggle:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.7), rgba(236, 72, 153, 0.7));
}

.toggle-text {
    color: white;
    font-weight: 600;
    font-size: 14px;
}

.toggle-icon {
    font-size: 16px;
}
</style>