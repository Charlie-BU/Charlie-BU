import { Modal } from "@arco-design/web-vue";

export const useModal = () => {
    const useConfirmModal = (
        onOk: () => void | Promise<void>,
        action?: string,
        confirmText?: string
    ) => {
        return Modal.confirm({
            title: `确认${action || "操作"}`,
            content: confirmText || `是否确认${action || "执行此操作"}？`,
            cancelText: "取消",
            okText: "确认",
            onOk,
            titleAlign: "start",
        });
    };

    return {
        useConfirmModal,
    };
};
