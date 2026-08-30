<template>
    <el-main class="login-content">
        <div class="login-container">
            <div class="login-card">
                <div class="login-header">
                    <h2 class="gradient-text">{{ t('welcomeBack') }}</h2>
                    <p class="login-subtitle">{{ t('loginSubtitle') }}</p>
                </div>

                <div class="login-form">
                    <el-form :model="loginForm" :rules="rules" ref="loginFormRef">
                        <el-form-item prop="username">
                            <el-input v-model="loginForm.username" :placeholder="t('username')" prefix-icon="User"
                                class="custom-input" />
                        </el-form-item>

                        <el-form-item prop="password">
                            <el-input v-model="loginForm.password" :placeholder="t('password')" prefix-icon="Lock"
                                type="password" class="custom-input" show-password />
                        </el-form-item>

                        <el-button type="primary" class="login-button" @click="handleLogin" :loading="loading">
                            {{ t('login') }}
                        </el-button>
                    </el-form>
                </div>

            </div>

            <div class="login-decoration">
                <div class="glass-sphere-container">
                    <div class="glass-sphere-glow"></div>
                    <div class="glass-sphere">
                        <div class="glass-sphere-inner">
                            <div class="glass-sphere-reflection"></div>
                            <div class="glass-sphere-reflection secondary"></div>
                            <el-icon :size="80" class="decoration-icon">
                                <Key />
                            </el-icon>
                        </div>
                    </div>
                </div>
                <div class="decoration-text">
                    <h3 class="gradient-text">{{ t('adminLogin') }}</h3>
                    <p>{{ t('adminLoginDesc') }}</p>
                </div>
            </div>
        </div>
    </el-main>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import Cookies from 'js-cookie'
import { Message } from "@arco-design/web-vue";

import { request } from '../api/request'

const router = useRouter()

// 语言设置
const LANG = localStorage.getItem("LANG") || "Chinese"
const translations = reactive({
    Chinese: {
        welcomeBack: '欢迎回来',
        loginSubtitle: '登录您的账号以继续',
        username: '用户名',
        password: '密码',
        login: '登录',
        adminLogin: '管理员登录',
        adminLoginDesc: '登录后对网站信息进行更新',
        usernameRequired: '请输入用户名',
        passwordRequired: '请输入密码',
        loginSuccess: '登录成功',
        loginFailed: '登录失败'
    },
    English: {
        welcomeBack: 'Welcome Back',
        loginSubtitle: 'Login to your account to continue',
        username: 'Username',
        password: 'Password',
        login: 'Login',
        adminLogin: 'Admin Login',
        adminLoginDesc: 'Login to update website information',
        usernameRequired: 'Please enter your username',
        passwordRequired: 'Please enter your password',
        loginSuccess: 'Login successful',
        loginFailed: 'Login failed'
    }
})

// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key
}

// 表单数据
const loginForm = reactive({
    username: '',
    password: '',
})

// 表单验证规则
const rules = {
    username: [
        { required: true, message: () => t('usernameRequired'), trigger: 'blur' }
    ],
    password: [
        { required: true, message: () => t('passwordRequired'), trigger: 'blur' }
    ]
}

const loginFormRef = ref(null)
const loading = ref(false)

// 登录处理
const handleLogin = async () => {
    if (!loginFormRef.value) return

    await loginFormRef.value.validate(async (valid) => {
        if (valid) {
            loading.value = true
            try {
                const res = await request.post('/api/login', {
                    username: loginForm.username,
                    password: loginForm.password
                })
                if (res.data.status !== 200) {
                    Message.error(res.data.message);
                    Cookies.set('sessionid', "");
                    Cookies.remove('sessionid');
                    return;
                }
                Cookies.set('sessionid', res.data.sessionid);
                Message.success(t('loginSuccess'))
                router.push("/")
            } catch (error) {
                console.error(error)
                Message.error(error.message || t('loginFailed'))
            } finally {
                loading.value = false
            }
        }
    })
}
</script>

<style scoped>
.login-content {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 90vh;
    padding: 40px 20px;
}

.login-container {
    display: flex;
    max-width: 1000px;
    width: 100%;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.login-card {
    flex: 1;
    padding: 40px;
    display: flex;
    flex-direction: column;
}

.login-header {
    text-align: center;
    margin-bottom: 30px;
}

.gradient-text {
    background: linear-gradient(45deg, #e674f5, #0e8add, #F59E0B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 3s ease-in-out infinite;
    font-weight: 700;
    margin-bottom: 10px;
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

.login-subtitle {
    color: rgba(255, 255, 255, 0.8);
    font-size: 1rem;
    margin-top: 0;
}

.login-form {
    flex: 1;
    max-width: 400px;
    margin: 0 auto;
    width: 100%;
}

.custom-input :deep(.el-input__wrapper) {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: none;
    border-radius: 10px;
    padding: 12px 15px;
    transition: all 0.3s ease;
}

.custom-input :deep(.el-input__wrapper:hover) {
    border-color: rgba(139, 92, 246, 0.5);
}

.custom-input :deep(.el-input__wrapper.is-focus) {
    box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.5);
    border-color: rgba(139, 92, 246, 0.5);
}

.custom-input :deep(.el-input__inner) {
    color: rgba(255, 255, 255, 0.9);
}

.custom-input :deep(.el-input__prefix-inner) {
    color: rgba(255, 255, 255, 0.6);
}

.form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    font-size: 0.9rem;
}

.forgot-link {
    color: #a78bfa;
    text-decoration: none;
    transition: color 0.3s ease;
}

.forgot-link:hover {
    color: #c4b5fd;
    text-decoration: underline;
}

.login-button {
    width: 100%;
    padding: 12px;
    font-size: 1rem;
    font-weight: 600;
    background: linear-gradient(45deg, #8B5CF6, #EC4899);
    border: none;
    border-radius: 10px;
    margin-bottom: 20px;
    transition: all 0.3s ease;
    margin-top: 20px;
    height: 100%;
    margin-bottom: 40px;
}

.login-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(139, 92, 246, 0.4);
}

.register-option {
    text-align: center;
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
}

.register-link {
    color: #a78bfa;
    font-weight: 600;
    margin-left: 5px;
    text-decoration: none;
    transition: color 0.3s ease;
}

.register-link:hover {
    color: #c4b5fd;
    text-decoration: underline;
}

.login-footer {
    margin-top: 30px;
}

.social-login {
    text-align: center;
}

.social-title {
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.9rem;
    margin-bottom: 15px;
    position: relative;
}

.social-title::before,
.social-title::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 60px;
    height: 1px;
    background: rgba(255, 255, 255, 0.2);
}

.social-title::before {
    left: 20px;
}

.social-title::after {
    right: 20px;
}

.social-icons {
    display: flex;
    justify-content: center;
    gap: 15px;
}

.social-icon {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    transition: all 0.3s ease;
}

.social-icon:hover {
    background: rgba(139, 92, 246, 0.3);
    border-color: rgba(139, 92, 246, 0.5);
    transform: translateY(-3px);
}

/* 装饰部分 */
.login-decoration {
    flex: 1;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(236, 72, 153, 0.2));
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 40px;
    position: relative;
    overflow: hidden;
}

.glass-sphere-container {
    position: relative;
    margin-bottom: 30px;
}

.glass-sphere-glow {
    position: absolute;
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.5), rgba(236, 72, 153, 0.5));
    filter: blur(20px);
    opacity: 0.7;
    z-index: 0;
    animation: pulse 3s ease-in-out infinite;
}

.glass-sphere {
    position: relative;
    width: 160px;
    height: 160px;
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
    display: flex;
    justify-content: center;
    align-items: center;
    animation: float 6s ease-in-out infinite;
    z-index: 1;
}

.glass-sphere-inner {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
}

.glass-sphere-reflection {
    position: absolute;
    width: 60px;
    height: 20px;
    background: rgba(255, 255, 255, 0.25);
    border-radius: 50%;
    filter: blur(3px);
    top: 30px;
    left: 30px;
    transform: rotate(-30deg);
}

.glass-sphere-reflection.secondary {
    width: 30px;
    height: 10px;
    top: 60px;
    left: 100px;
    background: rgba(255, 255, 255, 0.15);
    transform: rotate(20deg);
}

.decoration-icon {
    color: rgba(255, 255, 255, 0.9);
    filter: drop-shadow(0 0 10px rgba(139, 92, 246, 0.7));
}

.decoration-text {
    text-align: center;
    max-width: 300px;
}

.decoration-text h3 {
    font-size: 1.8rem;
    margin-bottom: 10px;
}

.decoration-text p {
    color: rgba(255, 255, 255, 0.8);
    line-height: 1.6;
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-15px);
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

/* 响应式设计 */
@media (max-width: 768px) {
    .login-container {
        flex-direction: column;
    }

    .login-decoration {
        display: none;
    }

    .login-card {
        padding: 30px 20px;
    }

    .social-title::before,
    .social-title::after {
        width: 40px;
    }
}
</style>