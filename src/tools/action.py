from src.tools.prompt import ToolPromptManager,prompt_man
from src.chat.session import ChatSession,chatSession_man
from src.tools.parser import Parser,parser_man
import datetime
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass

class Action():
    def __init__(self):
        #几个大指针
        self.chatSession=chatSession_man
        self.parser=parser_man
        self.prompt=prompt_man

action_man=Action()