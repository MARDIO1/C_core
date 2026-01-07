# src/core/main.py
"""
主程序 - 使用包结构导入LLM API
"""
# 现在可以直接导入
from chat.session import chatSession_man
from tools.prompt import get_prompt_manager
from tools.parser import parser_man
import api.LLM

def main():
    """主函数"""
    print("马丢启动...")
    
    # 获取提示词管理器实例
    prompt_man = get_prompt_manager()
    
    # 重置Parser状态
    parser_man.reset()
    # 获取用户输入
    temp_input = input("你: ")
    # 复杂promote
    messages = prompt_man.create_agent_promote(temp_input)
    chatSession_man.current_response = api.LLM.new_response_init(messages)
    # 流式处理响应
    while chatSession_man.streaming_get_API_response():
        # 显示当前chunk
        chatSession_man.streaming_show_step()
        
        # 使用Parser解析当前chunk
        parser_man.step_parser()
        
        # 调试：打印解析器状态
        #parser_man.debug_step()
    print("\n马丢结束")

if __name__ == "__main__":
    main()
