<template>
    <el-main class="article-content" :style="{ 'padding': isMobileRef ? '40px 40px' : '40px 20px' }">
        <div class="article-container">
            <!-- AI 总结与目录 -->
            <transition name="sidebar-collapse">
                <div class="article-sidebar-left" v-if="!isSidebarCollapsed" style="padding-bottom: 100px;">
                    <!-- AI 总结 -->
                    <div class="ai-summary">
                        <div class="sidebar-header">
                            <div class="sidebar-title-row" style="display: flex; justify-content: center; gap: 0;">
                                <img src="@/assets/ai.png" alt="AI Icon" class="ai-icon" />
                                <h3>{{ t('AISummary') }}</h3>
                            </div>
                        </div>
                        <el-scrollbar style="overflow: auto;">
                            <div class="article-summary">
                                <div v-if="currentArticle">
                                    <div class="ai-summary-content-wrapper">
                                        <div v-if="aiSummary || isGeneratingSummary || isTyping"
                                            class="ai-summary-content" :class="{ 'streaming': isGeneratingSummary }">
                                            <span v-if="isGeneratingSummary && !aiSummary"
                                                class="generating-placeholder">
                                                {{ t('isGeneratingSummary') }}
                                            </span>
                                            <span v-else v-html="formattedSummary" class="summary-text"></span>
                                            <span v-if="isGeneratingSummary" class="cursor">|</span>
                                        </div>
                                        <div
                                            style="display: flex; justify-content: flex-end; align-items: center; margin-top: 10px;">
                                            <a-button v-if="isTyping" type="primary" size="small" shape="round"
                                                status="danger" @click="stopAISummaryRender(false)">
                                                <template #icon>
                                                    <icon-close />
                                                </template>
                                                {{ t('stopGenerating') }}
                                            </a-button>
                                            <a-button v-else type="primary" size="small" shape="round"
                                                :loading="isGeneratingSummary" :disabled="isGeneratingSummary"
                                                @click="regenerate_article_AISummary">
                                                <template #icon>
                                                    <icon-refresh />
                                                </template>
                                                {{ isGeneratingSummary ? t('isGeneratingSummary') : formattedSummary
                                                    ? t('regenerateSummary') : t('generateSummary')
                                                }}
                                            </a-button>
                                        </div>
                                    </div>
                                </div>
                                <div v-else class="summary-empty">
                                    <p>{{ t('selectArticle') }}</p>
                                </div>
                            </div>
                        </el-scrollbar>
                    </div>
                    <!-- 目录 -->
                    <div class="summary-tree">
                        <div class="sidebar-header">
                            <div class="sidebar-title-row">
                                <h3>{{ t('contents') }}</h3>
                            </div>
                        </div>
                        <el-scrollbar style="overflow: auto;">
                            <div class="article-summary">
                                <el-tree v-if="treeData && treeData.length > 0" :data="treeData" :props="{
                                    children: 'children',
                                    label: 'label'
                                }" @node-click="handleNodeClick" node-key="id" default-expand-all highlight-current
                                    class="summary-tree" />
                                <div v-else class="summary-empty">
                                    <p>{{ t('selectArticle') }}</p>
                                </div>
                            </div>
                        </el-scrollbar>
                    </div>
                </div>
            </transition>

            <!-- 文章内容 -->
            <div class="article-main">
                <div class="article-header">
                    <div class="article-title-row">
                        <h1 class="article-title">{{ currentArticle.title }}</h1>
                        <div class="article-tags">
                            <a-tag v-for="(tag, tagIndex) in currentArticle.tags" :key="tagIndex" color="#b71de8">
                                <template #icon>
                                    <icon-tag style="color: #fff;" />
                                </template>
                                {{ tag }}
                            </a-tag>
                        </div>
                    </div>
                    <div class="article-meta">
                        <div class="meta-left">
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
                        </div>
                        <div class="meta-right">
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

            <!-- 文章列表 -->
            <a-drawer :width="400" :visible="articleListDrawerVisible" @cancel="articleListDrawerVisible = false"
                :header="false" :footer="false" :drawer-style="{
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                }" unmountOnClose>
                <div class="article-sidebar-right" style="overflow: auto;">
                    <div class="sidebar-header">
                        <div class="sidebar-title-row"
                            style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                            <h3>{{ t('articleList') }}</h3>
                            <a-popover position="bottom">
                                <a-button type="primary" size="small" shape="round">
                                    <template #icon>
                                        <icon-tags />
                                    </template>
                                    {{ selectedCategory || t('allCategories') }}
                                </a-button>
                                <template #content>
                                    <a-doption @click="handleCategorySelect(null)">
                                        <template #icon>
                                            <icon-tag />
                                        </template>
                                        <span>{{ t('allCategories') }}</span> {{ articles.length
                                        }}
                                    </a-doption>
                                    <a-doption v-for="category in categories" :key="category"
                                        @click="handleCategorySelect(category)">
                                        <template #icon>
                                            <icon-tag />
                                        </template>
                                        {{ category }} {{
                                            getCategoryCount(category) }}
                                    </a-doption>
                                </template>
                            </a-popover>
                        </div>
                    </div>
                    <el-scrollbar style="overflow: auto;">
                        <div class="article-menu">
                            <div v-for="(article, index) in filteredArticles" :key="index" class="article-menu-item"
                                :class="{ 'active': currentArticleId === article.id }"
                                @click="selectArticle(article.id)">
                                <div class="article-item-header">
                                    <div class="article-menu-title">{{ article.title }}</div>
                                    <a-button v-if="admin_id" type="primary" size="small" shape="round" status="danger"
                                        class="delete-article-btn" @click.stop="handleDeleteArticle(article.id)" circle>
                                        <template #icon>
                                            <icon-delete />
                                        </template>
                                    </a-button>
                                </div>
                                <div class="article-menu-date">{{ formatTime(article.timeCreated) }}</div>
                                <div class="article-menu-tags">
                                    <a-tag v-for="(tag, tagIndex) in article.tags" :key="tagIndex" size="small">
                                        <template #icon>
                                            <icon-tag />
                                        </template>
                                        {{ tag }}
                                    </a-tag>
                                </div>
                            </div>
                        </div>
                    </el-scrollbar>
                </div>
            </a-drawer>
        </div>
    </el-main>

    <!-- 搜索弹窗 -->
    <transition name="modal-fade">
        <div v-if="searchDialogVisible" class="search-modal-overlay" @click="searchDialogVisible = false">
            <div class="search-modal" :style="{ width: isMobileRef ? '80%' : '40%' }" @click.stop>
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
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </transition>


    <!-- 删除确认弹窗 -->
    <Modal v-model:visible="deleteDialogVisible" type="delete" :title="t('deleteArticle')" :content="t('deleteConfirm')"
        @confirm="confirmDelete" @cancel="cancelDelete" />

    <!-- 右侧悬浮按钮 -->
    <a-tooltip :content="t('articleList')" position="left">
        <a-button type="primary" shape="circle" class="floating-add-btn btn1"
            @click="articleListDrawerVisible = !articleListDrawerVisible">
            <icon-double-left />
        </a-button>
    </a-tooltip>
    <a-tooltip :content="t('searchArticle')" position="left">
        <a-button type="primary" shape="circle" class="floating-add-btn btn2" @click="handleSearchArticle">
            <icon-search />
        </a-button>
    </a-tooltip>
    <a-tooltip :content="t('addArticle')" position="left">
        <a-button v-if="admin_id" type="primary" shape="circle" class="floating-add-btn btn3" @click="handleAddArticle">
            <icon-plus />
        </a-button>
    </a-tooltip>
    <a-tooltip :content="t('editArticle')" position="left">
        <a-button v-if="admin_id" type="primary" shape="circle" class="floating-add-btn btn4"
            @click="handleEditArticle(currentArticle.id)">
            <icon-edit />
        </a-button>
    </a-tooltip>
    <a-tooltip :content="currentArticle.isReleased ? t('setAsDraft') : t('publish')" position="left">
        <a-button v-if="admin_id" type="primary" shape="circle" class="floating-add-btn btn5"
            :style="{ background: currentArticle.isReleased ? '' : 'green' }"
            @click="handleDraftOrReleased(currentArticle.id)">
            <icon-save v-if="currentArticle.isReleased" />
            <icon-send v-else />
        </a-button>
    </a-tooltip>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { ElTree, ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import Cookies from 'js-cookie'

import { useMarkdown } from '@/hooks/useMarkdown'
import { request } from '@/api/request'
import { checkSessionId, calcHashForArticleId, getArticleIdFromHash, isMobile, countContent } from '@/utils/utils'
import Modal from '@/components/Modal.vue'
import { removeMarkdownSymbols } from '@/utils/markdown'

import aiIcon from '@/assets/ai.png';

// 路由
const route = useRoute()
const router = useRouter()

// 管理员ID
const admin_id = ref(null)

onMounted(async () => {
    admin_id.value = await checkSessionId()
    await getArticles()
    await routeArticle()
    // 添加键盘事件监听
    document.addEventListener('keydown', handleKeyDown)
})

const isSidebarCollapsed = ref(false)
const isMobileRef = ref(isMobile())

const { renderMarkdown } = useMarkdown()

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
        contents: '目录',
        AISummary: 'AI 总结',
        generateSummaryFailed: '生成 AI 总结失败',
        noContent: '文章内容为空',
        isGeneratingSummary: '生成中...',
        generateSummary: '生成 AI 总结',
        stopGenerating: '停止生成',
        regenerateSummary: '重新生成',
        generateSuccess: 'AI 总结生成成功',
        generateFailed: 'AI 总结生成失败',
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
        contents: 'Contents',
        AISummary: 'AI Summary',
        generateSummaryFailed: 'Failed to generate summary',
        noContent: 'Article content is empty',
        isGeneratingSummary: 'Generating...',
        generateSummary: 'Generate AI Summary',
        stopGenerating: 'Stop Generating',
        regenerateSummary: 'Regenerate',
        generateSuccess: 'AI Summary Generated',
        generateFailed: 'AI Summary Generation Failed',
    }
}

// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key
}

const articleListDrawerVisible = ref(true)

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
    }
    articleListDrawerVisible.value = true
}

// 摘要相关
const treeData = ref([])

// 生成文章目录树
const generateToc = (content, type) => {
    if (!content) return []
    let headings = []

    if (type === 1) {
        // 普通文本类型 - 提取包含 # 的行作为标题
        const lines = content.split('\n')
        lines.forEach((line, index) => {
            // 从两个 # 开始提取，一方面避免python语言注释，另一方面一级标题在本处渲染过大，不使用
            const match = line.match(/^(#{2,6})\s+(.+)$/)
            if (match) {
                const level = match[1].length
                const text = match[2].trim()
                headings.push({
                    level,
                    text,
                    lineIndex: index,
                    id: `heading-${index}`
                })
            }
        })
    } else if (type === 2) {
        // Markdown类型 - 使用正则提取标题
        const headingRegex = /^(#{2,6})\s+(.+)$/gm
        let match
        let lineIndex = 0

        while ((match = headingRegex.exec(content)) !== null) {
            const level = match[1].length
            const text = match[2].trim()
            // 计算行号
            const contentBefore = content.substring(0, match.index)
            lineIndex = contentBefore.split('\n').length - 1

            headings.push({
                level,
                text,
                lineIndex,
                id: `heading-${lineIndex}`
            })
        }
    }

    // 构建树形结构
    const tree = []
    const stack = []

    headings.forEach(heading => {
        const node = {
            id: heading.id,
            label: removeMarkdownSymbols(heading.text),
            lineIndex: heading.lineIndex,
            children: []
        }

        // 找到正确的父节点
        while (stack.length > 0 && stack[stack.length - 1].level >= heading.level) {
            stack.pop()
        }

        if (stack.length === 0) {
            tree.push(node)
        } else {
            stack[stack.length - 1].children.push(node)
        }

        stack.push({ ...node, level: heading.level })
    })

    return tree
}

// 点击目录节点跳转到对应位置
const handleNodeClick = (data) => {
    if (data.lineIndex !== undefined) {
        // 滚动到对应位置
        const contentElement = document.querySelector('.article-content-body')
        if (contentElement) {
            // 找到对应的标题元素
            const headings = contentElement.querySelectorAll('h2, h3, h4, h5, h6')
            const curr_heading = Array.from(headings).filter((item) => item.innerText === data.label)[0]
            if (curr_heading) {
                curr_heading.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                })
            }
        }
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
            const res = await request.post('/article/search_article', {
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
    // 停止当前的AI总结生成
    stopAISummaryRender()
    currentArticleId.value = id
    // 检查当前路由是否已经是这篇文章
    if (route.params.id !== id) {
        // 更新URL，但不重新加载页面
        const articleHash = calcHashForArticleId(id)
        router.push(`/articles/${articleHash}`)
    }
    articleListDrawerVisible.value = false
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

// 获取文章列表
const getArticles = async () => {
    try {
        const res = await request.post('/article/get_articles', {
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
        const res = await request.post('/article/get_article_content', {
            id: currentArticleId.value,
            lang: LANG
        })
        if (res.data.status !== 200) {
            console.log(res.data.message)
            return
        }
        currentArticle.value = res.data.article;
        // 生成目录树
        treeData.value = generateToc(currentArticle.value.content, currentArticle.value.type);
        // 生成AI摘要
        if (isCancelled.value) {
            setTimeout(async () => {
                await renderAISummary(currentArticle.value.aiSummary)
            }, 500)
            return
        }
        await renderAISummary(currentArticle.value.aiSummary)
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
    articleListDrawerVisible.value = false
    currentDeleteArticleId.value = articleId
    deleteDialogVisible.value = true
}

// 确认删除
const confirmDelete = async () => {
    if (!currentDeleteArticleId.value) return
    try {
        // 调用删除API
        const res = await request.post('/article/delete_article', {
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
        const res = await request.post('/article/change_article_status', {
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

// AI摘要相关
const aiSummary = ref('')
const isGeneratingSummary = ref(false)      // 是否在调用接口生成中
const isTyping = ref(false)                 // 是否在流式打印
const isCancelled = ref(false)              // 是否被取消
const formattedSummary = computed(() => {
    if (!aiSummary.value) return ''
    return aiSummary.value.replace(/\n/g, '<br>')
})

// DEBUG
// setInterval(() => {
//     console.log("isGeneratingSummary", isGeneratingSummary.value);
//     console.log("isTyping", isTyping.value);
//     console.log("isCancelled", isCancelled.value);
//     console.log("");
// }, 1000)

// 渲染AI总结
const renderAISummary = async (AISUMMARY) => {
    if (!currentArticle.value.content) {
        ElMessage.warning(t('noContent'))
        return
    }
    isTyping.value = true
    isCancelled.value = false // 重置取消标志
    aiSummary.value = ''

    try {
        if (AISUMMARY) {
            await streamEffect(AISUMMARY)
            return
        }
    } catch (error) {
        if (error.message === 'CANCELLED') {
            // 用户取消，不显示错误
            return
        }
        console.error('生成AI总结失败:', error)
        ElMessage.error(t('generateSummaryFailed'))
    } finally {
        isTyping.value = false
    }
}

// 停止AI总结渲染
const stopAISummaryRender = (clean = true) => {
    isCancelled.value = true // 设置取消标志
    isGeneratingSummary.value = false
    isTyping.value = false
    if (clean) {
        aiSummary.value = ''
    }
}

// 流式效果
const streamEffect = async (text) => {
    const chars = text.split('')
    let currentText = ''

    for (let i = 0; i < chars.length; i++) {
        // 检查是否被取消
        if (isCancelled.value) {
            // 通过抛出错误来取消Promise链
            throw new Error('CANCELLED')
        }

        currentText += chars[i]
        aiSummary.value = currentText

        // 根据字符类型调整延迟
        const delay = chars[i] === '\n' ? 100 : Math.random() * 30 + 20

        // 使用可取消的延迟
        await new Promise((resolve, reject) => {
            const timeoutId = setTimeout(() => {
                if (!isCancelled.value) {
                    resolve()
                } else {
                    reject(new Error('CANCELLED'))
                }
            }, delay)

            // 如果取消，立即拒绝Promise
            if (isCancelled.value) {
                clearTimeout(timeoutId)
                reject(new Error('CANCELLED'))
            }
        })
    }
    isTyping.value = false
}

const regenerate_article_AISummary = async () => {
    stopAISummaryRender()
    isGeneratingSummary.value = true
    try {
        const res = await request.post('/article/regenerate_article_AISummary', {
            id: currentArticle.value.id
        })
        if (res.data.status === 200 || res.data.status === 201) {
            ElMessage.success(t('generateSuccess'))
            isGeneratingSummary.value = false
            await renderAISummary(res.data.aiSummary)
        } else {
            ElMessage.error(res.data.message || t('generateFailed'))
        }
    } catch (error) {
        ElMessage.error(t('generateFailed'))
        console.error('重新生成AI总结失败:', error)
    }
}

onBeforeUnmount(() => {
    // 组件卸载时移除事件监听
    document.removeEventListener('keydown', handleKeyDown)
    // 组件卸载时取消正在进行的生成
    stopAISummaryRender()
    isCancelled.value = false;
})
</script>

<style scoped>
@import './index.css';
</style>