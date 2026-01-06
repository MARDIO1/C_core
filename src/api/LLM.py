
from typing import Optional, List, Dict, Any, Union
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

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

def new_response_init(input: Union[str, List[Dict[str, Any]]]):
    """创建新的响应"""
    # Union[str, List[Dict[str, Any]]] 表示：
    # 参数可以是两种类型之一：
    # 1. str: 单个字符串（自动转换为用户消息）
    # 2. List[Dict[str, Any]]: 消息列表
    # 确保客户端已初始化
    client = client_init()
    
    # set extra_body for thinking control
    extra_body = {
        # enable thinking, set to False to disable
        "enable_thinking": True
    }
    
    # 处理输入：可以是字符串或消息列表
    if isinstance(input, str):
        messages: List[ChatCompletionMessageParam] = [
            {"role": "user", "content": input}
        ]
    else:
        # 转换消息格式为OpenAI要求的类型
        messages: List[ChatCompletionMessageParam] = []
        for msg in input:
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
    
    response = client.chat.completions.create(
        model='deepseek-ai/DeepSeek-V3.2',
        messages=messages,
        stream=True,
        extra_body=extra_body
    )
    return response


