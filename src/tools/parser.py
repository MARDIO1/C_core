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
        self.stop_flag = False  # 更大的flag，只有final_answer会设置为true

    def step_parser(self):
        """从chat_session.answer_chunk中提取标签，修改成员变量"""
        chunk = self.chat_session.answer_chunk or ""
        
        if not chunk:
            return
        
        # 将chunk添加到当前文本
        self.current_text += chunk
        
        # 调试输出（已注释掉）
        # print(f"[DEBUG PARSER] chunk: '{chunk[:100]}...'")
        # print(f"[DEBUG PARSER] current_text (处理前): '{self.current_text[:200]}...'")
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
                    # 没有完整的开始标签，检查是否有部分开始标签
                    # 检查 current_text 是否以 '<' 开头，或者包含任何开始标签的开始部分
                    has_partial_start = False
                    
                    # 情况1：current_text 以 '<' 开头（可能是开始标签的开始）
                    if self.current_text.startswith("<"):
                        has_partial_start = True
                        # print(f"[DEBUG PARSER] current_text 以 '<' 开头，可能是开始标签，等待更多chunk")
                    
                    # 情况2：检查是否有部分开始标签（如 "<thought"）
                    if not has_partial_start:
                        for tag_name in ["action", "thought", "final_answer", "observation"]:
                            partial_start = f"<{tag_name}"
                            if partial_start in self.current_text:
                                # 有部分开始标签，等待更多chunk
                                has_partial_start = True
                                # print(f"[DEBUG PARSER] 检测到部分开始标签 '{partial_start}'，等待更多chunk")
                                break
                    
                    if has_partial_start:
                        # 有部分开始标签，等待更多chunk
                        # 不清空 current_text
                        break
                    else:
                        # 完全没有开始标签的任何部分，清空文本
                        # 但保留最后几个字符，以防标签被分割
                        if len(self.current_text) > 10:
                            # 保留最后10个字符
                            self.current_text = self.current_text[-10:]
                            # print(f"[DEBUG PARSER] 清空大部分文本，保留最后10字符: '{self.current_text}'")
                        else:
                            # print(f"[DEBUG PARSER] 清空 current_text: '{self.current_text}'")
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
                        # print(f"[DEBUG PARSER] 找到action: '{self.tag_content[:100]}...'")
                    elif self.step_tag == "thought":
                        self.step_thought = self.tag_content
                        self.thought_complete_flag = True
                        # print(f"[DEBUG PARSER] 找到thought: '{self.tag_content[:100]}...'")
                    elif self.step_tag == "final_answer":
                        self.step_final_answer = self.tag_content
                        self.final_answer_complete_flag = True
                        self.stop_flag = True  # 设置stop_flag为true
                        # print(f"[DEBUG PARSER] 找到final_answer: '{self.tag_content[:100]}...'")
                        # print(f"[DEBUG PARSER] 设置final_answer_complete_flag = True")
                        # print(f"[DEBUG PARSER] 设置stop_flag = True")
                    elif self.step_tag == "observation":
                        self.step_observation = self.tag_content
                        self.observation_complete_flag = True
                        # print(f"[DEBUG PARSER] 找到observation: '{self.tag_content[:100]}...'")
                    
                    # 退出标签
                    self.step_tag = None
                    self.tag_content = ""
                    self.current_text = self.current_text[end_pos + len(end_tag):]
                    # print(f"[DEBUG PARSER] 退出标签，更新current_text: '{self.current_text[:100]}...'")
                    # print(f"[DEBUG PARSER] 继续while循环处理剩余内容")
                else:
                    # 没有找到结束标签，但可能有部分结束标签
                    # 检查是否有结束标签的开始部分
                    partial_end_tag = f"</{self.step_tag}"
                    
                    # 情况1：current_text 包含 '</'（可能是结束标签的开始）
                    if "</" in self.current_text:
                        # 可能是结束标签的开始，等待更多chunk
                        # 不清空 current_text
                        break
                    
                    # 情况2：检查是否有部分结束标签（如 "</thought"）
                    elif partial_end_tag in self.current_text:
                        # 有部分结束标签，等待更多chunk
                        # 不清空 current_text，等待完整结束标签
                        break
                    else:
                        # 没有结束标签的任何部分，累积内容
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
        self.stop_flag = False  # 重置stop_flag
        self.now_action = ""
        self.step_final_answer = ""
        self.step_thought = ""
        self.step_observation = ""

parser_man=Parser()
