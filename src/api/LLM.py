
#单例:
_client = None
def client_init():
    '''初始化，迟早要重构'''
    from openai import OpenAI
    """获取或创建客户端（单例）"""
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(
            base_url='https://api-inference.modelscope.cn/v1',
            api_key='ms-1c9cc707-01e0-46ef-8f53-d202a207d74f',
        )
    return _client

def new_response_init(input):
    # set extra_body for thinking control
    extra_body = {
        # enable thinking, set to False to disable
        "enable_thinking": True
    }
    response = _client.chat.completions.create(
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
    #done_thinking = extra_body["enable_thinking"] #开启思考这个呃其实没啥用
    return response