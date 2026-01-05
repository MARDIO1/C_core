def init():
    '''初始化，迟早要重构'''
    from openai import OpenAI
    client = OpenAI(
        base_url='https://api-inference.modelscope.cn/v1',
        api_key='ms-1c9cc707-01e0-46ef-8f53-d202a207d74f', # ModelScope Token
    )
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
            'content': '你好，你是谁'
            }
        ],
        stream=True,#打开流式输出
        extra_body=extra_body
    )
    #done_thinking = extra_body["enable_thinking"] #开启思考这个呃其实没啥用
    return response

def step(ChatSession):
    '''每一步，不知道该不该搬走'''
    #for chunk in ChatSession.response:#难道respone一直在增长吗？他在哪里被赋值？
        #response每一次for就会触发从远端获取一次，但是它本身不会增长，只是类似远程指针
        #chunk，有什么用？内容部分，赋值
    chunk=ChatSession.chunk

    if chunk.choices: 
        thinking_chunk = chunk.choices[0].delta.reasoning_content
        answer_chunk = chunk.choices[0].delta.content

        if thinking_chunk != '':
            ChatSession.thinking_list.append(thinking_chunk)
        if answer_chunk != '':
            ChatSession.answer_list.append(answer_chunk)

    else:
        return False #已经没有更多数据了！