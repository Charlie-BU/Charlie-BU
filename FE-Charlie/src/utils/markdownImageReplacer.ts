import { createApp, h } from "vue";
import ArcoVue from "@arco-design/web-vue";
import { Image as AImage } from "@arco-design/web-vue";

/**
 * 替换 markdown 渲染后的自定义图片标签为 a-image 组件
 * @param container 包含 markdown 内容的 DOM 容器
 */
export const replaceMarkdownImages = (container: HTMLElement) => {
    // 查找所有的 arco-image-placeholder 标签
    const placeholders = container.querySelectorAll("arco-image-placeholder");

    placeholders.forEach((placeholder) => {
        const src = placeholder.getAttribute("data-src") || "";
        const alt = placeholder.getAttribute("data-alt") || "";
        const title = placeholder.getAttribute("data-title") || "";

        // 创建一个新的 div 来挂载 Vue 组件
        const mountDiv = document.createElement("div");
        mountDiv.style.width = "100%";
        mountDiv.style.display = "flex";
        mountDiv.style.flexDirection = "column";
        mountDiv.style.alignItems = "center";
        mountDiv.style.margin = "1em auto";

        // 创建 Vue 应用实例
        const app = createApp({
            render() {
                return h("div", { class: "markdown-image-wrapper" }, [
                    h(AImage, {
                        src,
                        alt,
                        title,
                        preview: true,
                        fit: "contain",
                        style: {
                            width: "70%",
                            borderRadius: "0.5em",
                            maxWidth: "100%",
                            height: "auto",
                        },
                        previewProps: {
                            closable: true,
                            maskClosable: true,
                            escToClose: true,
                            wheelZoom: true,
                            keyboard: true,
                        },
                    }),
                    alt ? h("figcaption", {
                        style: {
                            textAlign: "center",
                            color: "#929295",
                            marginTop: "8px",
                            fontSize: "14px",
                        }
                    }, alt) : null
                ].filter(Boolean));
            },
        });

        // 使用 ArcoVue 插件
        app.use(ArcoVue);

        // 挂载组件
        app.mount(mountDiv);

        // 替换原来的 placeholder
        placeholder.parentNode?.replaceChild(mountDiv, placeholder);
    });
};

/**
 * 监听 DOM 变化，自动替换新添加的图片标签
 * @param container 要监听的容器
 */
export const observeMarkdownImages = (container: HTMLElement) => {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === "childList") {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const element = node as HTMLElement;
                        // 检查新添加的节点是否包含图片占位符
                        if (
                            element.querySelector &&
                            element.querySelector("arco-image-placeholder")
                        ) {
                            replaceMarkdownImages(element);
                        }
                    }
                });
            }
        });
    });

    observer.observe(container, {
        childList: true,
        subtree: true,
    });

    return observer;
};
