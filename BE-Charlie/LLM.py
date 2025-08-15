import os
from volcenginesdkarkruntime import Ark

from config import ARK_API_KEY


client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=ARK_API_KEY,
)


def get_ark_summary(prompt_prefix, content):
    completion = client.chat.completions.create(
        model="deepseek-v3-250324",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的文章摘要助手。我将提供一篇文章，你需要根据全文生成一段总结。\n要求：\n1. 用第一人称撰写，不得使用“作者”“笔者”等称谓，不得改为第三人称；\n2. 输出纯文本（不可包含任何markdown符号、列表符号或额外的格式说明）；\n3. 直接输出总结，不得包含解释、提示或与总结无关的内容；\n4. 字数建议控制在200字上下，可分段（使用\\n换行）；\n5. 总结需尽可能涵盖文章的重点内容。"
            },
            {"role": "user", "content": prompt_prefix + content},
        ],
    )
    return completion.choices[0].message.content


if __name__ == "__main__":
    prompt = "你好"
    print(get_ark_response(prompt))


# Streaming:
# stream = client.chat.completions.create(
#     model="deepseek-v3-250324",
#     messages=[
#         {"role": "system", "content": "你是人工智能助手."},
#         {"role": "user", "content": "你好"},
#     ],
#     # 响应内容是否流式返回
#     stream=True,
# )

# if __name__ == "__main__":
#     for chunk in stream:
#         if not chunk.choices:
#             continue
#         print(chunk.choices[0].delta.content, end="")
