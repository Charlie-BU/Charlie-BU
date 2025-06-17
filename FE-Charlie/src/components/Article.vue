<template>
    <el-main class="article-content">
        <div class="article-container">
            <!-- 左侧文章菜单 -->
            <div class="article-sidebar">
                <div class="sidebar-header">
                    <h3>{{ t('articleList') }}</h3>
                </div>
                <el-scrollbar height="calc(100vh - 200px)">
                    <div class="article-menu">
                        <div v-for="(article, index) in articles" :key="index" class="article-menu-item"
                            :class="{ 'active': currentArticleId === article.id }" @click="selectArticle(article.id)">
                            <div class="article-menu-title">{{ article.title }}</div>
                            <div class="article-menu-date">{{ formatTime(article.timeCreated) }}</div>
                            <div class="article-menu-tags">
                                <el-tag v-for="(tag, tagIndex) in article.tags" :key="tagIndex" size="small"
                                    effect="dark" class="article-tag">
                                    {{ tag }}
                                </el-tag>
                            </div>
                        </div>
                    </div>
                </el-scrollbar>
            </div>

            <!-- 右侧文章内容 -->
            <div class="article-main">
                <el-empty v-if="!currentArticle" :description="t('selectArticle')"></el-empty>
                <div v-else class="article-detail">
                    <div class="article-header">
                        <h1 class="article-title">{{ currentArticle.title }}</h1>
                        <div class="article-meta">
                            <div class="article-time">
                                <div class="time-item">
                                    <el-icon>
                                        <Calendar />
                                    </el-icon>
                                    <span>{{ t('created') }}: {{ formatTime(currentArticle.timeCreated) }}</span>
                                </div>
                                <div class="time-item">
                                    <el-icon>
                                        <Timer />
                                    </el-icon>
                                    <span>{{ t('updated') }}: {{ formatTime(currentArticle.timeLastUpdated) }}</span>
                                </div>
                            </div>
                            <div class="article-tags">
                                <el-tag v-for="(tag, tagIndex) in currentArticle.tags" :key="tagIndex" size="small"
                                    effect="dark" class="article-tag">
                                    {{ tag }}
                                </el-tag>
                            </div>
                        </div>
                    </div>
                    <div class="article-content-body">
                        <!-- 根据文章类型渲染不同内容 -->
                        <template v-if="currentArticle.type === 1">
                            {{ currentArticle.content }}
                        </template>
                        <div v-else-if="currentArticle.type === 2" v-html="renderMarkdown(currentArticle.content)">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </el-main>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Calendar, Timer } from '@element-plus/icons-vue'
import { request } from '../api/request'
import MarkdownIt from 'markdown-it' // 导入markdown-it

// 初始化markdown-it
const markdown = new MarkdownIt()

// 多语言支持
const LANG = localStorage.getItem("LANG") || "Chinese";
const translations = {
    Chinese: {
        articleList: '文章列表',
        selectArticle: '请选择一篇文章',
        created: '创建时间',
        updated: '更新时间'
    },
    English: {
        articleList: 'Article List',
        selectArticle: 'Please select an article',
        created: 'Created',
        updated: 'Updated'
    }
}

// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key
}

// 文章列表
const articles = ref([])
const currentArticleId = ref(null)

// 获取当前选中的文章
const currentArticle = computed(() => {
    return articles.value.find(article => article.id === currentArticleId.value) || null
})

// 选择文章
const selectArticle = (id) => {
    currentArticleId.value = id
}

// 格式化日期
const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString(LANG === 'Chinese' ? 'zh-CN' : 'en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
    })
}

// Markdown渲染函数
const renderMarkdown = (content) => {
    return markdown.render(content || '')
}

// 获取文章列表
const getArticles = async () => {
    try {
        const res = await request.post('/api/get_articles', {
            lang: LANG
        })
        if (res.status !== 200) {
            console.log(res.message)
            return
        }
        // 按时间排序（从新到旧）
        articles.value = res.data.articles;
        selectArticle(articles.value[0].id);
    } catch (error) {
        console.error(error)
    }
}

onMounted(async () => {
    await getArticles()
})
</script>

<style scoped>
.article-content {
    max-width: 1500px;
    margin: 0 auto;
    padding: 40px 20px;
}

.article-container {
    display: flex;
    gap: 30px;
    min-height: calc(100vh - 200px);
}

/* 左侧菜单样式 */
.article-sidebar {
    flex: 0 0 300px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    height: fit-content;
}

.sidebar-header {
    padding: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.sidebar-header h3 {
    margin: 0;
    color: #ffffff;
    font-size: 1.3rem;
    font-weight: 600;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.article-menu {
    padding: 10px;
}

.article-menu-item {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.article-menu-item:hover {
    background: rgba(255, 255, 255, 0.12);
    transform: translateY(-2px);
}

.article-menu-item.active {
    background: rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.5);
    box-shadow: 0 5px 15px rgba(139, 92, 246, 0.2);
}

.article-menu-title {
    font-weight: 600;
    margin-bottom: 5px;
    color: #ffffff;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.article-menu-date {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 8px;
}

.article-menu-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}

.article-tag {
    background: rgba(139, 92, 246, 0.3);
    border-color: rgba(139, 92, 246, 0.5);
    color: #A78BFA;
}

/* 右侧内容样式 */
.article-main {
    flex: 1;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    padding: 30px;
    overflow: hidden;
}

.article-header {
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.article-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 20px;
    color: #ffffff;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.article-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 15px;
}

.article-time {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.time-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.9rem;
}

.article-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.article-content-body {
    color: rgba(255, 255, 255, 0.92);
    line-height: 1.8;
    font-size: 1.1rem;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    text-align: justify;
}

/* 添加Markdown样式 */
.article-content-body :deep(h1),
.article-content-body :deep(h2),
.article-content-body :deep(h3),
.article-content-body :deep(h4),
.article-content-body :deep(h5),
.article-content-body :deep(h6) {
    margin-top: 1.5em;
    margin-bottom: 0.8em;
    font-weight: 600;
    color: #ffffff;
    text-align: left;
}

.article-content-body :deep(p) {
    margin-bottom: 1em;
    text-align: justify;
}

.article-content-body :deep(a) {
    color: #A78BFA;
    text-decoration: none;
}

.article-content-body :deep(a:hover) {
    text-decoration: underline;
}

.article-content-body :deep(ul),
.article-content-body :deep(ol) {
    padding-left: 2em;
    margin-bottom: 1em;
}

.article-content-body :deep(blockquote) {
    border-left: 4px solid rgba(139, 92, 246, 0.5);
    padding-left: 1em;
    margin-left: 0;
    margin-right: 0;
    font-style: italic;
    color: rgba(255, 255, 255, 0.7);
}

.article-content-body :deep(code) {
    background: rgba(0, 0, 0, 0.2);
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: monospace;
    font-size: 0.9em;
}

.article-content-body :deep(pre) {
    background: rgba(0, 0, 0, 0.2);
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    margin-bottom: 1em;
}

.article-content-body :deep(pre code) {
    background: none;
    padding: 0;
}

.article-content-body :deep(table) {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1em;
}

.article-content-body :deep(th),
.article-content-body :deep(td) {
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.5em;
}

.article-content-body :deep(th) {
    background: rgba(0, 0, 0, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .article-container {
        flex-direction: column;
    }

    .article-sidebar {
        flex: none;
        width: 100%;
        max-height: 300px;
    }
}
</style>