export const calcHashForArticleId = (articleId: number) => {
    // 添加一个密钥和偏移量增加安全性
    const secretKey = "Charlie'sArticles";
    const offset = 1024;
    // 对文章ID进行简单处理
    const processedId = (articleId + offset) * 7;
    // 将处理后的ID与密钥组合
    const combined = `${processedId}:${secretKey}:${new Date().getTime()}`;
    // 使用Base64编码
    const hash = btoa(combined);
    return hash;
};

export const getArticleIdFromHash = (hash: string) => {
    try {
        // Base64解码
        const decoded = atob(hash);
        // 提取处理后的ID
        const parts = decoded.split(":");
        const processedId = parseInt(parts[0], 10);
        // 还原原始ID
        const offset = 1024;
        const articleId = processedId / 7 - offset;
        return Math.round(articleId);
    } catch (error) {
        console.error("解密失败:", error);
        return -1;
    }
};

import FingerprintJS from "@fingerprintjs/fingerprintjs";
export const getFingerprint = async (): Promise<string> => {
    try {
        const fpPromise = FingerprintJS.load();
        const fp = await fpPromise;
        const result = await fp.get();
        const visitorId = result.visitorId;
        return visitorId;
    } catch (error) {
        console.error("获取指纹失败:", error);
        return "";
    }
};

export const isMobile = (): boolean => {
    const width = window.innerWidth;
    return width <= 768;
};

export const countContent = (
    text: string = ""
): {
    chineseCharCount: number;
    englishWordCount: number;
    wordCount: number;
    readingTime: number;
} => {
    const chineseChars = text.match(/[\u4e00-\u9fff]/g) || [];
    const englishWords = text.match(/\b[a-zA-Z]+(?:['-][a-zA-Z]+)?\b/g) || [];

    const chineseReadingTime = chineseChars.length / 400;
    const englishReadingTime = englishWords.length / 225;
    const totalMinutes = Math.ceil(chineseReadingTime + englishReadingTime);

    return {
        chineseCharCount: chineseChars.length,
        englishWordCount: englishWords.length,
        wordCount: chineseChars.length + englishWords.length,
        readingTime: totalMinutes,
    };
};

export const getDate = (LANG: string = "Chinese") => {
    return new Date().toLocaleDateString(
        LANG === "English" ? "en-US" : "zh-CN",
        {
            year: "numeric",
            month: "short",
            day: "numeric",
        }
    );
};

export const formatDateRange = (
    start: string,
    end: string,
    LANG: string = "Chinese"
) => {
    if (!start) return "";

    const startDate = new Date(start);
    const startStr = startDate.toLocaleDateString(
        LANG === "English" ? "en-US" : "zh-CN",
        {
            year: "numeric",
            month: "short",
            day: "numeric",
        }
    );

    if (!end || start === end) return startStr;

    const endDate = new Date(end);
    const endStr = endDate.toLocaleDateString(
        LANG === "English" ? "en-US" : "zh-CN",
        {
            year: "numeric",
            month: "short",
            day: "numeric",
        }
    );

    return `${startStr} - ${endStr}`;
};
