from openai import OpenAI

ai_chatbot = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# response = client.chat.completions.create(
#     model="deepseek/deepseek-chat-v3-0324:free",
#     messages=[
#         {"role": "user", "content": "Объясни квантовые вычисления"},
#     ],
# )

# print(response.choices[0].message.content)


# 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