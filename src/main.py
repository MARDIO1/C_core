# src/core/main.py
"""
主程序 - 使用包结构导入LLM API
"""
# 现在可以直接导入
from chat.session import ChatSession
chatSession=ChatSession()
def main():
    """主函数"""
    print("马丢启动...")
    chatSession.new_input_get_LLMresponse(input())
    while(chatSession.streaming_get_API_response()):
        chatSession.streaming_show_step()
    print("\n马丢结束")
if __name__ == "__main__":
    main()
