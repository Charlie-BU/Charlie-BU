export const markdownSign = {
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

export const removeMarkdownSymbols = (text: string) => {
    return text
        .replace(/^#{1,6}\s*/gm, '') // 去除标题符号 # 
        .replace(/(\*\*|__)(.*?)\1/g, '$2') // 去除粗体 **text** 或 __text__
        .replace(/(\*|_)(.*?)\1/g, '$2') // 去除斜体 *text* 或 _text_
        .replace(/`{1,3}([^`]+)`{1,3}/g, '$1') // 去除代码 `text` 或 ```text```
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // 去除链接 [text](url)
        .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1') // 去除图片 ![alt](url)
        .replace(/~~(.*?)~~/g, '$1') // 去除删除线 ~~text~~
        .replace(/^>\s*/gm, '') // 去除引用 >
        .replace(/^[-*+]\s+/gm, '') // 去除无序列表 - * +
        .replace(/^\d+\.\s+/gm, '') // 去除有序列表 1. 2. 3.
        .trim()
}
