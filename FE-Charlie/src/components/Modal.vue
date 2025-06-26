<!--
使用方法：
【表单模式】
<Modal v-model:visible="formVisible" type="form" title="编辑信息" confirm-text="保存" @confirm="handleFormSubmit">
    <template #form>
        <el-form :model="formData">
            <el-form-item label="标题">
                <el-input v-model="formData.title" />
            </el-form-item>
            <el-form-item label="描述">
                <el-input v-model="formData.description" type="textarea" />
            </el-form-item>
        </el-form>
    </template>
</Modal>

【删除模式】
<Modal v-model:visible="deleteVisible" type="delete" title="确认删除" content="确定要删除这个项目吗？"
    @confirm="handleDeleteConfirm" />

【自定义模式】
<Modal v-model:visible="customVisible" type="custom" title="自定义弹窗" @confirm="handleCustomConfirm">
    <div>这里可以放任何自定义内容</div>
</Modal>
-->

<template>
    <div v-if="visible" class="delete-dialog-overlay" :class="{ 'closing': isClosing }" @click="handleCancel">
        <div class="delete-dialog" :class="{ 'closing': isClosing }" @click.stop>
            <div class="delete-dialog-header">
                <div class="warning-icon" v-if="type === 'delete'">
                    <el-icon :size="28">
                        <CircleCloseFilled />
                    </el-icon>
                </div>
                <div class="info-icon" v-else>
                    <el-icon :size="28">
                        <Opportunity />
                    </el-icon>
                </div>
                <h4 style="font-size: 18px; margin-bottom: 5px;">{{ title }}</h4>
            </div>
            <div class="delete-dialog-content">
                <!-- 删除模式 -->
                <p v-if="type === 'delete'" class="warning-text">{{ content || '确定要删除此项吗？' }}</p>

                <!-- 表单模式 -->
                <div v-else-if="type === 'form'" class="form-content">
                    <slot name="form"></slot>
                </div>

                <!-- 自定义内容 -->
                <div v-else>
                    <slot></slot>
                </div>
            </div>
            <div class="delete-dialog-actions">
                <button class="cancel-button" @click="handleCancel">
                    {{ cancelText || '取消' }}
                </button>
                <button class="confirm-button" @click="handleConfirm" :style="{
                    'background': type === 'delete' ? 'red' : 'green'
                }">
                    <el-icon class="button-icon" v-if="type === 'delete'">
                        <Delete />
                    </el-icon>
                    <el-icon class="button-icon" v-else>
                        <Check />
                    </el-icon>
                    {{ confirmText || (type === 'delete' ? '确认删除' : '确认') }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    type: {
        type: String,
        default: 'delete',
        validator: (value) => ['delete', 'form', 'custom'].includes(value)
    },
    title: {
        type: String,
        default: '确认删除'
    },
    content: {
        type: String,
        default: ''
    },
    cancelText: {
        type: String,
        default: ''
    },
    confirmText: {
        type: String,
        default: ''
    },
    closeOnEsc: {
        type: Boolean,
        default: true
    }
})

const emit = defineEmits(['update:visible', 'confirm', 'cancel'])

const isClosing = ref(false)

// ESC键处理函数
const handleEscKey = (event) => {
    if (event.key === 'Escape' && props.visible && props.closeOnEsc) {
        handleCancel()
    }
}

// 监听visible变化，添加/移除ESC键监听
watch(() => props.visible, (newVal) => {
    if (newVal) {
        isClosing.value = false
        document.addEventListener('keydown', handleEscKey)
    } else {
        document.removeEventListener('keydown', handleEscKey)
    }
})

// 取消操作 - 添加关闭动画
const handleCancel = () => {
    if (isClosing.value) return // 防止重复触发

    isClosing.value = true

    // 延迟关闭，等待动画完成
    setTimeout(() => {
        emit('update:visible', false)
        emit('cancel')
        isClosing.value = false
        document.removeEventListener('keydown', handleEscKey)
    }, 300) // 动画持续时间
}

// 确认操作 - 添加关闭动画
const handleConfirm = () => {
    if (isClosing.value) return

    emit('confirm')

    // 如果是删除操作，自动关闭弹窗
    if (props.type === 'delete') {
        isClosing.value = true
        setTimeout(() => {
            emit('update:visible', false)
            isClosing.value = false
            document.removeEventListener('keydown', handleEscKey)
        }, 300)
    }
}

// 组件卸载前移除事件监听
onBeforeUnmount(() => {
    document.removeEventListener('keydown', handleEscKey)
})
</script>

<style scoped>
/* 弹窗遮罩 */
.delete-dialog-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    animation: overlay-enter 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.delete-dialog-overlay.closing {
    animation: overlay-exit 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes overlay-enter {
    from {
        opacity: 0;
        backdrop-filter: blur(0px);
    }

    to {
        opacity: 1;
        backdrop-filter: blur(8px);
    }
}

@keyframes overlay-exit {
    from {
        opacity: 1;
        backdrop-filter: blur(8px);
    }

    to {
        opacity: 0;
        backdrop-filter: blur(0px);
    }
}

/* 弹窗主体 */
.delete-dialog {
    background: linear-gradient(135deg, rgba(76, 8, 125, 0.95), rgba(112, 65, 206, 0.98));
    border-radius: 20px;
    padding: 32px;
    max-width: 480px;
    width: 90%;
    box-shadow: 0 25px 50px rgba(139, 92, 246, 0.3), 0 0 0 1px rgba(167, 139, 250, 0.2);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(167, 139, 250, 0.2);
    position: relative;
    animation: dialog-enter 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.delete-dialog.closing {
    animation: dialog-exit 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes dialog-enter {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(-10px);
    }

    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

@keyframes dialog-exit {
    from {
        opacity: 1;
        transform: scale(1) translateY(0);
    }

    to {
        opacity: 0;
        transform: scale(0.9) translateY(-10px);
    }
}

.delete-dialog-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
    /* 增加头部底部间距 */
}

.warning-icon {
    color: #EC4899;
    filter: drop-shadow(0 0 8px rgba(236, 72, 153, 0.5));
    animation: warning-pulse 2s ease-in-out infinite;
}

.info-icon {
    color: #8B5CF6;
    filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.5));
}

@keyframes warning-pulse {

    0%,
    100% {
        transform: scale(1);
        filter: drop-shadow(0 0 8px rgba(236, 72, 153, 0.5));
    }

    50% {
        transform: scale(1.1);
        filter: drop-shadow(0 0 12px rgba(236, 72, 153, 0.8));
    }
}

.delete-dialog-header h4 {
    color: #ffffff;
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.delete-dialog-content {
    margin-bottom: 32px;
    /* 增加内容区域底部间距 */
    padding: 0 4px;
    /* 增加内容区域左右内边距 */
}

.delete-dialog-content p {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1rem;
    line-height: 1.8;
    /* 增加行高 */
    margin: 16px 5px 16px 0;
    /* 增加上下外边距 */
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.warning-text {
    color: rgba(236, 72, 153, 0.9) !important;
    font-size: 18px !important;
    font-weight: bold;
}

.form-content {
    color: rgba(255, 255, 255, 0.9);
    padding: 8px 0;
    /* 增加表单内容的上下内边距 */
}

/* 添加输入框透明背景样式 */
.form-content :deep(.el-input__wrapper) {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: none;
}

.form-content :deep(.el-input__wrapper:hover),
.form-content :deep(.el-input__wrapper.is-focus) {
    background: transparent;
    border-color: rgba(255, 255, 255, 0.5);
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.3);
}

.form-content :deep(.el-textarea__inner),
.form-content :deep(.el-input__inner) {
    background: transparent;
    color: rgba(255, 255, 255, 0.9);
}

/* 添加el-select透明背景样式 */
.form-content :deep(.el-select__wrapper) {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: none;
}

.form-content :deep(.el-select__wrapper:hover),
.form-content :deep(.el-select__wrapper.is-focus) {
    background: transparent;
    border-color: rgba(255, 255, 255, 0.5);
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.3);
}

.form-content :deep(.el-select__inner),
.form-content :deep(.el-select__placeholder) {
    background: transparent;
    color: rgba(255, 255, 255, 0.9);
}

/* 下拉菜单样式 */
.form-content :deep(.el-select__selected-item),
.form-content :deep(.el-select-dropdown__item) {
    background: transparent;
    color: rgba(255, 255, 255, 0.9);
}

.form-content :deep(.el-select-dropdown__item.selected) {
    background: transparent;
    color: #8B5CF6;
}

.delete-dialog-actions {
    display: flex;
    gap: 16px;
    /* 增加按钮之间的间距 */
    justify-content: flex-end;
    padding-top: 8px;
    /* 增加按钮区域顶部内边距 */
}

.cancel-button,
.confirm-button {
    padding: 14px 28px;
    /* 增加按钮内边距 */
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.95rem;
    border: none;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 120px;
    /* 设置按钮最小宽度 */
    justify-content: center;
}

.cancel-button {
    background: rgba(167, 139, 250, 0.1);
    color: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(167, 139, 250, 0.3);
    backdrop-filter: blur(10px);
}

.cancel-button:hover {
    background: rgba(167, 139, 250, 0.2);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(139, 92, 246, 0.2);
}

.confirm-button {
    background: linear-gradient(135deg, #8B5CF6, #A855F7);
    color: white;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}

.confirm-button:hover {
    background: linear-gradient(135deg, #7C3AED, #8B5CF6);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.6);
}

.confirm-button:active {
    transform: translateY(0);
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}

.button-icon {
    font-size: 16px;
}

/* 响应式调整 */
@media (max-width: 480px) {
    .delete-dialog {
        padding: 24px;
        margin: 20px;
    }

    .delete-dialog-actions {
        flex-direction: column;
        gap: 12px;
        /* 移动端按钮间距 */
    }

    .cancel-button,
    .confirm-button {
        width: 100%;
        justify-content: center;
        padding: 16px 28px;
        /* 移动端增加按钮内边距 */
    }

    .delete-dialog-content {
        margin-bottom: 28px;
        /* 移动端调整内容底部间距 */
    }

    .delete-dialog-header {
        margin-bottom: 20px;
        /* 移动端调整头部底部间距 */
    }
}
</style>

<!-- 添加全局样式，影响teleport到body的元素 -->
<style>
/* 下拉菜单全局样式 */
.el-popper {
    z-index: 10000 !important;
    /* 确保比Modal的z-index(9999)高 */
}

body .el-popper.is-pure,
body .el-popper.el-select__popper {
    background: rgba(76, 8, 125, 0.95) !important;
    border: 1px solid rgba(167, 139, 250, 0.2) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
}

body .el-popper.is-pure .el-select-dropdown__item,
body .el-popper.el-select__popper .el-select-dropdown__item {
    color: rgba(255, 255, 255, 0.9) !important;
}

body .el-popper.is-pure .el-select-dropdown__item.hover,
body .el-popper.el-select__popper .el-select-dropdown__item.hover,
body .el-popper.is-pure .el-select-dropdown__item:hover,
body .el-popper.el-select__popper .el-select-dropdown__item:hover {
    background-color: rgba(139, 92, 246, 0.2) !important;
}

body .el-popper.is-pure .el-select-dropdown__item.selected,
body .el-popper.el-select__popper .el-select-dropdown__item.selected {
    background-color: rgba(139, 92, 246, 0.3) !important;
    color: #fff !important;
    font-weight: bold !important;
}

/* 修复popper箭头颜色 */
body .el-popper.is-pure .el-popper__arrow::before,
body .el-popper.el-select__popper .el-popper__arrow::before {
    background-color: rgba(76, 8, 125, 0.95) !important;
    border-color: rgba(167, 139, 250, 0.2) !important;
}
</style>