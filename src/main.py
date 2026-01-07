# src/core/main.py
"""
主程序 - 使用包结构导入LLM API
"""
# 现在可以直接导入
from chat.session import chatSession_man
from tools.prompt import get_prompt_manager
from tools.parser import parser_man
from tools.action import action_man
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
    while True:
        # 重置Parser状态
        parser_man.reset()
        
        while True:
            '''流式处理响应'''
            # 获取API响应
            if not chatSession_man.streaming_get_API_response():
                # 检查是否有action需要处理
                if action_man.process_actions():
                    # 有action被执行，需要继续获取响应
                    chatSession_man.current_response = api.LLM.new_response_init(chatSession_man.messages_list)
                    continue
                else:
                    # 没有更多数据，也没有action需要处理
                    break
            
            chatSession_man.streaming_show_step()
            
            parser_man.step_parser()
            
            if parser_man.complete_flag:
                if action_man.process_actions():
                    chatSession_man.current_response = api.LLM.new_response_init(chatSession_man.messages_list)
                    parser_man.reset()
                    
        if parser_man.final_answer_complete_flag:
            break
    
    print("\n马丢结束")

if __name__ == "__main__":
    main()
