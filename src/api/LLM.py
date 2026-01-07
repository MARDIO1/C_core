from typing import Optional, List, Dict, Any, Union
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import os
from dotenv import load_dotenv

# 加载指定路径的 .env 文件
env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'KEY', '.env')
load_dotenv(env_path)

MODEL = 'deepseek-chat'#deepseek-ai/DeepSeek-V3.2
BASE_URL = 'ttps://api.deepseek.com'#https://api-inference.modelscope.cn/v1

# 单例客户端，使用类型提示
_client: Optional[OpenAI] = None

def client_init() -> OpenAI:
    '''获取或创建客户端（单例）'''
    global _client
    if _client is None:
        # 从环境变量取出 API KEY
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError(f"DEEPSEEK_API_KEY 环境变量未设置。请检查 .env 文件: {env_path}")
        
        _client = OpenAI(
            base_url=BASE_URL,
            api_key=api_key,
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
        model=MODEL,
        messages=messages,
        stream=True,
        extra_body=extra_body
    )
    return response
