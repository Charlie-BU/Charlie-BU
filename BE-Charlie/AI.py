import os
from volcenginesdkarkruntime import Ark

from config import ARK_API_KEY
from prompts import SUMMARY


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
                "content": SUMMARY
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
