<template>
    <div class="app-container">
        <div class="dynamic-background">
            <div class="gradient-orb orb-1"></div>
            <div class="gradient-orb orb-2"></div>
            <div class="gradient-orb orb-3"></div>
            <div class="gradient-orb orb-4"></div>
        </div>

        <!-- 顶部导航栏 -->
        <NavBar />

        <!-- 主要内容区域 -->
        <router-view />

        <!-- 底部 -->
        <Footer />
    </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
import Footer from './components/Footer.vue'
import { onMounted } from 'vue'

onMounted(() => {
    const LANG = localStorage.getItem("LANG");
    if (LANG !== "Chinese" && LANG !== "English") {
        localStorage.setItem("LANG", "Chinese");
    }
})
</script>

<style scoped>
.app-container {
    width: 100%;
    height: 100%;
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
    margin: 0;
    padding: 0;
}

/* 动态背景 */
.dynamic-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    /* 不加背景色方案 */
    /* background: linear-gradient(-45deg, #4c087d, #a50495, #3d0069, #671bad, #0071e3, #8225d3, #4A00E0); */
    /* background-size: 400% 400%; */
    /* animation: gradient 40s ease infinite; */
}

/* @keyframes gradient {
    0% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }

    100% {
        background-position: 0% 50%;
    }
} */

.gradient-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(70px);
    animation: float 8s ease-in-out infinite;
    opacity: 0.8;
}

.orb-1 {
    width: 300px;
    height: 300px;
    background: linear-gradient(45deg, #0575E6, #00F260);
    top: 60%;
    left: 5%;
    animation-delay: 0s;
}

.orb-2 {
    width: 200px;
    height: 200px;
    background: linear-gradient(45deg, #8E2DE2, #4A00E0);
    top: 60%;
    right: 10%;
    animation-delay: 2s;
}

.orb-3 {
    width: 250px;
    height: 250px;
    background: linear-gradient(45deg, #a50495, #671bad);
    bottom: 60%;
    left: 50%;
    animation-delay: 4s;
}

.orb-4 {
    width: 220px;
    height: 220px;
    background: linear-gradient(45deg, #00F260, #4A00E0);
    top: 20%;
    right: 25%;
    animation-delay: 1s;
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0px) rotate(0deg) scale(1);
    }

    50% {
        transform: translateY(-20px) rotate(180deg) scale(1.05);
    }
}
</style>
