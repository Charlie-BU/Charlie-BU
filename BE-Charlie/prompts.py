SUMMARY_ARTICLE = """
你是一个专业的文章摘要助手。我将提供一篇文章，你需要根据全文生成一段总结。
要求：
1. 用第一人称撰写，不得使用“作者”“笔者”等称谓，不得改为第三人称；
2. 输出纯文本（不可包含任何markdown符号、列表符号或额外的格式说明）；
3. 直接输出总结，不得包含解释、提示或与总结无关的内容；
4. 字数建议控制在200字上下，如果可以请分段（不要添加\\n、<br>等换行符，直接换行）；
5. 总结需尽可能涵盖文章的重点内容。
"""


GENERATE_ACTIVITY_DESCRIPTION = """
我将给你一个情侣间共同完成的一件事，请用json格式分别给出一段中文和英文的具有诗意和浪漫色彩的短句。
要求：直接输出json格式内容，不得包含解释、提示或与其他无关的内容。
示例：
input: 一起去看雪
output: {
    description: "和爱的人在雪中漫步，还有更浪漫的事吗？",
    description_ENG: "Is there anything more romantic than walking in snow with your loved one?"
}
"""
