import datetime
import subprocess
import os
import re
from typing import List, Dict, Any, Optional, Iterator, Callable
from dataclasses import dataclass

class Action():
    def __init__(self):
        # 导入全局实例
        from chat.session import chatSession_man
        from tools.parser import parser_man
        from tools.prompt import get_prompt_manager
        
        # 几个大指针
        self.chatSession = chatSession_man
        self.parser = parser_man  # 指向 parser 的指针
        self.prompt_manager = get_prompt_manager()
        
        # 工具注册表
        self.tools: Dict[str, Callable] = {}
        
        # 状态机状态: idle, thought, observation, final_answer
        self.state = "idle"
        
        # 注册默认工具
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        self.register_tool("run_terminal_command", self.run_terminal_command)
        self.register_tool("read_file", self.read_file)
        self.register_tool("list_directory", self.list_directory)
    
    def register_tool(self, name: str, func: Callable):
        """注册工具函数"""
        self.tools[name] = func
    
    def parse_action_string(self, action_str: str) -> tuple[str, list]:
        """
        解析 action 字符串，格式如: tool_name(param1, param2, ...)
        返回: (工具名, 参数列表)
        """
        # 匹配工具名和参数部分
        match = re.match(r'^(\w+)\((.*)\)$', action_str.strip())
        if not match:
            raise ValueError(f"无效的 action 格式: {action_str}")
        
        tool_name = match.group(1)
        params_str = match.group(2).strip()
        
        # 如果参数为空
        if not params_str:
            return tool_name, []
        
        # 简单的参数解析（处理带引号的字符串）
        params = []
        i = 0
        while i < len(params_str):
            if params_str[i] in ('"', "'"):
                # 找到字符串参数
                quote_char = params_str[i]
                j = i + 1
                while j < len(params_str) and params_str[j] != quote_char:
                    j += 1
                if j >= len(params_str):
                    raise ValueError(f"未闭合的引号: {params_str}")
                params.append(params_str[i+1:j])
                i = j + 1
            elif params_str[i].isalnum() or params_str[i] in './\\_-':
                # 找到非字符串参数（数字、路径等）
                j = i
                while j < len(params_str) and params_str[j] not in (',', ')'):
                    j += 1
                param = params_str[i:j].strip()
                # 尝试转换为数字
                try:
                    if '.' in param:
                        param = float(param)
                    else:
                        param = int(param)
                except ValueError:
                    pass  # 保持字符串
                params.append(param)
                i = j
            elif params_str[i] == ',':
                i += 1
            elif params_str[i].isspace():
                i += 1
            else:
                raise ValueError(f"无法解析的参数: {params_str[i:]}")
        
        return tool_name, params
    
    def execute_action(self, action_str: str) -> str:
        """
        执行 action 字符串，返回观察结果
        """
        try:
            # 解析 action
            tool_name, params = self.parse_action_string(action_str)
            
            # 检查工具是否存在
            if tool_name not in self.tools:
                return f"错误: 未知工具 '{tool_name}'。可用工具: {', '.join(self.tools.keys())}"
            
            # 执行工具
            tool_func = self.tools[tool_name]
            result = tool_func(*params)
            
            # 返回观察结果
            return str(result)
            
        except Exception as e:
            return f"错误执行 action '{action_str}': {str(e)}"
    
    def run_terminal_command(self, command: str) -> str:
        """
        执行终端命令
        """
        try:
            # 安全检查：禁止某些危险命令
            dangerous_patterns = ['rm -rf', 'format', 'del /', 'shutdown', 'halt']
            for pattern in dangerous_patterns:
                if pattern in command.lower():
                    return f"安全限制: 禁止执行可能危险的命令 '{command}'"
            
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30秒超时
            )
            
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            
            return output.strip() or "命令执行成功（无输出）"
            
        except subprocess.TimeoutExpired:
            return "错误: 命令执行超时（30秒）"
        except Exception as e:
            return f"错误执行命令: {str(e)}"
    
    def read_file(self, file_path: str) -> str:
        """
        读取文件内容
        """
        try:
            # 安全检查：限制路径
            if not os.path.exists(file_path):
                return f"错误: 文件不存在 '{file_path}'"
            
            # 检查是否为文件
            if not os.path.isfile(file_path):
                return f"错误: '{file_path}' 不是文件"
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 限制输出长度
            max_length = 5000
            if len(content) > max_length:
                content = content[:max_length] + f"\n...（已截断，总长度 {len(content)} 字符）"
            
            return content
            
        except UnicodeDecodeError:
            return f"错误: 无法以 UTF-8 解码文件 '{file_path}'（可能是二进制文件）"
        except Exception as e:
            return f"错误读取文件: {str(e)}"
    
    def list_directory(self, path: str = ".") -> str:
        """
        列出目录内容
        """
        try:
            # 安全检查
            if not os.path.exists(path):
                return f"错误: 路径不存在 '{path}'"
            
            if not os.path.isdir(path):
                return f"错误: '{path}' 不是目录"
            
            # 列出目录内容
            items = os.listdir(path)
            
            # 分类显示
            dirs = []
            files = []
            
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    dirs.append(f"[目录] {item}/")
                else:
                    size = os.path.getsize(item_path)
                    files.append(f"[文件] {item} ({size} 字节)")
            
            # 排序
            dirs.sort()
            files.sort()
            
            # 组合输出
            output = []
            if dirs:
                output.append("目录:")
                output.extend(dirs)
            if files:
                if output:
                    output.append("")
                output.append("文件:")
                output.extend(files)
            
            if not output:
                return "目录为空"
            
            return "\n".join(output)
            
        except Exception as e:
            return f"错误列出目录: {str(e)}"
    
    def process_actions(self):
        """
        处理解析器中的 action，应在主循环中调用
        返回: 是否需要继续处理（True/False）
        """
        # 检查是否有完成的 thought
        if self.parser.thought_complete_flag:
            self.state = "thought"
            self.parser.thought_complete_flag = False
            # thought 不需要特殊处理，只是状态更新
        
        # 检查是否有完成的 action
        if self.parser.complete_flag:
            action_str = self.parser.now_action
            if action_str:
                # 执行 action
                observation = self.execute_action(action_str)
                
                # 重置 parser 的 action 标志
                self.parser.complete_flag = False
                self.parser.now_action = ""
                
                # 将观察结果添加到消息列表
                observation_msg = f"<observation>{observation}</observation>"
                self.chatSession.messages_list.append({
                    'role': 'user',
                    'content': observation_msg
                })
                
                # 更新状态
                self.state = "observation"
                return True
        
        # 检查是否有完成的 final_answer
        if self.parser.final_answer_complete_flag:
            self.state = "final_answer"
            self.parser.final_answer_complete_flag = False
            # final_answer 表示对话结束
        
        # 检查是否有完成的 observation（来自其他来源）
        if self.parser.observation_complete_flag:
            self.state = "observation"
            self.parser.observation_complete_flag = False
        
        return False

action_man = Action()
