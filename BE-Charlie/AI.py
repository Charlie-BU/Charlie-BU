from volcenginesdkarkruntime import Ark
import json

from config import ARK_API_KEY, SUMMARY_ARTICLE, GENERATE_ACTIVITY_DESCRIPTION
from prompts import getPrompt


client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=ARK_API_KEY,
)


def get_article_summary(content):
    prompt = getPrompt(SUMMARY_ARTICLE)
    completion = client.chat.completions.create(
        model="deepseek-v3-250324",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ],
    )
    return completion.choices[0].message.content


def get_activity_description(title):
    prompt = getPrompt(GENERATE_ACTIVITY_DESCRIPTION)
    completion = client.chat.completions.create(
        model="deepseek-v3-250324",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": title},
        ],
    )
    return json.loads(completion.choices[0].message.content)


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
