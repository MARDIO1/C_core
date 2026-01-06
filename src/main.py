# src/core/main.py
"""
主程序 - 使用包结构导入LLM API
"""
# 现在可以直接导入
from chat.session import ChatSession,chatSession_man
from tools.prompt import prompt_man
from tools.parser import parser_man
# chatSession=ChatSession()
def main():
    """主函数"""
    print("马丢启动...")
    '''while True:
        chatSession_man.new_input_get_LLMresponse(input())
        while(chatSession_man.streaming_get_API_response()):
            chatSession_man.streaming_show_step()
    '''
    temp_input=input()
    temp_message=prompt_man.create_agent_promote(temp_input)
    chatSession_man.new_input_get_LLMresponse(temp_message)
    while(chatSession_man.streaming_get_API_response()):
        chatSession_man.streaming_show_step()
        
    print("\n马丢结束")
if __name__ == "__main__":
    main()
