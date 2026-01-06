# src/chat/session.py
import datetime
#import sys
#import os
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass

# 添加src目录到路径，以便可以导入api模块
# 其实根本不需要sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 导入自己的模块
import api.LLM 
@dataclass
class ChatConfig:
    enable_thinking: bool = True
    record_tokens: bool = True
    add_timestamps: bool = True

class ChatSession:
    '''非常重要的类！'''
    def __init__(self, config: Optional[ChatConfig] = None):
        self.start_time: datetime.datetime = datetime.datetime.now()
        # 初始化客户端
        api.LLM.client_init()
        # 响应对象，使用类型提示
        self.current_response: Optional[Iterator] = None
        self.chunk: Optional[Any] = None
        self.thinking_chunk: Optional[str] = None
        self.answer_chunk: Optional[str] = None
        # 配置
        self.config = config or ChatConfig()
        # 数据存储
        self.thinking_list: List[Dict[str, Any]] = []
        self.answer_list: List[Dict[str, Any]] = []
        self.messages_list: List[Dict[str, Any]] = []
        
    def new_input_get_LLMresponse(self, input_string: str) -> None:
        '''发送消息并获取响应'''
        # 添加用户消息
        self.messages_list.append({'role': 'user', 'content': input_string})
        # 获取响应
        self.current_response = api.LLM.new_response_init(self.messages_list)

    def streaming_get_API_response(self) -> bool:
        '''获取API响应'''
        if self.current_response is None:
            return False
        
        try:
            chunk = next(self.current_response)
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                # 使用getattr安全访问属性
                self.thinking_chunk = getattr(delta, 'reasoning_content', '')
                self.answer_chunk = getattr(delta, 'content', '')

                if self.thinking_chunk:
                    self.thinking_list.append({'role': 'thinking', 'content': self.thinking_chunk})
                if self.answer_chunk:
                    self.answer_list.append({'role': 'answer', 'content': self.answer_chunk})
                    # 收集完整的AI回复
                    if not hasattr(self, '_current_ai_reply'):
                        self._current_ai_reply = ""
                    self._current_ai_reply += self.answer_chunk
                return True
        except StopIteration:
            # 响应完成，将完整的AI回复添加到messages_list
            '''if hasattr(self, '_current_ai_reply') and self._current_ai_reply:
                self.messages_list.append({'role': 'assistant', 'content': self._current_ai_reply})
                del self._current_ai_reply'''#麻烦得很
            return False  # 没有更多数据
        except Exception:
            return False
        
        return False
    
    def one_step(self):
        self.new_input_get_LLMresponse(input())

    def streaming_show_step(self):
        #如果thinking_chunk非空
        if self.thinking_chunk != '':
            print(self.thinking_chunk, end='', flush=True)
        #如果thinking空了，answer非空
        elif self.answer_chunk != '':
            print(self.answer_chunk, end='', flush=True)
            

        '''发送到web端的通讯部分开始'''
        '''发送到web端的通讯部分结束'''

chatSession_man=ChatSession()#全局变量，单例