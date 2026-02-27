import MarkdownIt from "markdown-it";
import hljs from "highlight.js";
import markdownItContainer from "markdown-it-container";
import "./index.css";
import { createApp, h } from "vue";
import ArcoVue from "@arco-design/web-vue";
import { Image as AImage } from "@arco-design/web-vue";
import prettier from "prettier/standalone";
import markdownPlugin from "prettier/plugins/markdown";
import pangu from "pangu";

export const useMarkdown = () => {
    const markdownSign: Record<
        string,
        { sign: string; description: string; icon: string }
    > = {
        bold: {
            sign: `
**Text**`,
            description: `加粗`,
            icon: "B",
        },
        italic: {
            sign: `
*Text*`,
            description: `斜体`,
            icon: "I",
        },
        quote: {
            sign: `
> Text`,
            description: `引用`,
            icon: '"',
        },
        divider: {
            sign: `
---
`,
            description: `分割线`,
            icon: "——",
        },
        strikeThrough: {
            sign: `
~~Text~~`,
            description: `删除线`,
            icon: "S",
        },
        code: {
            sign: `\`Code\``,
            description: `行内代码`,
            icon: "<>",
        },
        codeBlock: {
            sign: `
\`\`\`
Code
\`\`\``,
            description: `代码块`,
            icon: "</>",
        },
        link: {
            sign: `
[Description](https://example.com)`,
            description: `链接`,
            icon: "🔗",
        },
        image: {
            sign: `
![Description](https://example.com/image.png)`,
            description: `图片`,
            icon: "🖼",
        },
        heading1: {
            sign: `
# `,
            description: `一级标题`,
            icon: "H1",
        },
        heading2: {
            sign: `
## `,
            description: `二级标题`,
            icon: "H2",
        },
        heading3: {
            sign: `
### `,
            description: `三级标题`,
            icon: "H3",
        },
        heading4: {
            sign: `
#### `,
            description: `四级标题`,
            icon: "H4",
        },
        heading5: {
            sign: `
##### `,
            description: `五级标题`,
            icon: "H5",
        },
        heading6: {
            sign: `
###### `,
            description: `六级标题`,
            icon: "H6",
        },
        list: {
            sign: `
- element1
- element2`,
            description: `无序列表`,
            icon: "•",
        },
        orderedListItem: {
            sign: `
1. element1
2. element2`,
            description: `有序列表项`,
            icon: "1.",
        },
        table: {
            sign: `
| Header1 | Header2 |
| :-----: | :-----: |
| Cell1   | Cell2   |
| Cell3   | Cell4   |
`,
            description: `表格`,
            icon: "⊞",
        },
    };
    const initMarkdownParser = () => {
        // 初始化 markdown 解析器
        const markdownParser = new MarkdownIt({
            highlight: (str: string, lang: string) => {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return `<pre class="hljs"><code>${
                            hljs.highlight(str, {
                                language: lang,
                                ignoreIllegals: true,
                            }).value
                        }</code></pre>`;
                    } catch (_) {}
                }
                // 语言未知时自动识别或转义
                const safeHtml = hljs.highlightAuto(str).value;
                return `<pre class="hljs"><code>${safeHtml}</code></pre>`;
            },
        });

        // 使用容器插件添加高亮块
        const styles = ["warning", "primary", "success", "info", "danger"];
        styles.forEach((style) => {
            markdownParser.use(markdownItContainer, style, {
                validate(params: string) {
                    return new RegExp(`^${style}\\s*(.*)$`).test(params.trim());
                },
                render(tokens: any[], idx: number) {
                    if (tokens[idx].nesting === 1) {
                        // opening tag
                        return `<div class="markdown-${style}">\n`;
                    } else {
                        // closing tag
                        return "</div>\n";
                    }
                },
            });
        });

        // 图片宽高自适应、圆角、图注
        // 重写 image 渲染规则，使用 a-image 组件
        markdownParser.renderer.rules.image = (tokens, idx) => {
            const token = tokens[idx];
            const src = token.attrGet("src");
            const alt = token.content || "";
            const title = token.attrGet("title") || "";

            // 生成自定义标签，之后会被 a-image 组件替换
            return `
            <div class="markdown-image-container" style="width: 100%; display: flex; flex-direction: column; align-items: center; margin: 1em auto;">
                <arco-image-placeholder 
                    data-src="${src}" 
                    data-alt="${alt}" 
                    data-title="${title}"
                    style="width: 70%; border-radius: 0.5em;">
                </arco-image-placeholder>
            </div>
        `;
        };

        // 重写 table 渲染规则，包裹table-wrapper
        const proxy = (
            tokens: any[],
            idx: number,
            options: any,
            _env: any,
            self: any,
        ) => self.renderToken(tokens, idx, options);

        const originalTableOpenRenderer =
            markdownParser.renderer.rules.table_open || proxy;
        const originalTableCloseRenderer =
            markdownParser.renderer.rules.table_close || proxy;

        // 重写 table_open 规则，添加包裹 div
        markdownParser.renderer.rules.table_open = (
            tokens,
            idx,
            options,
            env,
            self,
        ) => {
            return (
                '<div class="markdown-table-wrapper">\n' +
                originalTableOpenRenderer(tokens, idx, options, env, self)
            );
        };

        // 重写 table_close 规则，关闭包裹 div
        markdownParser.renderer.rules.table_close = (
            tokens,
            idx,
            options,
            env,
            self,
        ) => {
            return (
                originalTableCloseRenderer(tokens, idx, options, env, self) +
                "\n</div>"
            );
        };

        return markdownParser;
    };

    const markdownParser = initMarkdownParser();

    const replaceMarkdownImages = (container: HTMLElement) => {
        // 查找所有的 arco-image-placeholder 标签
        const placeholders = container.querySelectorAll(
            "arco-image-placeholder",
        );

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
                    return h(
                        "div",
                        { class: "markdown-image-wrapper" },
                        [
                            h(AImage, {
                                src,
                                alt,
                                title,
                                preview: true,
                                fit: "contain",
                                style: {
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
                            alt
                                ? h(
                                      "figcaption",
                                      {
                                          style: {
                                              textAlign: "center",
                                              color: "#929295",
                                              marginTop: "8px",
                                              fontSize: "14px",
                                          },
                                      },
                                      alt,
                                  )
                                : null,
                        ].filter(Boolean),
                    );
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

    const removeMarkdownSymbols = (text: string) => {
        return text
            .replace(/^#{1,6}\s*/gm, "") // 去除标题符号 #
            .replace(/(\*\*|__)(.*?)\1/g, "$2") // 去除粗体 **text** 或 __text__
            .replace(/(\*|_)(.*?)\1/g, "$2") // 去除斜体 *text* 或 _text_
            .replace(/`{1,3}([^`]+)`{1,3}/g, "$1") // 去除代码 `text` 或 ```text```
            .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1") // 去除链接 [text](url)
            .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1") // 去除图片 ![alt](url)
            .replace(/~~(.*?)~~/g, "$1") // 去除删除线 ~~text~~
            .replace(/^>\s*/gm, "") // 去除引用 >
            .replace(/^[-*+]\s+/gm, "") // 去除无序列表 - * +
            .replace(/^\d+\.\s+/gm, "") // 去除有序列表 1. 2. 3.
            .trim();
    };

    const formatMarkdownByPrettier = async (
        markdown: string,
    ): Promise<string> => {
        try {
            const formatted = await prettier.format(markdown, {
                parser: "markdown",
                plugins: [markdownPlugin],
            });
            // 用 pangu 在中英文之间插入空格
            const spaced = pangu.spacingText(formatted);
            // 去掉 ** 和 ** 的空格 (仅当只有一个空格时)
            const final = spaced
                .replace(/(^|[^ ]) \*\*/g, "$1**")
                .replace(/\*\* ([^ ])/g, "**$1");
            return final.trim();
        } catch (error) {
            console.error("[formatByPrettier] 格式化失败:", error);
            return markdown; // 格式化失败则返回原内容
        }
    };

    return {
        markdownSign,
        renderMarkdown: (content: string) => {
            return markdownParser.render(content || "");
        },
        replaceImages: replaceMarkdownImages,
        removeMarkdownSymbols,
        formatMarkdownByPrettier,
    };
};
