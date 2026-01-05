# src/chat/session.py
import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from urllib import response
#自己的模块
import api.LLM 
@dataclass
class ChatConfig:
    enable_thinking: bool = True
    record_tokens: bool = True
    add_timestamps: bool = True

class ChatSession:
    '''非常重要的类！'''
    def __init__(self, config: Optional[ChatConfig] = None):
        #别人的复杂初始化
        #"创建一个名为messages_list的对象属性，它是一个列表，列表中的每个元素都是字典，字典的键是字符串，值可以是任意类型。初始化为空列表。"
        self.start_time: datetime.datetime = datetime.datetime.now()
        api.LLM.client_init()
        #self.response=None #api.LLM.response_init()#这个很大其实
        self.current_response = None
        self.chunk=None
        self.thinking_chunk =None
        self.answer_chunk =None
        #我们自己的数据结构
        # 使用 Optional[ChatConfig] 表示config可以是ChatConfig或None，真的是莫名其妙
        self.config = config or ChatConfig()
        self.thinking_list: List[Dict[str, Any]] = []
        self.answer_list: List[Dict[str, Any]] = []
        self.messages_list: List[Dict[str, Any]] = []
        
    def input_and_get_response(self,input_string):
        '''整块消息发送，可惜没有流式发送'''
        #self.messages_list.append(input_string)
        #self.response.message["content"]=self.messages_list
        """发送消息"""
        # 添加用户消息
        self.messages_list.append({'role': 'user', 'content': input_string})
        # 获取响应
        self.current_response = api.LLM.new_response_init(input_string)

    def get_API_response(self):
        '''获取API响应'''
        try:
            chunk = next(self.current_response)
            if chunk.choices: 
                self.thinking_chunk = chunk.choices[0].delta.reasoning_content
                self.answer_chunk = chunk.choices[0].delta.content

                if self.thinking_chunk != '':
                    self.thinking_list.append({'role': 'thinking', 'content': self.thinking_chunk})
                if self.answer_chunk != '':
                    self.answer_list.append({'role': 'answer', 'content': self.answer_chunk})
            return True
        except StopIteration:
            return False  # 没有更多数据
    
    def step(self):
        self.input_and_get_response(input())

    def fast_show_step(self):
        #如果thinking_chunk非空
        if self.thinking_chunk != '':
            print(self.thinking_chunk, end='', flush=True)
        #如果thinking空了，answer非空
        elif self.answer_chunk != '':
            #print('\n\n ------最终回答------\n')
            print(self.answer_chunk, end='', flush=True)

        