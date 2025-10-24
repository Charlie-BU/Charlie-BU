import MarkdownIt from "markdown-it";
import hljs from "highlight.js";
import markdownItContainer from "markdown-it-container";
import { replaceMarkdownImages } from "../../utils/markdownImageReplacer";
import "./index.css";

export const useMarkdown = () => {
    const markdown = new MarkdownIt({
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
        markdown.use(markdownItContainer, style, {
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
    markdown.renderer.rules.image = (tokens, idx) => {
        const token = tokens[idx];
        const src = token.attrGet("src");
        const alt = token.content || "";
        const title = token.attrGet("title") || "";

        // 生成自定义标签，稍后会被 Vue 组件替换
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

    return {
        renderMarkdown: (content: string) => {
            return markdown.render(content || "");
        },
        replaceImages: replaceMarkdownImages,
    };
};
