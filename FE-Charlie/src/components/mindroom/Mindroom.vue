<template>
    <div class="mindroom-container">
        <!-- 房间列表页面 -->
        <div v-if="!roomId" class="room-list-container">
            <div class="room-list-header">
                <h1>{{ t('mindroom') }}</h1>
                <p>{{ t('mindroomDesc') }}</p>
                <el-button type="primary" @click="createNewRoom" class="create-room-btn">
                    {{ t('createRoom') }}
                </el-button>
            </div>

            <div class="room-list">
                <el-empty v-if="rooms.length === 0" :description="t('noRooms')" />
                <div v-else class="room-grid">
                    <div v-for="room in rooms" :key="room.id" class="room-card" @click="enterRoom(room.id)">
                        <div class="room-card-header">
                            <h3>{{ room.title || t('untitledRoom') }}</h3>
                            <span class="room-id">#{{ room.id }}</span>
                        </div>
                        <p class="room-description">{{ room.description || t('noDescription') }}</p>
                        <div class="room-footer">
                            <span class="room-members">
                                <el-icon>
                                    <User />
                                </el-icon> {{ room.memberCount || 0 }}
                            </span>
                            <span class="room-created">{{ formatDate(room.createdAt) }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 房间详情页面 -->
        <div v-else class="room-detail-container">
            <div class="room-header">
                <div class="room-title-section">
                    <div class="room-back">
                        <el-button @click="backToList" text>
                            <el-icon>
                                <ArrowLeft />
                            </el-icon>
                        </el-button>
                    </div>
                    <div v-if="isEditing" class="room-title-edit">
                        <el-input v-model="editingRoom.title" :placeholder="t('roomTitle')" />
                        <el-input v-model="editingRoom.subtitle" :placeholder="t('roomSubtitle')" />
                    </div>
                    <div v-else class="room-title-display">
                        <h2>{{ currentRoom.title || t('untitledRoom') }}</h2>
                        <p v-if="currentRoom.subtitle">{{ currentRoom.subtitle }}</p>
                    </div>
                </div>
                <div class="room-actions">
                    <el-button v-if="isOwner && !isEditing" @click="startEditing" type="primary" plain>
                        {{ t('editRoom') }}
                    </el-button>
                    <template v-if="isEditing">
                        <el-button @click="cancelEditing">{{ t('cancel') }}</el-button>
                        <el-button type="primary" @click="saveRoomSettings">{{ t('save') }}</el-button>
                    </template>
                    <el-button @click="shareRoom" type="success" plain>
                        {{ t('share') }}
                    </el-button>
                </div>
            </div>

            <div class="room-content">
                <!-- 文档编辑区 -->
                <div class="document-pane">
                    <div class="document-toolbar">
                        <div class="editor-mode-toggle">
                            <el-radio-group v-model="editorMode" size="small">
                                <el-radio-button label="markdown">{{ t('markdown') }}</el-radio-button>
                            </el-radio-group>
                        </div>
                        <div class="document-actions">
                            <el-tooltip :content="t('autoSave')" placement="top">
                                <span class="auto-save-indicator">
                                    <el-icon>
                                        <Check />
                                    </el-icon> {{ t('autoSaved') }}
                                </span>
                            </el-tooltip>
                        </div>
                    </div>
                    <div class="document-editor">
                        <!-- Markdown编辑器 -->
                        <div class="markdown-editor">
                            <div class="markdown-toolbar">

                            </div>
                            <textarea ref="markdownEditor" v-model="documentContent" :placeholder="t('startTyping')"
                                style="min-height: calc(100vh - 120px);" @input="handleDocumentChange"></textarea>
                        </div>
                    </div>
                </div>

                <!-- Markdown预览区 -->
                <div class="markdown-preview-pane">
                    <div class="markdown-preview" v-html="renderMarkdown(documentContent)"></div>
                </div>
            </div>
        </div>

        <!-- 创建房间对话框 -->
        <el-dialog v-model="showCreateDialog" :title="t('createNewRoom')" width="500px">
            <el-form :model="newRoom" label-position="top">
                <el-form-item :label="t('roomTitle')">
                    <el-input v-model="newRoom.title" :placeholder="t('roomTitlePlaceholder')"></el-input>
                </el-form-item>
                <el-form-item :label="t('roomDescription')">
                    <el-input v-model="newRoom.description" type="textarea" :rows="3"
                        :placeholder="t('roomDescPlaceholder')"></el-input>
                </el-form-item>
                <el-form-item :label="t('roomAccess')">
                    <el-radio-group v-model="newRoom.isPublic">
                        <el-radio :label="true">{{ t('public') }}</el-radio>
                        <el-radio :label="false">{{ t('private') }}</el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item :label="t('guestPermissions')">
                    <el-radio-group v-model="newRoom.guestCanWrite">
                        <el-radio :label="true">{{ t('readWrite') }}</el-radio>
                        <el-radio :label="false">{{ t('readOnly') }}</el-radio>
                    </el-radio-group>
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showCreateDialog = false">{{ t('cancel') }}</el-button>
                <el-button type="primary" @click="confirmCreateRoom">{{ t('create') }}</el-button>
            </template>
        </el-dialog>

        <!-- 分享房间对话框 -->
        <el-dialog v-model="showShareDialog" :title="t('shareRoom')" width="500px">
            <div class="share-content">
                <p>{{ t('shareRoomDesc') }}</p>
                <el-input v-model="shareLink" readonly class="share-link-input">
                    <template #append>
                        <el-button @click="copyShareLink">{{ t('copy') }}</el-button>
                    </template>
                </el-input>
            </div>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import MarkdownIt from 'markdown-it'

// 初始化markdown-it
const markdown = new MarkdownIt()

// 路由
const route = useRoute()
const router = useRouter()

// 语言设置
const LANG = ref(localStorage.getItem("LANG") || "Chinese")

// 翻译
const translations = reactive({
    Chinese: {
        mindroom: '灵感空间',
        mindroomDesc: '创建和分享你的想法，与他人实时协作',
        createRoom: '创建房间',
        untitledRoom: '未命名房间',
        noDescription: '暂无描述',
        noRooms: '暂无房间',
        roomTitle: '房间标题',
        roomSubtitle: '房间副标题',
        editRoom: '编辑房间',
        share: '分享',
        cancel: '取消',
        save: '保存',
        richText: '富文本',
        markdown: 'Markdown',
        autoSave: '自动保存',
        autoSaved: '已自动保存',
        startTyping: '开始输入...',
        noMessages: '暂无消息',
        typeMessage: '输入消息...',
        send: '发送',
        insertEmoji: '插入表情',
        insertCode: '插入代码',
        quoteDocument: '引用文档',
        createNewRoom: '创建新房间',
        roomTitlePlaceholder: '输入房间标题',
        roomDescription: '房间描述',
        roomDescPlaceholder: '输入房间描述',
        roomAccess: '访问权限',
        public: '公开',
        private: '私密',
        guestPermissions: '访客权限',
        readWrite: '可读写',
        readOnly: '仅可读',
        create: '创建',
        shareRoom: '分享房间',
        shareRoomDesc: '复制以下链接分享给他人',
        copy: '复制',
        copySuccess: '复制成功',
        roomCreated: '房间创建成功',
        roomUpdated: '房间设置已更新',
        enterRoomId: '请输入房间ID',
        join: '加入'
    },
    English: {
        mindroom: 'Mindroom',
        mindroomDesc: 'Create and share your ideas, collaborate with others in real-time',
        createRoom: 'Create Room',
        untitledRoom: 'Untitled Room',
        noDescription: 'No description',
        noRooms: 'No rooms available',
        roomTitle: 'Room Title',
        roomSubtitle: 'Room Subtitle',
        editRoom: 'Edit Room',
        share: 'Share',
        cancel: 'Cancel',
        save: 'Save',
        richText: 'Rich Text',
        markdown: 'Markdown',
        autoSave: 'Auto Save',
        autoSaved: 'Auto Saved',
        startTyping: 'Start typing...',
        noMessages: 'No messages yet',
        typeMessage: 'Type a message...',
        send: 'Send',
        insertEmoji: 'Insert Emoji',
        insertCode: 'Insert Code',
        quoteDocument: 'Quote Document',
        createNewRoom: 'Create New Room',
        roomTitlePlaceholder: 'Enter room title',
        roomDescription: 'Room Description',
        roomDescPlaceholder: 'Enter room description',
        roomAccess: 'Access Control',
        public: 'Public',
        private: 'Private',
        guestPermissions: 'Guest Permissions',
        readWrite: 'Read & Write',
        readOnly: 'Read Only',
        create: 'Create',
        shareRoom: 'Share Room',
        shareRoomDesc: 'Copy the link below to share with others',
        copy: 'Copy',
        copySuccess: 'Copied to clipboard',
        roomCreated: 'Room created successfully',
        roomUpdated: 'Room settings updated',
        enterRoomId: 'Enter Room ID',
        join: 'Join'
    }
})

// 翻译函数
const t = (key) => {
    return translations[LANG.value][key] || key
}

// 房间ID
const roomId = ref(route.params.id)

// 监听路由变化
watch(() => route.params.id, (newId) => {
    roomId.value = newId
    if (newId) {
        fetchRoomDetails(newId)
    }
})

// 房间列表
const rooms = ref([])

// 当前房间信息
const currentRoom = ref({
    id: '',
    title: '',
    subtitle: '',
    description: '',
    isPublic: true,
    guestCanWrite: true,
    ownerId: '',
    createdAt: new Date().toISOString()
})

// 编辑状态
const isEditing = ref(false)
const editingRoom = ref({})

// 是否为房主
const isOwner = ref(false)

// 编辑器模式
const editorMode = ref('richtext')

// 文档内容
const documentContent = ref('')
const richtextEditor = ref(null)
const markdownEditor = ref(null)

// 聊天相关
const messages = ref([])
const messageInput = ref('')
const chatMessages = ref(null)
const showEmojiPicker = ref(false)
const emojis = ['😀', '😂', '🤔', '👍', '👎', '❤️', '🎉', '🔥', '💡', '⚡️', '🌈', '🍕']

// 对话框控制
const showCreateDialog = ref(false)
const showShareDialog = ref(false)
const newRoom = ref({
    title: '',
    description: '',
    isPublic: true,
    guestCanWrite: true
})
const shareLink = ref('')

// 格式化日期
const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString()
}

// 格式化时间
const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 渲染Markdown
const renderMarkdown = (content) => {
    return content ? markdown.render(content) : ''
}

// 格式化消息内容（支持代码块和表情）
const formatMessageContent = (content) => {
    // 简单处理，实际项目中可能需要更复杂的处理
    let formatted = content

    // 处理代码块
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')

    // 处理行内代码
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>')

    return formatted
}

// 获取房间列表
const fetchRooms = async () => {
    // 模拟数据，实际项目中应该从API获取
    rooms.value = [
        {
            id: '1',
            title: '项目头脑风暴',
            description: '讨论新项目的创意和实现方案',
            memberCount: 5,
            createdAt: '2023-09-15T10:00:00Z'
        },
        {
            id: '2',
            title: '学习笔记分享',
            description: '分享学习过程中的笔记和心得',
            memberCount: 3,
            createdAt: '2023-09-10T14:30:00Z'
        }
    ]
}

// 获取房间详情
const fetchRoomDetails = async (id) => {
    // 模拟数据，实际项目中应该从API获取
    currentRoom.value = {
        id,
        title: id === '1' ? '项目头脑风暴' : '学习笔记分享',
        subtitle: id === '1' ? '创意无限' : '知识共享',
        description: id === '1' ? '讨论新项目的创意和实现方案' : '分享学习过程中的笔记和心得',
        isPublic: true,
        guestCanWrite: true,
        ownerId: 'user1',
        createdAt: '2023-09-15T10:00:00Z'
    }

    // 模拟是否为房主
    isOwner.value = true

    // 获取文档内容
    documentContent.value = '这是房间的文档内容，可以在这里编辑和协作。\n\n## 标题\n这是一个段落。'

    // 获取聊天记录
    messages.value = [
        {
            sender: 'User1',
            content: '大家好！',
            timestamp: '2023-09-15T10:05:00Z',
            isMe: true
        },
        {
            sender: 'Guest_123',
            content: '你好，这个项目看起来很有趣！',
            timestamp: '2023-09-15T10:07:00Z',
            isMe: false
        },
        {
            sender: 'User2',
            content: '我有一个想法，可以这样实现：\n```\nfunction example() {\n  return "Hello World";\n}\n```',
            timestamp: '2023-09-15T10:10:00Z',
            isMe: false
        }
    ]

    // 滚动到最新消息
    nextTick(() => {
        scrollToBottom()
    })
}

// 返回房间列表
const backToList = () => {
    router.push('/mindroom')
}

// 进入房间
const enterRoom = (id) => {
    router.push(`/mindroom/${id}`)
}

// 创建新房间
const createNewRoom = () => {
    newRoom.value = {
        title: '',
        description: '',
        isPublic: true,
        guestCanWrite: true
    }
    showCreateDialog.value = true
}

// 确认创建房间
const confirmCreateRoom = async () => {
    // 模拟创建房间，实际项目中应该调用API
    const newId = Math.floor(Math.random() * 1000).toString()

    // 添加到房间列表
    rooms.value.unshift({
        id: newId,
        title: newRoom.value.title,
        description: newRoom.value.description,
        memberCount: 1,
        createdAt: new Date().toISOString()
    })

    showCreateDialog.value = false
    ElMessage.success(t('roomCreated'))

    // 进入新创建的房间
    router.push(`/mindroom/${newId}`)
}

// 开始编辑房间设置
const startEditing = () => {
    editingRoom.value = { ...currentRoom.value }
    isEditing.value = true
}

// 取消编辑
const cancelEditing = () => {
    isEditing.value = false
}

// 保存房间设置
const saveRoomSettings = async () => {
    // 模拟保存设置，实际项目中应该调用API
    currentRoom.value = { ...editingRoom.value }
    isEditing.value = false
    ElMessage.success(t('roomUpdated'))
}

// 分享房间
const shareRoom = () => {
    shareLink.value = `${window.location.origin}/mindroom/${roomId.value}`
    showShareDialog.value = true
}

// 复制分享链接
const copyShareLink = () => {
    navigator.clipboard.writeText(shareLink.value)
        .then(() => {
            ElMessage.success(t('copySuccess'))
        })
        .catch(err => {
            console.error('复制失败:', err)
        })
}

// 处理文档变更
const handleDocumentChange = () => {
    // 实际项目中应该实现自动保存和协作同步
    // 这里只是模拟
    console.log('文档内容已更新，准备自动保存')
}

// 插入Markdown格式
const insertMarkdown = (type) => {
    const editor = editorMode.value === 'richtext' ? richtextEditor.value : markdownEditor.value
    if (!editor) return

    const textarea = editor
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selected = documentContent.value.substring(start, end)

    let insertion = ''
    switch (type) {
        case 'bold':
            insertion = `**${selected || '粗体文本'}**`
            break
        case 'italic':
            insertion = `*${selected || '斜体文本'}*`
            break
        case 'heading':
            insertion = `\n## ${selected || '标题'}\n`
            break
        case 'link':
            insertion = `[${selected || '链接文本'}](https://example.com)`
            break
        case 'code':
            insertion = selected ? `\`${selected}\`` : '\`代码\`'
            break
        case 'list':
            insertion = `\n- ${selected || '列表项'}\n`
            break
        default:
            return
    }

    documentContent.value = documentContent.value.substring(0, start) + insertion + documentContent.value.substring(end)

    // 设置光标位置
    nextTick(() => {
        textarea.focus()
        const newPosition = start + insertion.length
        textarea.setSelectionRange(newPosition, newPosition)
    })
}

// 发送消息
const sendMessage = () => {
    if (!messageInput.value.trim()) return

    // 添加消息到列表
    messages.value.push({
        sender: 'Me',
        content: messageInput.value,
        timestamp: new Date().toISOString(),
        isMe: true
    })

    // 清空输入框
    messageInput.value = '';

    // 滚动到底部
    nextTick(() => {
        scrollToBottom()
    })
}

// 滚动到聊天底部
const scrollToBottom = () => {
    if (chatMessages.value) {
        chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
}

// 插入表情
const insertEmoji = (emoji) => {
    messageInput.value += emoji
    showEmojiPicker.value = false
}

// 插入代码块
const insertCodeBlock = () => {
    messageInput.value += '\n```\n// 在这里输入代码\n```\n'
}

// 引用文档
const quoteDocument = () => {
    // 获取选中的文档内容
    const editor = editorMode.value === 'richtext' ? richtextEditor.value : markdownEditor.value
    if (!editor) return

    const textarea = editor
    const start = textarea.selectionStart
    const end = textarea.selectionEnd

    if (start !== end) {
        const selected = documentContent.value.substring(start, end)
        messageInput.value += `> ${selected}\n`
    } else {
        // 如果没有选中内容，提示用户
        ElMessage.info('请先在文档中选择要引用的内容')
    }
}

onMounted(async () => {
    // 获取房间列表
    await fetchRooms()

    // 如果有房间ID，获取房间详情
    if (roomId.value) {
        await fetchRoomDetails(roomId.value)
    }
})

onBeforeUnmount(() => {
    // 清理工作，如断开WebSocket连接等
})
</script>

<style scoped>
.mindroom-container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    min-height: calc(100vh - 200px);
}

/* 房间列表样式 */
.room-list-container {
    display: flex;
    flex-direction: column;
    gap: 30px;
}

.room-list-header {
    text-align: center;
    margin-bottom: 20px;
}

.room-list-header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
    background: linear-gradient(45deg, #8E2DE2, #4A00E0);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.room-list-header p {
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.8);
    max-width: 600px;
    margin: 0 auto 20px;
}

.create-room-btn {
    padding: 12px 24px;
    font-size: 1.1rem;
}

.room-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.room-card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 20px;
    transition: all 0.3s ease;
    cursor: pointer;
    height: 200px;
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.room-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
}

.room-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.room-card h3 {
    margin: 0;
    font-size: 1.4rem;
    color: #fff;
}

.room-id {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.6);
}

.room-description {
    flex-grow: 1;
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 15px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    line-clamp: 3;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}

.room-footer {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.6);
}

/* 房间详情样式 */
.room-detail-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
    height: 85vh;
}

.room-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 15px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.room-title-section {
    display: flex;
    align-items: center;
    gap: 15px;
}

.room-back button {
    font-size: 1.2rem;
}

.room-title-display h2 {
    margin: 0 0 5px 0;
    font-size: 1.8rem;
}

.room-title-display p {
    margin: 0;
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.7);
}

.room-title-edit {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 300px;
}

.room-actions {
    display: flex;
    gap: 10px;
}

.room-content {
    display: flex;
    max-height: 1000vh;
    height: calc(100vh - 120px);
    overflow: auto;
}

.document-pane {
    flex: 1;
    padding-right: 16px;
    border-right: 1px solid #eee;
}

.markdown-preview-pane {
    flex: 1;
    padding-left: 16px;
    overflow-y: auto;
}

.markdown-preview {
    padding: 16px;
    background: #fff;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.document-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 15px;
    background: rgba(0, 0, 0, 0.2);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.auto-save-indicator {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
}

.document-editor {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.richtext-editor,
.markdown-editor {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.markdown-toolbar {
    padding: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(0, 0, 0, 0.1);
}

textarea {
    flex: 1;
    padding: 15px;
    background: transparent;
    border: none;
    color: #fff;
    font-size: 1rem;
    line-height: 1.6;
    resize: none;
    outline: none;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
}

.markdown-editor {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.markdown-preview {
    flex: 1;
    padding: 15px;
    overflow-y: auto;
    background: rgba(0, 0, 0, 0.2);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 聊天区域样式 */
.chat-pane {
    flex: 2;
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.no-messages {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    color: rgba(255, 255, 255, 0.5);
    font-style: italic;
}

.message-item {
    max-width: 85%;
    padding: 10px 15px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.1);
    align-self: flex-start;
}

.my-message {
    align-self: flex-end;
    background: rgba(74, 0, 224, 0.3);
}

.message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-size: 0.85rem;
}

.message-sender {
    font-weight: bold;
    color: rgba(255, 255, 255, 0.9);
}

.message-time {
    color: rgba(255, 255, 255, 0.6);
}

.message-content {
    word-break: break-word;
    line-height: 1.4;
}

.message-content pre {
    background: rgba(0, 0, 0, 0.3);
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    margin: 10px 0;
}

.message-content code {
    background: rgba(0, 0, 0, 0.3);
    padding: 2px 5px;
    border-radius: 3px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
}

.chat-input {
    padding: 15px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(0, 0, 0, 0.2);
    position: relative;
}

.chat-tools {
    display: flex;
    justify-content: flex-start;
    margin-top: 10px;
}

.emoji-picker {
    position: absolute;
    bottom: 100%;
    right: 15px;
    background: rgba(30, 30, 30, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 10px;
    width: 250px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    z-index: 10;
}

.emoji-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
}

.emoji-item {
    font-size: 1.5rem;
    cursor: pointer;
    text-align: center;
    transition: transform 0.2s;
}

.emoji-item:hover {
    transform: scale(1.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .room-content {
        flex-direction: column;
    }

    .document-pane,
    .chat-pane {
        flex: none;
        height: 50%;
    }

    .room-grid {
        grid-template-columns: 1fr;
    }

    .room-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .room-actions {
        width: 100%;
        justify-content: flex-end;
    }
}
</style>