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

export const getFingerprint = async (): Promise<string> => {
    // @ts-ignore
    const fpPromise = import("https://openfpcdn.io/fingerprintjs/v4").then(
        (FingerprintJS) => FingerprintJS.load()
    );
    try {
        const fp = await fpPromise;
        const result = await fp.get();
        const visitorId = result.visitorId;
        return visitorId;
    } catch (error) {
        console.error("获取指纹失败:", error);
        return "";
    }
};
