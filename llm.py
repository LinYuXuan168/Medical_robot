from zhipuai import ZhipuAI

client = ZhipuAI(api_key="34ce6c9885554de79b71b390b62c7a42.PU5uiMj1kuRfxTUn") # 请填写您自己的APIKey
answer = '乳腺癌的症状是高烧，同时伴随着头晕'
response = client.chat.completions.create(
    model="glm-4-plus",  # 请填写您要调用的模型名称
    messages=[
        {"role": "user", "content": "以一名医生的口吻润色{}这句话,给我最终版本就可以".format(answer)},
    ],
)
print(response.choices[0].message.content)