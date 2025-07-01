<template>
    <el-footer class="footer">
        <div class="footer-content">
            <p>Copyright © 2025 - Present <span style="font-style: italic; font-weight: bold;">Charlie. BU</span>
                {{ t('footnote') }}</p>
            <div class="social-links">
                <el-button circle class="social-btn">
                    <el-icon>
                        <Platform />
                    </el-icon>
                </el-button>
                <el-button circle class="social-btn">
                    <el-icon>
                        <ChatDotRound />
                    </el-icon>
                </el-button>
                <el-button circle class="social-btn">
                    <el-icon>
                        <Link />
                    </el-icon>
                </el-button>
            </div>
        </div>
    </el-footer>
</template>

<script setup>
import { reactive } from 'vue'

const LANG = localStorage.getItem("LANG") || "Chinese";
const translations = reactive({
    Chinese: {
        footnote: '用心创造每一个像素.'
    },
    English: {
        footnote: 'Create every pixel with heart.'
    }
})
// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key
}
</script>

<style scoped>
.footer {
    background: rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    margin-top: 60px;
    height: auto;
}

.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    color: rgba(255, 255, 255, 0.8);
}

.social-links {
    display: flex;
    gap: 12px;
}

.social-btn {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    transition: all 0.3s ease;
}

.social-btn:hover {
    background: rgba(139, 92, 246, 0.3);
    transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .footer-content {
        flex-direction: column;
        gap: 20px;
        text-align: center;
    }
}
</style>