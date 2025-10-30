<template>
    <el-main class="editor-content">
        <div class="editor-container">
            <!-- 编辑器头部 -->
            <div class="editor-header">
                <h2>{{ isEdit ? t('editArticle') : t('addArticle') }}</h2>
            </div>

            <!-- 编辑表单 -->
            <el-form :model="articleForm" ref="formRef" label-position="top" class="article-form" @submit.prevent>
                <el-form-item v-if="language === 1 || language === 3" :label="t('tags')" prop="tags">
                    <div>
                        <el-tag v-for="tag in articleForm.tags" :key="tag" closable @close="removeTag(tag)"
                            class="article-tag" effect="dark">
                            {{ tag }}
                        </el-tag>
                        <el-input v-if="inputTagVisible" ref="tagInputRef" v-model="inputTagValue" class="tag-input"
                            size="small" @keydown.enter.prevent="addTag" @keyup.esc="cancelTagInput"
                            @blur="addTag"></el-input>
                        <el-button v-else class="add-tag-btn" size="small" @click="showTagInput">
                            + {{ t('addTag') }}
                        </el-button>
                    </div>
                </el-form-item>

                <el-form-item v-if="language === 2 || language === 3" label="Tags (English)" prop="tag_ENG">
                    <div>
                        <el-tag v-for="tag in articleForm.tag_ENG" :key="tag" closable @close="removeTagENG(tag)"
                            class="article-tag" effect="dark">
                            {{ tag }}
                        </el-tag>
                        <el-input v-if="inputTagENGVisible" ref="tagENGInputRef" v-model="inputTagENGValue"
                            class="tag-input" size="small" @keydown.enter.prevent="addTagENG"
                            @keyup.esc="cancelTagENGInput" @blur="addTagENG"></el-input>
                        <el-button v-else class="add-tag-btn" size="small" @click="showTagENGInput">
                            + Add Tag
                        </el-button>
                    </div>
                </el-form-item>

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
                        <el-form :model="articleForm" ref="contentFormRef" @submit.prevent>

                            <el-form-item prop="content">
                                <div v-if="articleForm.type === 2" class="markdown-toolbar">
                                    <el-tooltip v-for="(item, key) in markdownSign" :key="key"
                                        :content="item.description" placement="top">
                                        <el-button @click="insertMarkdown('content', key)" size="small"
                                            class="markdown-btn">
                                            {{ item.icon }}
                                        </el-button>
                                    </el-tooltip>
                                </div>
                                <el-input ref="contentInputRef" v-model="articleForm.content" type="textarea" :rows="33"
                                    @paste="handlePaste" :placeholder="t('contentPlaceholder')"></el-input>
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
                        <el-form :model="articleForm" ref="contentFormRef" @submit.prevent>
                            <div v-if="articleForm.type === 2" class="markdown-toolbar">
                                <el-tooltip v-for="(item, key) in markdownSign" :key="key" :content="item.description"
                                    placement="top">
                                    <el-button @click="insertMarkdown('content_ENG', key)" size="small"
                                        class="markdown-btn">
                                        {{ item.icon }}
                                    </el-button>
                                </el-tooltip>
                            </div>
                            <el-form-item prop="content_ENG">
                                <el-input ref="contentENGInputRef" v-model="articleForm.content_ENG" type="textarea"
                                    @paste="handlePaste" :rows="33" :placeholder="t('contentPlaceholder')"></el-input>
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
import { ref, reactive, onMounted, onBeforeUnmount, nextTick, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { request } from '../../api/request'
import { useMarkdown } from '../../hooks/useMarkdown'
import Cookies from 'js-cookie'
import { checkSessionId } from '../../utils/utils'
import { Message } from '@arco-design/web-vue'

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

    // 添加键盘事件监听
    document.addEventListener('keydown', handleKeyDown)
})

const { markdownSign, renderMarkdown, formatMarkdownByPrettier } = useMarkdown()

// Command(Ctrl)+S 保存
const handleKeyDown = async (event) => {
    // 保存
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        // 阻止默认的保存行为
        event.preventDefault()
        await formRef.value.validate(async (valid) => {
            if (!valid) return
            if (articleForm.content === "" && articleForm.content_ENG === "") {
                Message.warning("请输入文章内容")
                return
            }

            try {
                // 格式化 Markdown 内容
                articleForm.content = await formatMarkdownByPrettier(articleForm.content)
                articleForm.content_ENG = await formatMarkdownByPrettier(articleForm.content_ENG)

                const apiUrl = '/article/update_article'
                const requestData = {
                    ...articleForm,
                    isReleased: false,
                }

                const res = await request.post(apiUrl, requestData)

                if (res.data.status === 200) {
                    Message.success(t('saveSuccess'))
                } else if (res.data.status === -1) {
                    Message.warning(res.data.message)
                } else {
                    Message.error(res.data.message || t('saveFailed'))
                }
            } catch (error) {
                console.error('暂存失败:', error)
                Message.error(t('saveFailed'))
            }
        })
    }
    // 格式化 Markdown 内容
    if ((event.metaKey || event.ctrlKey) && event.altKey && articleForm.type === 2) {
        event.preventDefault()
        if (event.key === 'l' || event.key === '¬' || event.code === 'KeyL') {
            articleForm.content = await formatMarkdownByPrettier(articleForm.content)
            articleForm.content_ENG = await formatMarkdownByPrettier(articleForm.content_ENG)
            Message.success(t('formatted'))
        }
    }
}

// 组件卸载时移除事件监听
onBeforeUnmount(() => {
    document.removeEventListener('keydown', handleKeyDown)
})

// 多语言支持
const LANG = localStorage.getItem("LANG") || "Chinese"
const translations = {
    Chinese: {
        addArticle: '新文章',
        editArticle: '编辑文章',
        tags: '标签',
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
        formatted: '格式化成功',
    },
    English: {
        addArticle: 'New Article',
        editArticle: 'Edit Article',
        tags: 'Tags',
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
        formatted: 'Formatted successfully',
    }
}

// 翻译函数
const t = (key) => {
    return translations[LANG][key] || key
}

// Markdown快捷键部分
const contentInputRef = useTemplateRef("contentInputRef")
const contentENGInputRef = useTemplateRef("contentENGInputRef")

// 在光标位置插入文本的通用函数
const insertAtCursor = (text, field = null) => {
    // 如果没有指定field，则根据当前语言设置自动判断
    let targetField = field
    if (!targetField) {
        // 根据当前激活的输入框来判断
        const activeElement = document.activeElement
        if (activeElement === contentENGInputRef.value?.$el?.querySelector('textarea')) {
            targetField = 'content_ENG'
        } else {
            targetField = 'content'
        }
    }

    const textareaRef = targetField === 'content_ENG' ? contentENGInputRef : contentInputRef
    const textarea = textareaRef.value?.$el?.querySelector('textarea') || textareaRef.value

    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const currentValue = articleForm[targetField] || ''

    // 在光标位置插入文本
    const newValue = currentValue.substring(0, start) + text + currentValue.substring(end)
    articleForm[targetField] = newValue

    // 设置新的光标位置
    nextTick(() => {
        textarea.focus()
        const newCursorPos = start + text.length
        textarea.setSelectionRange(newCursorPos, newCursorPos)
    })
}

const insertMarkdown = (field, type) => {
    const textareaRef = field === 'content_ENG' ? contentENGInputRef : contentInputRef
    const textarea = textareaRef.value?.$el?.querySelector('textarea') || textareaRef.value
    if (!textarea) return

    // 先聚焦到对应的文本框
    textarea.focus()

    // 使用insertAtCursor函数插入Markdown标记
    nextTick(() => {
        const insertion = markdownSign[type].sign
        insertAtCursor(insertion, field)
    })
}

// 表单引用
const formRef = useTemplateRef("formRef")

const language = ref(1)

// 文章表单数据
const articleForm = reactive({
    id: '',
    tags: [],
    tag_ENG: [],
    type: 2, // 默认为Markdown
    content: '',
    content_ENG: '',
})

// 标签输入相关
const inputTagVisible = ref(false)
const inputTagValue = ref('')
const tagInputRef = ref(null)

// 英文标签输入相关
const inputTagENGVisible = ref(false)
const inputTagENGValue = ref('')
const tagENGInputRef = ref(null)

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

// 取消标签输入
const cancelTagInput = () => {
    inputTagVisible.value = false
    inputTagValue.value = ''
}

// 显示英文标签输入框
const showTagENGInput = () => {
    inputTagENGVisible.value = true
    nextTick(() => {
        tagENGInputRef.value.focus()
    })
}

// 取消英文标签输入
const cancelTagENGInput = () => {
    inputTagENGVisible.value = false
    inputTagENGValue.value = ''
}


// 添加标签
const addTag = (event) => {
    // 如果有事件对象，阻止默认行为
    if (event && event.preventDefault) {
        event.preventDefault()
    }
    const value = inputTagValue.value.trim()
    if (value) {
        // 限制标签长度
        if (value.length > 20) {
            Message.warning('标签长度不能超过20个字符')
            inputTagValue.value = value.substring(0, 20)
            return
        }

        if (!articleForm.tags.includes(value)) {
            // 限制标签数量
            if (articleForm.tags.length >= 4) {
                Message.warning('最多只能添加4个标签')
                inputTagVisible.value = false
                inputTagValue.value = ''
                return
            }

            articleForm.tags.push(value)
            inputTagVisible.value = false
            inputTagValue.value = ''
        } else {
            // 提示用户标签已存在
            Message.warning('标签已存在')
            inputTagValue.value = ''
            nextTick(() => {
                tagInputRef.value.focus()
            })
        }
    } else {
        // 空值时关闭输入框
        inputTagVisible.value = false
        inputTagValue.value = ''
    }
}

// 添加英文标签
const addTagENG = (event) => {
    // 如果有事件对象，阻止默认行为
    if (event && event.preventDefault) {
        event.preventDefault()
    }
    const value = inputTagENGValue.value.trim()
    if (value) {
        // 限制标签长度
        if (value.length > 20) {
            Message.warning('Tag length cannot exceed 20 characters')
            inputTagENGValue.value = value.substring(0, 20)
            return
        }

        if (!articleForm.tag_ENG.includes(value)) {
            // 限制标签数量
            if (articleForm.tag_ENG.length >= 4) {
                Message.warning('You can only add up to 4 tags')
                inputTagENGVisible.value = false
                inputTagENGValue.value = ''
                return
            }

            articleForm.tag_ENG.push(value)
            inputTagENGVisible.value = false
            inputTagENGValue.value = ''
        } else {
            // 提示用户标签已存在
            Message.warning('Tag already exists')
            inputTagENGValue.value = ''
            nextTick(() => {
                tagENGInputRef.value.focus()
            })
        }
    } else {
        // 空值时关闭输入框
        inputTagENGVisible.value = false
        inputTagENGValue.value = ''
    }
}

// 移除标签
const removeTag = (tag) => {
    articleForm.tags = articleForm.tags.filter(t => t !== tag)
}

// 移除英文标签
const removeTagENG = (tag) => {
    articleForm.tag_ENG = articleForm.tag_ENG.filter(t => t !== tag)
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
            Message.warning("请输入文章内容")
            return
        }

        saving.value = true
        try {
            const apiUrl = isEdit.value ? '/article/update_article' : '/article/add_article'
            const requestData = {
                ...articleForm,
                isReleased: false,
            }

            const res = await request.post(apiUrl, requestData)

            if (res.data.status === 200) {
                Message.success(t('saveSuccess'))
                router.push('/articles')
            } else if (res.data.status === -1) {
                Message.warning(res.data.message)
            } else {
                Message.error(res.data.message || t('saveFailed'))
            }
        } catch (error) {
            console.error('保存草稿失败:', error)
            Message.error(t('saveFailed'))
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
            Message.warning("请输入文章内容")
            return
        }

        saving.value = true
        try {
            const apiUrl = isEdit.value ? '/article/update_article' : '/article/add_article'
            const requestData = {
                ...articleForm,
                isReleased: true,
            }

            const res = await request.post(apiUrl, requestData)

            if (res.data.status === 200) {
                Message.success("发布成功")
                router.push('/articles')
            } else if (res.data.status === -1) {
                Message.warning(res.data.message)
            } else {
                Message.error(res.data.message || "发布失败")
            }
        } catch (error) {
            console.error('发布文章失败:', error)
            Message.error("发布失败")
        } finally {
            saving.value = false
        }
    })
}

// 检查管理员权限
const checkAdminPermission = async () => {
    const admin_id = await checkSessionId()
    if (!admin_id) {
        Message.error(t('unauthorized'))
        router.push('/articles')
    }
}

// 获取文章详情（编辑模式）
const getArticleDetail = async (id) => {
    try {
        const res = await request.post('/article/get_article_detail', {
            id,
        })
        if (res.data.status === 200) {
            const article = res.data.article
            articleForm.id = article.id
            articleForm.tags = article.tags || []
            articleForm.tag_ENG = article.tag_ENG || []
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
        Message.error(error.message || '获取文章详情失败')
    }
}


// 图片插入逻辑
const handlePaste = async (event) => {
    const items = event.clipboardData?.items || []

    for (const item of items) {
        // 检测粘贴内容是否为图片类型
        if (item.type.indexOf("image") !== -1) {
            event.preventDefault()
            const file = item.getAsFile()
            if (!file) return

            const formData = new FormData()
            formData.append("image", file)
            try {
                const res = await request.post("/article/upload_image", formData)

                if (res.data.status === 200) {
                    const image_url = res.data.image_url
                    insertAtCursor(`![${file.name}](${image_url}?x-oss-process=image/resize,w_800)`)
                } else {
                    alert(res.data.message || "上传失败")
                }
            } catch (err) {
                console.error(err)
                alert("上传出错")
            }
        }
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
    /* background: rgba(255, 255, 255, 0.08); */
    /* backdrop-filter: blur(20px); */
    /* border-radius: 16px; */
    /* border: 1px solid rgba(255, 255, 255, 0.15); */
    /* box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); */
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
    margin-right: 10px;
    background: rgba(245, 158, 11, 0.2);
    border-color: rgba(245, 158, 11, 0.6);
    color: #F59E0B;
}

.tag-input {
    background: rgba(245, 158, 11, 0.2);
    color: #F59E0B;
    width: 180px;
    margin-right: 10px;
}

.tag-input :deep(.el-input__inner) {
    color: #F59E0B;
}

@media (max-width: 768px) {
    .tag-input {
        width: 140px;
    }
}

.add-tag-btn {
    background: rgba(245, 158, 11, 0.2);
    border: 1px dashed rgba(245, 158, 11, 0.6);
    color: #F59E0B;
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
    height: 916px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 8px;
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

.markdown-toolbar {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(9, 1fr);
    gap: 8px;
    margin-bottom: 10px;
    padding: 8px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    justify-items: center;
    /* 水平居中每个格子内的按钮 */
    align-items: center;
    /* 垂直居中每个格子内的按钮 */
}

.markdown-btn {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #ffffff;
    font-weight: 600;
    font-size: 16px;
    margin-left: 0;
    /* 固定 icon 字体大小 */
    transition: all 0.2s ease;
}


.markdown-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
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
