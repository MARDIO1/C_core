"""
工具调用提示词管理器
"""
from typing import List,Dict, Optional
from string import Template

class ToolPromptManager:
    """管理工具调用的提示词"""
    
    # 总的提示词模版
    AGENT_PROMPT_TEMPLATE = \
    """你是一个可以调用工具的AI助手。使用ReAct（Reasoning-Acting）模式：

    思考-行动-观察循环：
    1. 先思考（<thought>...</thought>）
    2. 然后行动（<action>工具名(参数)</action>）
    3. 观察结果（<observation>...</observation>）
    4. 重复直到得到最终答案（<final_answer>...</final_answer>）
    5. 必须使用final_answer一轮发言才会结束。如果用户只需要观察，那么观察后总结就是最终结果

    可用工具：
    ${tool_list}

    当前工作目录：${project_directory}

    格式示例：
    用户：列出当前目录
    AI：<thought>我需要使用list_directory工具查看当前目录</thought>
    <action>list_directory(".")</action>
    <observation>...</observation>
    <final_answer>当前目录有......你还需要..吗？</final_answer>
    重要规则：
    1. 一次只调用一个工具
    2. 等待观察结果后再继续
    3. 使用XML标签格式
    4. 最终答案用<final_answer>标签。必须使用final_answer一轮发言才会结束
    5. 回答尽量精简，觉得可以听下就使用<final_answer>结束。
    """

    def __init__(self, project_directory: Optional[str] = None):
        self.project_directory = project_directory or "."
        #工作目录，默认当前目录
        self.tools_dic :Dict= {}#工具字典
        
    def register_tools_step(self, tool_name: str, description: str, params: str = ""):
        """注册工具"""
        #添加了一个备注功能，我觉得没用
        self.tools_dic[tool_name] = {
            "description": description,
            "params": params,
        }

    # 一个工具的描述模板
    TOOL_DESCRIPTION_TEMPLATE = \
    """${tool_name}(${params}): ${description}"""
    def get_tool_list_text(self) -> str:
        """把之前的字典格式化生成一个AI能看懂的字符串，返回字符串"""
        tool_descriptions :List[str] = []
        #tool_descriptions: Optional[List[str]] = None
        for tool_name, tool_info in self.tools_dic.items():
            #这是字典的一个方法，它会返回一个可迭代的视图对象，这个对象可以生成一系列的键值对。每次迭代，它会提供一个 (key, value) 的元组。
            temp_des = Template(self.TOOL_DESCRIPTION_TEMPLATE).substitute(
                tool_name=tool_name,
                params=tool_info["params"],
                description=tool_info["description"]
            )#唉写法太麻烦了，有什么方便的吗。。好吧也还行
            tool_descriptions.append(temp_des)
        return "\n".join(tool_descriptions)
    
    def get_system_prompt(self) -> str:
        """获取完整的系统提示"""
        tool_list = self.get_tool_list_text()#组装tool list
        return Template(self.AGENT_PROMPT_TEMPLATE).substitute(
            tool_list=tool_list,
            project_directory=self.project_directory
        )
    
    def create_agent_promote(self, user_input: str, use_tools: bool = True) -> list:
        """创建消息列表"""
        if use_tools:
            system_prompt = self.get_system_prompt()
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        else:
            return [{"role": "user", "content": user_input}]
    
    def register_default_tools(self):
        """注册默认工具"""
        self.register_tools_step(
            tool_name="run_terminal_command",
            params="command: str",
            description="执行终端命令"
        )
        
        self.register_tools_step(
            tool_name="read_file",
            params="file_path: str",
            description="读取文件内容"
        )
        
        self.register_tools_step(
            tool_name="list_directory",
            params="path: str = '.'",
            description="列出目录内容"
        )

# 全局实例
prompt_man = None
def get_prompt_manager(project_directory: Optional[str] = None) -> ToolPromptManager:
    """获取提示词管理器实例"""
    global prompt_man
    if prompt_man is None:
        prompt_man = ToolPromptManager(project_directory)
        prompt_man.register_default_tools()
    return prompt_man
