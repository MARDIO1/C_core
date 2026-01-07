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
    
    # 获取系统提示
    system_prompt = prompt_man.get_system_prompt()
    
    # 初始化消息列表：添加系统提示和用户输入
    # 注意：这里直接操作 chatSession_man.messages_list，而不是创建新的 messages 变量
    chatSession_man.messages_list.clear()  # 清空现有消息（如果有）
    chatSession_man.messages_list.append({"role": "system", "content": system_prompt})
    chatSession_man.messages_list.append({"role": "user", "content": temp_input})
    
    while 1:
        # 重置Parser状态（新的响应需要新的解析）
        parser_man.reset()
        
        # 创建新的LLM响应，直接使用 chatSession_man.messages_list
        chatSession_man.current_response = api.LLM.new_response_init(chatSession_man.messages_list)
        
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
                result = action_man.process_actions()
                if result:
                    # action执行成功，观察结果已添加到chatSession_man.messages_list
                    # AI的响应也已添加到chatSession_man.messages_list（在streaming_get_API_response中）
                    # 注意：不再需要更新 messages 变量，因为直接使用 chatSession_man.messages_list
                    # 退出内层循环，让外层循环重新开始
                    break
                else:
                    # action执行失败，继续处理
                    pass
        
        # 检查是否应该停止对话（收到final_answer）
        if parser_man.stop_flag:
            print("\n[完成] 收到最终答案，对话结束")
            break
        
    print("\n马丢结束")

if __name__ == "__main__":
    main()
