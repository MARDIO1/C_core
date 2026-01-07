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
    
    # 获取用户输入
    temp_input = input("你: ")
    # 创建初始消息（包含系统提示和用户输入）
    messages = prompt_man.create_agent_promote(temp_input)
    
    # 外层循环：每次发起一个新的响应
    while True:
        # 重置Parser状态（新的响应需要新的解析）
        parser_man.reset()
        
        # 创建新的LLM响应
        chatSession_man.current_response = api.LLM.new_response_init(messages)
        
        # 内层循环：流式处理chunk
        while True:
            # 获取API响应
            if not chatSession_man.streaming_get_API_response():
                # LLM响应结束，退出内层循环
                break
            
            # 显示当前chunk
            chatSession_man.streaming_show_step()
            
            # 解析当前chunk
            parser_man.step_parser()
            
            # 检查是否有action需要处理
            if parser_man.complete_flag:
                # 执行action
                if action_man.process_actions():
                    # action执行成功，观察结果已添加到chatSession_man.messages_list
                    # AI的响应也已添加到chatSession_man.messages_list（在streaming_get_API_response中）
                    # 更新messages以包含所有历史信息
                    messages = chatSession_man.messages_list.copy()
                    # 退出内层循环，让外层循环重新开始
                    break
        
        # 检查是否是最终答案
        if parser_man.final_answer_complete_flag:
            print("\n✓ 收到最终答案，对话结束")
            break
        

    
    print("\n马丢结束")

if __name__ == "__main__":
    main()
