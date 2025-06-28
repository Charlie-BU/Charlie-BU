<template>
    <el-main class="editor-content">
        <div class="editor-container">
            <!-- 编辑器头部 -->
            <div class="editor-header">
                <h2>{{ isEdit ? t('editArticle') : t('addArticle') }}</h2>
            </div>

            <!-- 编辑表单 -->
            <el-form :model="articleForm" ref="formRef" label-position="top" class="article-form">
                <!-- <el-form-item :label="t('tags')" prop="tags">
                    <el-tag v-for="tag in articleForm.tags" :key="tag" closable @close="removeTag(tag)"
                        class="article-tag" effect="dark">
                        {{ tag }}
                    </el-tag>
                    <el-input v-if="inputTagVisible" ref="tagInputRef" v-model="inputTagValue" class="tag-input"
                        size="small" @keyup.enter="addTag" @blur="addTag" :placeholder="t('tagPlaceholder')"></el-input>
                    <el-button v-else class="add-tag-btn" size="small" @click="showTagInput">
                        + {{ t('addTag') }}
                    </el-button>
                </el-form-item> -->

                <el-form-item :label="t('type')" prop="type">
                    <el-radio-group v-model="articleForm.type">
                        <el-radio :label="1">{{ t('textType') }}</el-radio>
                        <el-radio :label="2">{{ t('markdownType') }}</el-radio>
                    </el-radio-group>
                </el-form-item>

                <el-form-item :label="t('language')" prop="language">
                    <el-radio-group v-model="language">
                        <el-radio :label="1">仅中文</el-radio>
                        <el-radio :label="2">English Only</el-radio>
                        <el-radio :label="3">中英文 Both</el-radio>
                    </el-radio-group>
                </el-form-item>
            </el-form>
            <div v-if="language === 1 || language === 3">
                <div style="text-align: left; font-size: 16.8px;">内容（中文）</div>
                <div class="content-preview-container">
                    <!-- 内容编辑区 -->
                    <div class="content-editor">
                        <el-form :model="articleForm" ref="contentFormRef">
                            <el-form-item prop="content">
                                <el-input v-model="articleForm.content" type="textarea" :rows="33"
                                    :placeholder="t('contentPlaceholder')"></el-input>
                            </el-form-item>
                        </el-form>
                    </div>

                    <!-- Markdown 预览 -->
                    <div v-if="articleForm.type === 2" class="markdown-preview">
                        <div class="preview-header">
                            <h3>{{ t('preview') }}</h3>
                        </div>
                        <div class="preview-content" v-html="renderMarkdown(articleForm.content)"></div>
                    </div>
                </div>
            </div>
            <div v-if="language === 2 || language === 3">
                <div style="text-align: left; font-size: 16.8px;">Content (English)</div>
                <div class="content-preview-container">
                    <!-- 内容编辑区 -->
                    <div class="content-editor">
                        <el-form :model="articleForm" ref="contentFormRef">
                            <el-form-item prop="content_ENG">
                                <el-input v-model="articleForm.content_ENG" type="textarea" :rows="33"
                                    :placeholder="t('contentPlaceholder')"></el-input>
                            </el-form-item>
                        </el-form>
                    </div>

                    <!-- Markdown 预览 -->
                    <div v-if="articleForm.type === 2" class="markdown-preview">
                        <div class="preview-header">
                            <h3>{{ t('preview') }}</h3>
                        </div>
                        <div class="preview-content" v-html="renderMarkdown(articleForm.content_ENG)"></div>
                    </div>
                </div>
            </div>
            <!-- 底部控制按钮 -->
            <div class="editor-footer">
                <div class="editor-actions">
                    <el-button @click="goBack" size="large" class="charlie-btn charlie-btn-default">
                        {{ t('cancel') }}
                    </el-button>
                    <el-button type="primary" @click="saveAsDraft" size="large" :loading="saving"
                        class="charlie-btn charlie-btn-primary">
                        {{ t('saveDraft') }}
                    </el-button>
                    <el-button type="success" @click="publishArticle" size="large" :loading="saving"
                        class="charlie-btn charlie-btn-success">
                        {{ t('publish') }}
                    </el-button>
                </div>
            </div>
        </div>
    </el-main>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { request } from '../api/request'
import MarkdownIt from 'markdown-it'
import Cookies from 'js-cookie'

// 初始化markdown-it
const markdown = new MarkdownIt()

// 路由
const route = useRoute()
const router = useRouter()

onMounted(async () => {
    // 检查管理员权限
    await checkAdminPermission()

    // 判断是新增还是编辑
    const articleId = route.params.id
    if (articleId) {
        isEdit.value = true
        await getArticleDetail(articleId)
    }
})

// 多语言支持
const LANG = localStorage.getItem("LANG") || "Chinese"
const translations = {
    Chinese: {
        addArticle: '新文章',
        editArticle: '编辑文章',
        tags: '标签',
        tagPlaceholder: '输入标签并按回车',
        addTag: '添加标签',
        type: '类型',
        language: '语言',
        textType: '文本',
        markdownType: 'Markdown',
        content: '内容',
        contentPlaceholder: '请输入文章内容',
        preview: '预览',
        saveDraft: '存草稿',
        publish: '发布',
        save: '保存',
        cancel: '返回',
        saveSuccess: '保存成功',
        saveFailed: '保存失败',
        confirmLeave: '您有未保存的更改，确定要离开吗？',
        unauthorized: '未授权，请先登录',
    },
    English: {
        addArticle: 'New Article',
        editArticle: 'Edit Article',
        tags: 'Tags',
        tagPlaceholder: 'Enter tag and press Enter',
        addTag: 'Add Tag',
        type: 'Type',
        language: 'Language',
        textType: 'Plain Text',
        markdownType: 'Markdown',
        content: 'Content',
        contentPlaceholder: 'Enter article content',
        preview: 'Preview',
        saveDraft: 'Save Draft',
        publish: 'Publish',
        save: 'Save',
        cancel: 'Back',
        saveSuccess: 'Saved successfully',
        saveFailed: 'Save failed',
        confirmLeave: 'You have unsaved changes. Are you sure you want to leave?',
        unauthorized: 'Unauthorized, please login first',
    }
}

// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key
}

// 表单引用
const formRef = ref(null)

const language = ref(1)

// 文章表单数据
const articleForm = reactive({
    id: '',
    tags: [],
    type: 2, // 默认为Markdown
    content: '',
    content_ENG: '',
})

// 标签输入相关
const inputTagVisible = ref(false)
const inputTagValue = ref('')
const tagInputRef = ref(null)

// 保存状态
const saving = ref(false)

// 是否为编辑模式
const isEdit = ref(false)

// 显示标签输入框
const showTagInput = () => {
    inputTagVisible.value = true
    nextTick(() => {
        tagInputRef.value.focus()
    })
}

// 添加标签
const addTag = () => {
    if (inputTagValue.value) {
        if (!articleForm.tags.includes(inputTagValue.value)) {
            articleForm.tags.push(inputTagValue.value)
        }
    }
    inputTagVisible.value = false
    inputTagValue.value = ''
}

// 移除标签
const removeTag = (tag) => {
    articleForm.tags = articleForm.tags.filter(t => t !== tag)
}

// Markdown渲染函数
const renderMarkdown = (content) => {
    return markdown.render(content || '')
}

// 返回文章列表
const goBack = () => {
    router.push('/articles')
}

// 存为草稿
const saveAsDraft = async () => {
    // 表单验证
    await formRef.value.validate(async (valid) => {
        if (!valid) return
        if (articleForm.content === "" && articleForm.content_ENG === "") {
            ElMessage.warning("请输入文章内容")
            return
        }

        saving.value = true
        try {
            const apiUrl = isEdit.value ? '/api/update_article' : '/api/add_article'
            const requestData = {
                ...articleForm,
                isReleased: false,
            }

            const res = await request.post(apiUrl, requestData)

            if (res.data.status === 200) {
                ElMessage.success(t('saveSuccess'))
                router.push('/articles')
            } else if (res.data.status === -1) {
                ElMessage.warning(res.data.message)
            } else {
                ElMessage.error(res.data.message || t('saveFailed'))
            }
        } catch (error) {
            console.error('保存草稿失败:', error)
            ElMessage.error(t('saveFailed'))
        } finally {
            saving.value = false
        }
    })
}

const publishArticle = async () => {
    // 表单验证
    await formRef.value.validate(async (valid) => {
        if (!valid) return
        if (articleForm.content === "" && articleForm.content_ENG === "") {
            ElMessage.warning("请输入文章内容")
            return
        }

        saving.value = true
        try {
            const apiUrl = isEdit.value ? '/api/update_article' : '/api/add_article'
            const requestData = {
                ...articleForm,
                isReleased: true,
            }

            const res = await request.post(apiUrl, requestData)

            if (res.data.status === 200) {
                ElMessage.success("发布成功")
                router.push('/articles')
            } else if (res.data.status === -1) {
                ElMessage.warning(res.data.message)
            } else {
                ElMessage.error(res.data.message || "发布失败")
            }
        } catch (error) {
            console.error('发布文章失败:', error)
            ElMessage.error("发布失败")
        } finally {
            saving.value = false
        }
    })
}

// 检查管理员权限
const checkAdminPermission = async () => {
    try {
        const res = await request.post('/api/check_sessionid', {
            sessionid: Cookies.get('sessionid')
        })
        if (res.data.status !== 200 || !res.data.admin_id) {
            ElMessage.error(t('unauthorized'))
            router.push('/articles')
        }
    } catch (error) {
        console.error('检查管理员权限失败:', error)
        ElMessage.error(t('unauthorized'))
        router.push('/articles')
    }
}

// 获取文章详情（编辑模式）
const getArticleDetail = async (id) => {
    try {
        const res = await request.post('/api/get_article_detail', {
            id,
        })
        if (res.data.status === 200) {
            const article = res.data.article
            articleForm.id = article.id
            articleForm.tags = article.tags || []
            articleForm.type = article.type
            articleForm.content = article.content
            articleForm.content_ENG = article.content_ENG
        }
        if (articleForm.content && articleForm.content_ENG) {
            language.value = 3
        } else if (articleForm.content) {
            language.value = 1
        } else if (articleForm.content_ENG) {
            language.value = 2
        }
    } catch (error) {
        console.error('获取文章详情失败:', error)
        ElMessage.error(error.message || '获取文章详情失败')
    }
}
</script>

<style scoped>
.editor-content {
    max-width: 1500px;
    margin: 0 auto;
    padding: 40px 20px;
}

.editor-container {
    display: flex;
    flex-direction: column;
    gap: 30px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    padding: 30px;
}

.editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.editor-header h2 {
    margin: 0;
    color: #ffffff;
    font-size: 1.6rem;
    font-weight: 600;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.editor-actions {
    display: flex;
    gap: 10px;
}

.article-form {
    margin-top: 20px;
}

.article-tag {
    margin-right: 8px;
    margin-bottom: 8px;
    background: rgba(139, 92, 246, 0.3);
    border-color: rgba(139, 92, 246, 0.5);
    color: #A78BFA;
}

.tag-input {
    width: 100px;
    margin-right: 8px;
    vertical-align: bottom;
}

.add-tag-btn {
    background: rgba(139, 92, 246, 0.2);
    border: 1px dashed rgba(139, 92, 246, 0.5);
    color: #A78BFA;
}

/* 内容和预览的左右布局容器 */
.content-preview-container {
    display: flex;
    gap: 20px;
    margin-top: 20px;
}

/* 内容编辑区 */
.content-editor {
    flex: 1;
    min-width: 0;
}

/* Markdown预览区 */
.markdown-preview {
    flex: 1;
    min-height: 490px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    max-height: 800px;
    overflow: auto;
    overflow-y: auto;
    text-align: justify;
}

/* 响应式设计 - 在小屏幕上恢复为上下布局 */
@media (max-width: 992px) {
    .content-preview-container {
        flex-direction: column;
    }

    .content-editor,
    .markdown-preview {
        width: 100%;
    }
}

.preview-header {
    padding: 15px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.preview-header h3 {
    margin: 0;
    color: #ffffff;
    font-size: 1.1rem;
    font-weight: 600;
}

.preview-content {
    padding: 20px;
    color: rgba(255, 255, 255, 0.92);
    line-height: 1.6;
    font-size: 0.95rem;
}

/* 添加Markdown预览样式 */
.preview-content :deep(h1) {
    font-size: 1.5rem;
    margin-top: 1.2em;
    margin-bottom: 0.7em;
    font-weight: 600;
    color: #ffffff;
}

.preview-content :deep(h2) {
    font-size: 1.3rem;
    margin-top: 1.2em;
    margin-bottom: 0.7em;
    font-weight: 600;
    color: #ffffff;
}

.preview-content :deep(h3) {
    font-size: 1.15rem;
    margin-top: 1.1em;
    margin-bottom: 0.6em;
    font-weight: 600;
    color: #ffffff;
}

.preview-content :deep(h4),
.preview-content :deep(h5),
.preview-content :deep(h6) {
    font-size: 1rem;
    margin-top: 1em;
    margin-bottom: 0.5em;
    font-weight: 600;
    color: #ffffff;
}

.preview-content :deep(p) {
    margin-bottom: 0.8em;
    font-size: 0.95rem;
}

.preview-content :deep(a) {
    color: #A78BFA;
    text-decoration: none;
}

.preview-content :deep(a:hover) {
    text-decoration: underline;
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
    padding-left: 2em;
    margin-bottom: 1em;
}

.preview-content :deep(blockquote) {
    border-left: 4px solid rgba(139, 92, 246, 0.5);
    padding-left: 1em;
    margin-left: 0;
    margin-right: 0;
    font-style: italic;
    color: rgba(255, 255, 255, 0.7);
}

.preview-content :deep(code) {
    background: rgba(0, 0, 0, 0.2);
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: monospace;
    font-size: 0.85em;
}

.preview-content :deep(pre) {
    background: rgba(0, 0, 0, 0.2);
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    margin-bottom: 1em;
}

.preview-content :deep(pre code) {
    background: none;
    padding: 0;
}

.preview-content :deep(table) {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1em;
}

.preview-content :deep(th),
.preview-content :deep(td) {
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.5em;
}

.preview-content :deep(th) {
    background: rgba(0, 0, 0, 0.2);
}

/* 表单内的输入框样式覆盖 */
:deep(.el-input__inner),
:deep(.el-textarea__inner) {
    background-color: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: white;
    font-size: 1rem;
    /* 增大输入框字体大小 */
}

:deep(.el-input__inner::placeholder),
:deep(.el-textarea__inner::placeholder) {
    font-size: 1rem;
    /* 增大placeholder字体大小 */
    color: rgba(255, 255, 255, 0.6);
    /* 提高placeholder可见度 */
}

:deep(.el-input__inner:focus),
:deep(.el-textarea__inner:focus) {
    border-color: #A78BFA;
    box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.2);
}

:deep(.el-form-item__label) {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.05rem;
    /* 增大表单标签字体大小 */
    margin-bottom: 6px;
    /* 增加标签与输入框的间距 */
}

:deep(.el-radio__label) {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1rem;
    /* 增大单选按钮标签字体大小 */
}

:deep(.el-radio__input.is-checked .el-radio__inner) {
    background-color: #A78BFA;
    border-color: #A78BFA;
}

:deep(.el-radio__input.is-checked+.el-radio__label) {
    color: #A78BFA;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .editor-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .editor-actions {
        width: 100%;
        justify-content: flex-end;
    }
}

.editor-footer {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.15);
}

.editor-footer .editor-actions {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .editor-footer .editor-actions {
        flex-direction: column;
        width: 100%;
    }

    .editor-footer .el-button {
        width: 100%;
        margin-bottom: 10px;
    }
}

/* 所有底部按钮的基础样式 */
.editor-footer .el-button {
    padding: 12px 24px;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.3s ease;
    border: none;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
