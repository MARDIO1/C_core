# CLI聊天程序实现总结

## 已完成的工作

### 1. 包结构配置
- 创建了 `src/__init__.py` - 顶级包
- 创建了 `src/api/__init__.py` - API子包
- 创建了 `src/core/__init__.py` - Core子包
- 创建了 `src/client/__init__.py` - Client子包

### 2. 导入系统配置
- 修改了 `src/core/main.py` 使用正确的导入路径
- 添加了Python路径配置，支持从任何位置运行
- 测试验证了包导入和LLM API调用

### 3. 当前文件结构
```
src/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── LLM_api.py          # 现有的LLM API封装
├── core/
│   ├── __init__.py
│   └── main.py             # 主程序入口
└── client/
    └── __init__.py
```

## 完整的CLI聊天程序示例

以下是一个包含上下文、token计数和时间戳的完整CLI聊天程序：

```python
# src/chat/cli_chat.py
import sys
import os
import datetime
from typing import List, Dict, Any

# 添加src到路径
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, '..')
sys.path.append(src_dir)

from api.LLM_api import init, step

class ChatManager:
    """聊天管理器：处理上下文、token计数和时间戳"""
    
    def __init__(self):
        self.messages: List[Dict] = []
        self.total_tokens = 0
        self.start_time = datetime.datetime.now()
        
    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "token_count": self._estimate_tokens(content)
        }
        self.messages.append(message)
        self.total_tokens += message["token_count"]
        
    def get_conversation_for_api(self) -> List[Dict]:
        """获取API需要的对话格式"""
        return [{"role": msg["role"], "content": msg["content"]} 
                for msg in self.messages]
    
    def display_conversation(self):
        """显示完整的对话历史"""
        print("\n" + "="*60)
        print("对话历史：")
        print("="*60)
        for msg in self.messages:
            time_str = msg["timestamp"]
            role_str = "用户" if msg["role"] == "user" else "AI"
            print(f"[{time_str}] {role_str}: {msg['content'][:50]}...")
        print(f"总token数: {self.total_tokens}")
        print("="*60)
    
    def _estimate_tokens(self, text: str) -> int:
        """简单估算token数（实际应该使用tiktoken）"""
        return len(text) // 4
    
    def clear(self):
        """清空对话历史"""
        self.messages = []
        self.total_tokens = 0
        print("对话历史已清空")

def main():
    """CLI聊天主程序"""
    print("="*60)
    print("大模型CLI聊天程序")
    print("功能：上下文管理 | Token计数 | 时间戳记录")
    print("命令：/clear 清空历史 | /stats 查看统计 | /exit 退出")
    print("="*60)
    
    chat_manager = ChatManager()
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n你: ").strip()
            
            if not user_input:
                continue
                
            # 处理特殊命令
            if user_input == '/exit':
                print("再见！")
                break
            elif user_input == '/clear':
                chat_manager.clear()
                continue
            elif user_input == '/stats':
                chat_manager.display_conversation()
                continue
            elif user_input == '/help':
                print("可用命令：")
                print("  /clear - 清空对话历史")
                print("  /stats - 查看对话统计")
                print("  /exit  - 退出程序")
                print("  /help  - 显示帮助")
                continue
                
            # 添加用户消息
            chat_manager.add_message("user", user_input)
            
            # 显示AI回复（带时间戳）
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{current_time}] AI: ", end="", flush=True)
            
            # 注意：这里需要修改LLM_api.py以支持传入消息
            # 当前版本使用硬编码消息，需要扩展
            
            # 临时方案：使用现有的init()函数
            response = init()  # 这使用硬编码消息
            
            # 处理流式响应
            # 这里需要修改step()函数以支持自定义处理
            step(response)
            
            # 添加AI回复到历史（需要从响应中提取内容）
            # 当前版本step()直接打印，需要修改以返回内容
            
        except KeyboardInterrupt:
            print("\n\n程序被中断")
            break
        except Exception as e:
            print(f"\n错误: {e}")

if __name__ == "__main__":
    main()
```

## 需要扩展的LLM API功能

要使上述CLI聊天程序完全工作，需要修改 `LLM_api.py`：

### 扩展1：支持自定义消息
```python
def init_with_messages(messages: List[Dict]):
    """使用自定义消息初始化LLM"""
    from openai import OpenAI
    client = OpenAI(
        base_url='https://api-inference.modelscope.cn/v1',
        api_key='ms-1c9cc707-01e0-46ef-8f53-d202a207d74f',
    )
    
    extra_body = {"enable_thinking": True}
    response = client.chat.completions.create(
        model='deepseek-ai/DeepSeek-V3.2',
        messages=messages,
        stream=True,
        extra_body=extra_body
    )
    return response
```

### 扩展2：step()函数返回内容
```python
def step_with_return(response):
    """处理流式响应并返回完整内容"""
    full_response = ""
    done_thinking = False
    
    for chunk in response:
        if chunk.choices:
            thinking_chunk = chunk.choices[0].delta.reasoning_content
            answer_chunk = chunk.choices[0].delta.content

            if thinking_chunk:
                print(thinking_chunk, end='', flush=True)
            elif answer_chunk:
                if not done_thinking:
                    print('\n\n ------最终回答------\n')
                    done_thinking = True
                print(answer_chunk, end='', flush=True)
                full_response += answer_chunk
    
    return full_response
```

## 运行方式

1. **当前版本**：
```bash
cd t:\Mardio's G4\mardio_project\C_core
python src/core/main.py
```

2. **完整CLI聊天程序**（需要扩展LLM API后）：
```bash
python src/chat/cli_chat.py
```

## 总结

我们已经成功：
1. 配置了Python包结构
2. 实现了正确的模块导入
3. 验证了LLM API调用
4. 设计了完整的CLI聊天程序架构

下一步可以根据需要扩展LLM API功能，实现完整的上下文管理、token计数和时间戳功能。
