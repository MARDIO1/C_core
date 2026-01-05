
from typing import Optional
from openai import OpenAI

# 单例客户端，使用类型提示
_client: Optional[OpenAI] = None

def client_init() -> OpenAI:
    '''获取或创建客户端（单例）'''
    global _client
    if _client is None:
        _client = OpenAI(
            base_url='https://api-inference.modelscope.cn/v1',
            api_key='ms-1c9cc707-01e0-46ef-8f53-d202a207d74f',
        )
    return _client

def new_response_init(input: str):
    """创建新的响应"""
    # 确保客户端已初始化
    client = client_init()  # 这会初始化 _client 如果还没初始化
    
    # set extra_body for thinking control
    extra_body = {
        # enable thinking, set to False to disable
        "enable_thinking": True
    }
    response = client.chat.completions.create(
        model='deepseek-ai/DeepSeek-V3.2', # ModelScope Model-Id, required
        messages=[
            {
            'role': 'user',
            'content': input
            }
        ],
        stream=True,#打开流式输出
        extra_body=extra_body
    )
    return response
