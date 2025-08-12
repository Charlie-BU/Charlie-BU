<template>
    <el-main class="article-content" :style="{ 'padding': isMobileRef ? '40px 40px' : '40px 20px' }">
        <div class="article-container">
            <!-- 左侧文章菜单 -->
            <div class="article-sidebar" v-if="!isSidebarCollapsed">
                <div class="sidebar-header">
                    <div class="sidebar-title-row">
                        <h3>{{ t('articleList') }}</h3>
                    </div>
                    <div style="white-space: nowrap;">
                        <el-button v-if="admin_id" class="add-article-btn" size="small" type="primary"
                            @click="handleAddArticle" :icon="Plus">
                            {{ t('addArticle') }}
                        </el-button>
                        <el-button class="add-article-btn" size="small" type="primary" @click="handleSearchArticle"
                            :icon="Search">
                            {{ t('searchArticle') }}
                        </el-button>
                        <el-button class="add-article-btn" size="small" type="primary" @click="toggleCategoryMenu"
                            :icon="CollectionTag">
                            {{ selectedCategory || t('allCategories') }}
                        </el-button>
                    </div>
                </div>
                <el-scrollbar style="overflow: auto;">
                    <div class="article-menu">
                        <div v-for="(article, index) in filteredArticles" :key="index" class="article-menu-item"
                            :class="{ 'active': currentArticleId === article.id }" @click="selectArticle(article.id)">
                            <div class="article-item-header">
                                <div class="article-menu-title">{{ article.title }}</div>
                                <el-button v-if="admin_id" class="delete-article-btn" size="small" type="danger"
                                    @click.stop="handleDeleteArticle(article.id)" :icon="Delete" circle>
                                </el-button>
                            </div>
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
                <div class="article-header">
                    <div class="article-title-row">
                        <h1 class="article-title">{{ currentArticle.title }}</h1>
                        <div v-if="admin_id" class="article-actions">
                            <el-button size="medium" type="primary" @click="handleEditArticle(currentArticle.id)"
                                :icon="Edit">
                                {{ t('editArticle') }}
                            </el-button>
                            <el-button size="medium" type="primary"
                                :style="{ background: currentArticle.isReleased ? '' : 'green' }"
                                @click="handleDraftOrReleased(currentArticle.id)"
                                :icon="currentArticle.isReleased ? 'MessageBox' : 'Promotion'">
                                {{ currentArticle.isReleased ? t('setAsDraft') : t('publish') }}
                            </el-button>
                        </div>
                    </div>
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
                                    <Clock />
                                </el-icon>
                                <span>{{ t('updated') }}: {{ formatTime(currentArticle.timeLastUpdated) }}</span>
                            </div>
                            <div class="time-item">
                                <el-icon>
                                    <Document />
                                </el-icon>
                                <span>{{ t('wordCount') }}: {{ countContent(currentArticle.content).wordCount || 0
                                }}</span>
                            </div>
                            <div class="time-item">
                                <el-icon>
                                    <Timer />
                                </el-icon>
                                <span>{{ t('readingTime') }}: {{ countContent(currentArticle.content).readingTime || 0
                                }} {{ t('minute') }}</span>
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

            <!-- 折叠按钮 -->
            <el-button class="collapse-btn" :class="{ 'collapsed': isSidebarCollapsed }" circle
                @click="isSidebarCollapsed = !isSidebarCollapsed" :icon="Menu" />
        </div>
    </el-main>


    <!-- 分类导航菜单 -->
    <transition name="modal-fade">
        <div v-if="categoryMenuVisible" class="category-modal-overlay" @click="categoryMenuVisible = false">
            <div class="category-modal" :style="{ width: isMobileRef ? '50%' : '15%' }" @click.stop>
                <div class="category-modal-header">
                    <span class="category-modal-title">{{ t('categories') }}</span>
                </div>
                <div class="category-modal-body">
                    <el-menu class="category-menu" :default-active="selectedCategory" @select="handleCategorySelect">
                        <div class="category-menu-items">
                            <el-menu-item index="">
                                <span>{{ t('allCategories') }}</span>
                                <el-tag size="small" class="category-count">{{ articles.length }}</el-tag>
                            </el-menu-item>
                            <el-menu-item v-for="category in categories" :key="category" :index="category">
                                <span>{{ category }}</span>
                                <el-tag size="small" class="category-count">{{ getCategoryCount(category) }}</el-tag>
                            </el-menu-item>
                        </div>
                    </el-menu>
                </div>
            </div>
        </div>
    </transition>

    <!-- 搜索弹窗 -->
    <transition name="modal-fade">
        <div v-if="searchDialogVisible" class="search-modal-overlay" @click="searchDialogVisible = false">
            <div class="search-modal" :style="{ width: isMobileRef ? '80%' : '40%' }" @click.stop>
                <!-- <div class="search-modal-header">
                    <span class="search-modal-title">{{ t('searchArticle') }}</span>
                </div> -->
                <div class="search-modal-body">
                    <div class="custom-input-wrapper">
                        <span class="input-prefix-icon">
                            <el-icon>
                                <Search />
                            </el-icon>
                        </span>
                        <input v-model="searchInput" class="custom-input"
                            :placeholder="t('searchArticlePlaceholder')" />
                    </div>
                    <div v-if="searchInput" class="search-results">
                        <div class="search-item" v-for="article in searchResult" :key="article.id"
                            @click="selectArticle(article.id)">
                            <div class="search-item-title" v-html="article.title"></div>
                            <div class="search-item-content" v-html="article.content_show"></div>
                            <div class="search-item-meta">
                                <span>{{ t('created') }}: {{ formatTime(article.timeCreated) }}</span>
                                <br />
                                <span>{{ t('updated') }}: {{ formatTime(article.timeLastUpdated) }}</span>
                            </div>
                            <!-- <div class="article-tags">
                                <el-tag v-for="(tag, tagIndex) in currentArticle.tags" :key="tagIndex" size="small"
                                    effect="dark" class="article-tag">
                                    {{ tag }}
                                </el-tag>
                            </div> -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </transition>

    <!-- 删除确认弹窗 -->
    <Modal v-model:visible="deleteDialogVisible" type="delete" :title="t('deleteArticle')" :content="t('deleteConfirm')"
        @confirm="confirmDelete" @cancel="cancelDelete" />

</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { Plus, Delete, Edit, CollectionTag, Clock, Search, Close, CircleClose } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'
import Cookies from 'js-cookie'
import { request } from '../api/request'
import { calcHashForArticleId, getArticleIdFromHash, isMobile, countContent } from '../utils/utils'
import Modal from './Modal.vue'
// 在 Element Plus 中，图标（如 Menu）是独立的 Vue 组件，不能通过全局注册来自动可用
import { Menu } from '@element-plus/icons-vue'

// 路由
const route = useRoute()
const router = useRouter()

onMounted(async () => {
    await checkAdminPermission()
    await getArticles()
    await routeArticle()
    // 添加键盘事件监听
    document.addEventListener('keydown', handleKeyDown)
})

const isSidebarCollapsed = ref(false)
const isMobileRef = ref(isMobile())

// Command(Ctrl)+F 查找
const handleKeyDown = async (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'f') {
        // 阻止默认的保存行为
        event.preventDefault()
        searchDialogVisible.value = true
    }
    if (event.key === 'Escape') {
        if (searchDialogVisible.value === true) {
            searchDialogVisible.value = false
        }
        if (categoryMenuVisible.value === true) {
            categoryMenuVisible.value = false
        }
    }
}

// 监听路由参数变化
watch(() => route.params.id, (newId, oldId) => {
    // 只有当新ID与旧ID不同，且新ID不等于当前选中的文章ID时才处理
    if (newId && newId !== oldId && articles.value.length > 0) {
        routeArticle()
    }
})

// 初始化markdown-it
const markdown = new MarkdownIt()

// 多语言支持
const LANG = localStorage.getItem("LANG") || "Chinese";
const translations = {
    Chinese: {
        articleList: '文章列表',
        selectArticle: '请选择一篇文章',
        created: '创建时间',
        updated: '更新时间',
        wordCount: '字数',
        readingTime: '预计阅读时间',
        minute: '分钟',
        addArticle: '新文章',
        setAsDraft: '设为草稿',
        publish: '发布',
        editArticle: '编辑',
        deleteArticle: '删除文章',
        deleteConfirm: '确定要删除这篇文章吗？',
        deleteSuccess: '删除成功',
        deleteFailed: '删除失败',
        allCategories: '全部',
        categories: '分类',
        searchArticle: '搜索',
        searchArticlePlaceholder: '输入文章标题或内容',
    },
    English: {
        articleList: 'Article List',
        selectArticle: 'Please select an article',
        created: 'Created',
        updated: 'Updated',
        wordCount: 'Word Count',
        readingTime: 'Estimated Reading Time',
        minute: 'minute(s)',
        addArticle: 'New',
        setAsDraft: 'Set as Draft',
        publish: 'Publish',
        editArticle: 'Edit',
        deleteArticle: 'Delete Article',
        deleteConfirm: 'Are you sure you want to delete this article?',
        deleteSuccess: 'Delete successful',
        deleteFailed: 'Delete failed',
        allCategories: 'All',
        categories: 'Categories',
        searchArticle: 'Search',
        searchArticlePlaceholder: 'Search articles by title or content',
    }
}

// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key
}

// 管理员权限
const admin_id = ref(false)

// 检查管理员权限
const checkAdminPermission = async () => {
    try {
        const res = await request.post('/api/check_sessionid', {
            sessionid: Cookies.get('sessionid')
        })
        if (!res.data.admin_id) {
            Cookies.remove('sessionid')
        }
        admin_id.value = res.data.admin_id
    } catch (error) {
        console.error('检查管理员权限失败:', error)
    }
}

// 分类相关
// 分类菜单显示控制
const categoryMenuVisible = ref(false)

// 切换分类菜单显示状态
const toggleCategoryMenu = () => {
    categoryMenuVisible.value = !categoryMenuVisible.value
}

const selectedCategory = ref('')

// 获取所有分类
const categories = computed(() => {
    // 从文章中提取所有不重复的标签作为分类
    const allTags = new Set()
    articles.value.forEach(article => {
        if (article.tags && article.tags.length) {
            article.tags.forEach(tag => allTags.add(tag))
        }
    })
    return Array.from(allTags)
})

// 获取每个分类的文章数量
const getCategoryCount = (category) => {
    return articles.value.filter(article =>
        article.tags && article.tags.includes(category)
    ).length
}

// 过滤后的文章列表
const filteredArticles = computed(() => {
    if (!selectedCategory.value) {
        return articles.value
    }
    return articles.value.filter(article =>
        article.tags && article.tags.includes(selectedCategory.value)
    )
})

// 处理分类选择
const handleCategorySelect = (index) => {
    selectedCategory.value = index
    if (filteredArticles.value.length > 0) {
        const currentArticleInFiltered = filteredArticles.value.some(article => article.id === currentArticleId.value)
        // 如果过滤后没有文章，或者当前选中的文章不在过滤结果中，则选择第一篇文章
        if (!currentArticleInFiltered) {
            selectArticle(filteredArticles.value[0].id)
        }
        categoryMenuVisible.value = false
    }
}

// 搜索相关
const searchDialogVisible = ref(false)
const searchInput = ref('')
const handleSearchArticle = () => {
    searchDialogVisible.value = true
}

// 监听searchInput变化
watch(() => searchInput.value, (newValue, oldValue) => {
    if (newValue !== oldValue) {
        searchArticles()
    }
})

const searchResult = ref([])
const searchArticles = async () => {
    const keyword = searchInput.value.trim().toLowerCase()
    if (keyword) {
        selectedCategory.value = ''
        try {
            const res = await request.post('/api/search_article', {
                lang: LANG,
                keyword: keyword
            })
            if (res.data.result) {
                searchResult.value = res.data.result
            }
        } catch (error) {
            console.error('搜索文章失败:', error)
        }
    } else {
        searchResult.value = []
    }
}

// 文章列表
const articles = ref([])
const currentArticleId = ref(null)
const currentArticle = ref({})


const routeArticle = async () => {
    const articleHash = route.params.id
    if (!articleHash) {
        currentArticleId.value = filteredArticles.value[0].id
        await getArticleContent()
        return;
    }
    const articleId = getArticleIdFromHash(articleHash)
    // 检查文章列表是否为空
    if (filteredArticles.value.length === 0) {
        return; // 如果没有文章，直接返回
    }

    if (!articleId) {
        // 没有指定文章ID，选择第一篇文章，但不更新URL
        currentArticleId.value = filteredArticles.value[0].id
        return;
    }
    // 检查指定的文章ID是否存在于文章列表中
    const articleExists = filteredArticles.value.some(article => article.id === articleId)
    if (articleExists) {
        currentArticleId.value = articleId
        await getArticleContent()
    } else {
        // 文章不存在，重定向到文章列表页
        router.push("/articles")
        // 直接设置当前文章ID为第一篇文章
        currentArticleId.value = filteredArticles.value[0].id
        await getArticleContent()
    }
}


// 选择文章
const selectArticle = async (id) => {
    searchDialogVisible.value = false
    // 如果当前已经是这篇文章，不做任何操作
    if (currentArticleId.value === id) return;
    currentArticleId.value = id
    // 检查当前路由是否已经是这篇文章
    if (route.params.id !== id) {
        // 更新URL，但不重新加载页面
        const articleHash = calcHashForArticleId(id)
        router.push(`/articles/${articleHash}`)
    }
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
        if (res.data.status !== 200) {
            console.log(res.data.message)
            return
        }
        // 按时间排序（从新到旧）
        articles.value = res.data.articles;
    } catch (error) {
        console.error(error)
    }
}

const getArticleContent = async () => {
    try {
        const res = await request.post('/api/get_article_content', {
            id: currentArticleId.value,
            lang: LANG
        })
        if (res.data.status !== 200) {
            console.log(res.data.message)
            return
        }
        currentArticle.value = res.data.article;
    } catch (error) {
        console.error(error)
    }
}

// 删除相关变量
const deleteDialogVisible = ref(false)
const currentDeleteArticleId = ref(null)

// 删除文章
const handleDeleteArticle = (articleId) => {
    if (!admin_id.value) return
    currentDeleteArticleId.value = articleId
    deleteDialogVisible.value = true
}

// 确认删除
const confirmDelete = async () => {
    if (!currentDeleteArticleId.value) return
    try {
        // 调用删除API
        const res = await request.post('/api/delete_article', {
            id: currentDeleteArticleId.value
        })

        if (res.data.status === 200) {
            ElMessage.success(t('deleteSuccess'))
            // 重新获取文章列表
            await getArticles()
        } else {
            ElMessage.error(res.data.message || t('deleteFailed'))
        }
    } catch (error) {
        ElMessage.error(t('deleteFailed'))
        console.error('删除文章失败:', error)
    } finally {
        currentDeleteArticleId.value = null
    }
}

// 取消删除
const cancelDelete = () => {
    currentDeleteArticleId.value = null
}

// 添加文章
const handleAddArticle = () => {
    if (!admin_id.value) return
    router.push('/article/new')
}

// 编辑文章
const handleEditArticle = (articleId) => {
    if (!admin_id.value) return
    router.push(`/article/edit/${articleId}`)
}

// 切换文章发布状态（草稿/已发布）
const handleDraftOrReleased = async (articleId) => {
    if (!admin_id.value) return
    try {
        // 获取当前文章
        const article = articles.value.find(article => article.id === articleId)
        if (!article) return

        // 调用更新API，切换isReleased状态
        const res = await request.post('/api/change_article_status', {
            id: articleId
        })

        if (res.data.status === 200) {
            // 更新成功，刷新文章列表
            currentArticle.value.isReleased = !currentArticle.value.isReleased
            ElMessage.success(article.isReleased ? t('setAsDraft') + "成功" : t('publish') + "成功")
            await getArticles()
        } else {
            ElMessage.error(res.data.message || t('saveFailed'))
        }
    } catch (error) {
        console.error('更新文章状态失败:', error)
        ElMessage.error(t('saveFailed'))
    }
}

onBeforeUnmount(() => {
    // 组件卸载时移除事件监听
    document.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.article-content {
    max-width: 1500px;
    margin: 0 auto;
}

.article-container {
    position: relative;
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
    height: 800px;
    padding-bottom: 80px;
}

.sidebar-header {
    position: sticky;
    padding: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}


/* 分类过滤器样式 */
.category-filter {
    position: absolute;
    margin-top: 5px;
    background: rgba(76, 8, 125, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    padding: 15px;
    width: 250px;
    z-index: 1000;
    /* 增加z-index确保在其他元素上方 */
}

/* 添加过渡动画 */
.fade-dropdown-enter-active,
.fade-dropdown-leave-active {
    transition: opacity 0.3s, transform 0.3s;
}

.fade-dropdown-enter-from,
.fade-dropdown-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

.category-menu {
    background: transparent;
    border-right: none;
}

.category-title {
    margin: 0 0 10px 0;
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 600;
}

:deep(.el-menu-item) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 40px;
    line-height: 40px;
    color: rgba(255, 255, 255, 0.8);
    padding: 0 15px;
    border-radius: 8px;
    margin-bottom: 5px;
}

:deep(.el-menu-item:hover) {
    background-color: rgba(255, 255, 255, 0.1);
}

:deep(.el-menu-item.is-active) {
    background-color: rgba(139, 92, 246, 0.2);
    color: #A78BFA;
}

:deep(.el-menu--horizontal>.el-menu-item.is-active) {
    border-bottom: none;
}

:deep(.el-menu-item:focus) {
    background-color: rgba(139, 92, 246, 0.2);
}

.category-count {
    background: rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.3);
    color: #A78BFA;
    margin-left: 8px;
}

.sidebar-title-row {
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

.sidebar-header h3 {
    margin: 0;
    color: #ffffff;
    font-size: 1.3rem;
    font-weight: 600;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.add-article-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    transition: all 0.3s ease;
}

.add-article-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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

.article-item-header {
    margin-bottom: 5px;
}

.article-menu-title {
    font-weight: 600;
    color: #ffffff;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    width: 100%;
}

.delete-article-btn {
    position: absolute;
    /* 绝对定位 */
    right: 0;
    /* 靠右对齐 */
    top: 0;
    /* 靠顶部对齐 */
    background: rgba(245, 101, 101, 0.8);
    border: none;
    width: 24px;
    height: 24px;
    min-height: 24px;
    padding: 0;
    opacity: 0;
    transition: all 0.3s ease;
}

.article-menu-item:hover .delete-article-btn {
    opacity: 1;
}

.delete-article-btn:hover {
    background: rgba(245, 101, 101, 1);
    transform: scale(1.1);
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
    background: rgba(245, 158, 11, 0.2);
    border-color: rgba(245, 158, 11, 0.6);
    color: #F59E0B;
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
    max-height: 800px;
    overflow: auto;
    overflow-y: auto;
}

.article-header {
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.article-title-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;
    margin-bottom: 20px;
}

.article-title {
    position: relative;
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
    color: #ffffff;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    flex: 1;
}

.article-actions {
    position: absolute;
    display: flex;
    gap: 10px;
    right: 30px;
}

.article-actions .el-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    transition: all 0.3s ease;
    color: white;
}

.article-actions .el-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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

    .sidebar-title-row {
        flex-direction: column;
        align-items: stretch;
        gap: 15px;
    }

    .article-title-row {
        flex-direction: column;
        align-items: stretch;
        gap: 15px;
    }

    .article-item-header {
        flex-direction: column;
        gap: 8px;
    }

    .delete-article-btn {
        align-self: flex-end;
        opacity: 1;
    }
}

/* 表单提示样式 */
.form-tip {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.6);
    margin-top: 4px;
}

.collapse-btn {
    position: absolute;
    top: 10px;
    left: 10px;
    /* 调整位置 */
    z-index: 1000;
    width: 30px;
    height: 30px;
    padding: 0;
}

/* 表单内的输入框样式覆盖 */
:deep(.el-input__inner),
:deep(.el-textarea__inner) {
    background-color: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: white;
}

:deep(.el-input__inner:focus),
:deep(.el-textarea__inner:focus) {
    border-color: #A78BFA;
    box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.2);
}

:deep(.el-form-item__label) {
    color: rgba(255, 255, 255, 0.9);
}

.category-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: flex-start;
    z-index: 1000;
}

.category-modal {
    margin-top: 120px;
    background: rgba(76, 8, 125, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    overflow: hidden;
}

.category-modal-header {
    padding: 15px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.category-modal-title {
    color: rgba(255, 255, 255, 0.9);
    font-size: 16px;
    font-weight: 600;
}

.category-modal-close {
    color: rgba(255, 255, 255, 0.7);
    cursor: pointer;
}

.category-modal-close:hover {
    color: rgba(255, 255, 255, 0.9);
}

.category-modal-body {
    padding: 15px 20px;
}

.search-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: flex-start;
    z-index: 1000;
}

.search-modal {
    margin-top: 120px;
    background: rgba(76, 8, 125, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    overflow: hidden;
}

.search-modal-header {
    padding: 15px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.search-modal-title {
    color: rgba(255, 255, 255, 0.9);
    font-size: 16px;
    font-weight: 600;
}

.search-modal-close {
    color: rgba(255, 255, 255, 0.7);
}

.search-modal-close:hover {
    color: rgba(255, 255, 255, 0.9);
}

.search-modal-body {
    padding: 15px 20px;
}

.search-results {
    margin-top: 10px;
    max-height: 500px;
    overflow: auto;
}

.search-item {
    padding: 10px 15px;
    cursor: pointer;
    color: rgba(255, 255, 255, 0.8);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    transition: background 0.2s;
    border-radius: 20px;
}

.search-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

.search-item-title {
    font-weight: bold;
    margin-bottom: 5px;
}

.search-item-content {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
    text-align: left;
    margin-bottom: 5px;
}

.search-item-meta {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
    margin-bottom: 5px;
    text-align: left;
}

.search-item-tags .el-tag {
    margin-right: 5px;
}

/* 模态动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
    transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
}

.modal-fade-enter-active .search-modal,
.modal-fade-leave-active .search-modal {
    transition: transform 0.3s ease;
}

.modal-fade-enter-from .search-modal,
.modal-fade-leave-to .search-modal {
    transform: scale(0.95);
}

.custom-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 0 15px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: border-color 0.3s;
}

.custom-input-wrapper:hover {
    border-color: rgba(255, 255, 255, 0.4);
}

.custom-input-wrapper:focus-within {
    border-color: #A78BFA;
    box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.2);
}

.input-prefix-icon {
    color: rgba(255, 255, 255, 0.6);
    margin-right: 10px;
    margin-top: 5px;
}

.custom-input {
    flex: 1;
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.9);
    font-size: 14px;
    padding: 10px 0;
    outline: none;
}

.custom-input::placeholder {
    color: rgba(255, 255, 255, 0.4);
}

.input-clear-icon {
    color: rgba(255, 255, 255, 0.6);
    cursor: pointer;
    margin-left: 10px;
}

.input-clear-icon:hover {
    color: rgba(255, 255, 255, 0.9);
}
</style>