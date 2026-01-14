<template>
    <el-footer class="footer">
        <div class="footer-content">
            <p>
                Copyright © 2025 - Present
                <span style="font-style: italic; font-weight: bold"
                    >Charlie. BU</span
                >
                <br v-if="isMobileRef" />
                {{ t("footnote") }}
                <!-- 随时删 -->
                <!-- <a
                    href="https://beian.miit.gov.cn/#/Integrated/index"
                    target="_blank"
                    >蒙ICP备2024013129号-4</a
                > -->
            </p>
        </div>
    </el-footer>
</template>

<script setup>
import { ref, reactive } from "vue";
import { isMobile } from "../utils/utils";

const isMobileRef = ref(isMobile());

const LANG = localStorage.getItem("LANG") || "Chinese";
const translations = reactive({
    Chinese: {
        footnote: "用心创造每一个像素.",
    },
    English: {
        footnote: "Create every pixel with heart.",
    },
});
// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key;
};
</script>

<style scoped>
.footer {
    background: rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    margin-top: 40px;
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

/* 响应式设计 */
@media (max-width: 768px) {
    .footer-content {
        flex-direction: column;
        gap: 20px;
        text-align: center;
    }
}
</style>
