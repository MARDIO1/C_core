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
    chatSession.input(input())
    while(chatSession.get_API_response()):
        chatSession.fast_show_step()
    print("\n马丢结束")
if __name__ == "__main__":
    main()
