<template>
    <el-header class="header">
        <div class="nav-container">
            <div class="logo">
                <h2>Charlie's Blog</h2>
            </div>
            <el-menu mode="horizontal" :default-active="activeIndex" class="nav-menu" @select="handleSelect">
                <el-menu-item index="1">首页</el-menu-item>
                <el-menu-item index="2">文章</el-menu-item>
                <el-menu-item index="3">项目</el-menu-item>
                <el-menu-item index="4">日常</el-menu-item>
                <el-menu-item index="5">图集</el-menu-item>
            </el-menu>
        </div>
    </el-header>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeIndex = ref('1')

const handleSelect = (key: string) => {
    activeIndex.value = key
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
}
</style>