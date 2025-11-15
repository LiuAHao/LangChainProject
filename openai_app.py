import os
from openai import OpenAI

# 初始化OpenAI客户端，配置为调用本地Qwen模型服务
# 请确保设置环境变量OPENAI_API_KEY或在此处直接设置api_key
# 确保Qwen服务已在本地运行在http://localhost:8000
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),  # 替换为您的实际API密钥
    base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1")  # 本地Qwen服务地址
)

def call_qwen_model(prompt, model="qwen2.5-3b"):
    """
    调用Qwen大模型
    
    Args:
        prompt (str): 用户输入的提示词
        model (str): 要使用的模型名称，默认为qwen2.5-3b
    
    Returns:
        str: 模型返回的响应
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are Qwen, a large language model developed by Alibaba Cloud. You are a helpful assistant. Please answer all questions in Chinese."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"调用Qwen模型时出错: {e}")
        return "抱歉，我在调用Qwen模型时遇到了问题。"

if __name__ == "__main__":
    # 设置提示词，要求模型用中文回答
    prompt = "Give me a short introduction to large language model. Please answer in Chinese."
    
    print("正在调用Qwen大模型...")
    response = call_qwen_model(prompt)
    
    print("响应:")
    print(response)