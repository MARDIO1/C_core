"""
修复版Parser - 使用更简单的方法解析流式响应
"""
from typing import List, Optional, Dict, Any
import re
from src.chat.session import ChatSession, chatSession_man

class Parser:
    """简单解析器 - 专门处理流式XML标签"""
    
    def __init__(self):
        """使用全局实例"""
        self.chat_session: ChatSession = chatSession_man #指向全局类
        self.current_text = ""  # 当前累积的文本
        self.step_tag = None  # 当前所在的标签：'action', 'thought', 'final_answer'
        self.tag_content = ""  # 标签内的内容
        self.complete_flag:bool=False#一段结束瞬间产生的flag脉冲
        
        self.now_action =""
        self.step_final_answer=""
        self.step_thought=""
        self.step_observation=""

    def step_parser(self):
        """从chat_session.answer_chunk中提取标签，修改成员变量"""
        chunk = self.chat_session.answer_chunk or ""
        
        if not chunk:
            return
        
        # 将chunk添加到当前文本
        self.current_text += chunk
        
        # 处理当前文本
        while self.current_text:
            if self.step_tag is None:
                # 不在标签内，寻找开始标签
                action_start = self.current_text.find("<action>")
                thought_start = self.current_text.find("<thought>")
                final_start = self.current_text.find("<final_answer>")
                observation_start = self.current_text.find("<observation>")
                
                # 找到最近的开始标签
                starts = []
                if action_start != -1:
                    starts.append(("action", action_start, 8))
                if thought_start != -1:
                    starts.append(("thought", thought_start, 9))
                if final_start != -1:
                    starts.append(("final_answer", final_start, 14))
                if observation_start != -1:
                    starts.append(("observation", observation_start, 13))
                
                if starts:
                    # 按位置排序
                    starts.sort(key=lambda x: x[1])
                    tag_name, start_pos, tag_len = starts[0]
                    
                    # 进入标签
                    self.step_tag = tag_name
                    self.tag_content = ""
                    self.current_text = self.current_text[start_pos + tag_len:]
                else:
                    # 没有开始标签，清空文本
                    self.current_text = ""
            
            else:
                # 在标签内，寻找结束标签
                end_tag = f"</{self.step_tag}>"
                end_pos = self.current_text.find(end_tag)
                
                if end_pos != -1:
                    # 找到结束标签
                    self.tag_content += self.current_text[:end_pos]
                    
                    # 根据标签类型设置成员变量
                    if self.step_tag == "action":
                        self.now_action = self.tag_content
                        self.complete_flag = True
                    elif self.step_tag == "thought":
                        self.step_thought = self.tag_content
                    elif self.step_tag == "final_answer":
                        self.step_final_answer = self.tag_content
                    elif self.step_tag == "observation":
                        self.step_observation = self.tag_content
                    
                    # 退出标签
                    self.step_tag = None
                    self.tag_content = ""
                    self.current_text = self.current_text[end_pos + len(end_tag):]
                else:
                    # 没有找到结束标签，累积内容
                    self.tag_content += self.current_text
                    self.current_text = ""
    
    def reset(self):
        """重置解析器状态，用于新的对话"""
        self.current_text = ""
        self.step_tag = None
        self.tag_content = ""
        self.complete_flag = False
        self.now_action = ""
        self.step_final_answer = ""
        self.step_thought = ""
        self.step_observation = ""

parser_man=Parser() 