"""
修复版Parser - 使用更简单的方法解析流式响应
"""
from typing import List, Optional, Dict, Any
import re

class Parser:
    """简单解析器 - 专门处理流式XML标签"""
    
    def __init__(self):
        """使用全局实例"""
        from chat.session import chatSession_man
        self.chat_session = chatSession_man  # 指向全局类
        self.current_text = ""  # 当前累积的文本
        self.step_tag = None  # 当前所在的标签：'action', 'thought', 'final_answer'
        self.tag_content = ""  # 标签内的内容
        self.complete_flag: bool = False  # action完成标志
        self.thought_complete_flag: bool = False  # thought完成标志
        self.final_answer_complete_flag: bool = False  # final_answer完成标志
        self.observation_complete_flag: bool = False  # observation完成标志
        
        self.now_action = ""
        self.step_final_answer = ""
        self.step_thought = ""
        self.step_observation = ""

    def step_parser(self):
        """从chat_session.answer_chunk中提取标签，修改成员变量"""
        chunk = self.chat_session.answer_chunk or ""
        
        if not chunk:
            return
        
        # 将chunk添加到当前文本
        self.current_text += chunk
        
        # 调试输出（注释掉以避免过多输出）
        # print(f"[DEBUG PARSER] chunk: '{chunk[:50]}...'")
        # print(f"[DEBUG PARSER] current_text: '{self.current_text[:100]}...'")
        # print(f"[DEBUG PARSER] step_tag: {self.step_tag}")
        
        # 处理当前文本
        while self.current_text:
            if self.step_tag is None:
                # 不在标签内，寻找开始标签
                # 检查所有可能的开始标签
                if "<action>" in self.current_text:
                    start_pos = self.current_text.find("<action>")
                    self.step_tag = "action"
                    self.tag_content = ""
                    self.current_text = self.current_text[start_pos + 8:]  # 8是"<action>"的长度
                elif "<thought>" in self.current_text:
                    start_pos = self.current_text.find("<thought>")
                    self.step_tag = "thought"
                    self.tag_content = ""
                    self.current_text = self.current_text[start_pos + 9:]  # 9是"<thought>"的长度
                elif "<final_answer>" in self.current_text:
                    start_pos = self.current_text.find("<final_answer>")
                    self.step_tag = "final_answer"
                    self.tag_content = ""
                    self.current_text = self.current_text[start_pos + 14:]  # 14是"<final_answer>"的长度
                elif "<observation>" in self.current_text:
                    start_pos = self.current_text.find("<observation>")
                    self.step_tag = "observation"
                    self.tag_content = ""
                    self.current_text = self.current_text[start_pos + 13:]  # 13是"<observation>"的长度
                else:
                    # 没有开始标签，清空文本
                    self.current_text = ""
            
            else:
                # 在标签内，寻找结束标签
                end_tag = f"</{self.step_tag}>"
                if end_tag in self.current_text:
                    end_pos = self.current_text.find(end_tag)
                    # 找到结束标签
                    self.tag_content += self.current_text[:end_pos]
                    
                    # 根据标签类型设置成员变量和完成标志
                    if self.step_tag == "action":
                        self.now_action = self.tag_content
                        self.complete_flag = True
                        # print(f"[DEBUG PARSER] 找到action: '{self.tag_content[:50]}...'")
                    elif self.step_tag == "thought":
                        self.step_thought = self.tag_content
                        self.thought_complete_flag = True
                        # print(f"[DEBUG PARSER] 找到thought: '{self.tag_content[:50]}...'")
                    elif self.step_tag == "final_answer":
                        self.step_final_answer = self.tag_content
                        self.final_answer_complete_flag = True
                        # print(f"[DEBUG PARSER] 找到final_answer: '{self.tag_content[:50]}...'")
                        # print(f"[DEBUG PARSER] 设置final_answer_complete_flag = True")
                    elif self.step_tag == "observation":
                        self.step_observation = self.tag_content
                        self.observation_complete_flag = True
                        # print(f"[DEBUG PARSER] 找到observation: '{self.tag_content[:50]}...'")
                    
                    # 退出标签
                    self.step_tag = None
                    self.tag_content = ""
                    self.current_text = self.current_text[end_pos + len(end_tag):]
                    # print(f"[DEBUG PARSER] 退出标签，更新current_text: '{self.current_text[:50]}...'")
                else:
                    # 没有找到结束标签，累积内容
                    self.tag_content += self.current_text
                    self.current_text = ""
                    
    def debug_step(self):
        '''流式响应Debug，功能是在切换标签的时候输出一个 思考/观察/回答/行动就可以了'''
        
    def reset(self):
        """重置解析器状态，用于新的对话"""
        self.current_text = ""
        self.step_tag = None
        self.tag_content = ""
        self.complete_flag = False
        self.thought_complete_flag = False
        self.final_answer_complete_flag = False
        self.observation_complete_flag = False
        self.now_action = ""
        self.step_final_answer = ""
        self.step_thought = ""
        self.step_observation = ""

parser_man=Parser()
