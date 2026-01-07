# C_core - 马丢的AI对话核心

## 前言

人工智能导论课大作业的一部分，纯犯贱，考完化学一拍脑袋就开始造轮子了，画了三天才做完，都没时间复习了。
马丢版本的AI AGENT工具，创新点是没有，优点是自己做的可以客制化，后续可以升级，缺点是唐

## 快速开始

### 环境要求
- Python 3.11+ （我用的是3.11，理论上3.10也行，但没试过）
- 一个能用的DeepSeek API密钥（免费申请，后面会讲）
- 一点耐心（配置环境总会有各种小问题）

### 安装步骤

#### 1. 克隆项目
```bash
cd 你的项目目录
git clone https://github.com/你的仓库/C_core.git
cd C_core
```

#### 2. 安装依赖
推荐用 `uv`（快，而且省心）：
```powershell
# PowerShell里用分号分隔命令，不是&&
uv venv; .\.venv\Scripts\activate; uv pip install -e .
```

或者用传统的 `pip`：
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

#### 3. 配置API密钥
1. 去 [DeepSeek官网](https://platform.deepseek.com/) 注册账号，申请API密钥
2. 在项目里创建文件：`data/KEY/.env`
3. 写入你的密钥（注意变量名是 `DEEPSEEK_API_KEY_2`）：
```
DEEPSEEK_API_KEY_2=你的密钥在这里
```

**注意**：`.env` 文件已经在 `.gitignore` 里了，不会提交到Git。别把密钥硬编码在代码里。

**为什么是 `DEEPSEEK_API_KEY_2`？**：代码里写死了这个变量名，历史原因。你可以改代码，也可以改 `.env` 文件。

#### 4. 运行测试
```powershell
python src/main.py
```

如果一切正常，你会看到：
```
马丢启动...
你: 
```
输入点什么，比如"你好"，然后看AI怎么回应。能看到思考过程（如果开了thinking模式）。

## 项目架构

### 核心组件

```
ChatSession (数据源)
      ↓ 产生chunk
   Parser (处理器)
      ↓ 解析结果，控制状态机
   Action Manager (执行器)
      ├── 显示文本
      ├── 执行工具
      └── 管理状态
```

#### 1. ChatSession (`src/chat/session.py`)
- 管理对话历史和上下文
- 处理流式响应，分离thinking和answer
- 单例模式，全局一个实例 `chatSession_man`

#### 2. Parser (`src/tools/parser.py`)
- 解析AI的流式响应
- 控制状态机（complete_flag, stop_flag）
- 检测是否需要执行工具

#### 3. Action Manager (`src/tools/action.py`)
- 执行具体的工具调用
- 处理工具返回结果
- 管理执行状态

#### 4. LLM API (`src/api/LLM.py`)
- DeepSeek API的封装
- 单例客户端，避免重复创建连接
- 支持thinking模式（`enable_thinking: true`）

### 数据流
```
用户输入
    ↓
系统提示 + 历史消息
    ↓
DeepSeek API (流式)
    ↓
thinking chunk / answer chunk
    ↓
Parser解析 → 需要工具？ → Action执行
    ↓
结果显示 → 更新消息历史
```

## 详细配置

### API密钥设置

项目默认从 `data/KEY/.env` 读取密钥。如果你想改位置，修改 `src/api/LLM.py`：

```python
# 默认路径
env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'KEY', '.env')

# 可以改成项目根目录
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')

# 或者绝对路径（Windows）
env_path = "T:/Mardio's G4/C_thinking/KEY/.env"
```

### 模型配置

在 `src/api/LLM.py` 里可以改模型和API地址：

```python
MODEL = 'deepseek-chat'  # 或者 'deepseek-ai/DeepSeek-V3.2'
BASE_URL = 'https://api.deepseek.com'  # 或者 'https://api-inference.modelscope.cn/v1'
```

### 思考模式

默认开启thinking，能看到AI的推理过程。如果想关闭：

```python
extra_body = {
    "enable_thinking": False  # 关掉thinking
}
```

## 使用示例

### 基本对话
```
马丢启动...
你: 你好，介绍一下你自己
[AI的thinking过程...]
-------
你好！我是DeepSeek，一个AI助手...
```

### 观察思考过程
开启thinking后，你会先看到AI的推理（灰色文字），然后才是正式回答。

### 工具调用
项目预留了工具调用接口，可以在 `src/tools/action.py` 里添加你自己的工具。

## 开发指南

### 代码结构
```
C_core/
├── src/
│   ├── api/          # LLM API封装
│   ├── chat/         # 对话管理
│   └── tools/        # 解析器、动作、提示词
├── data/             # 数据文件
│   └── KEY/          # API密钥（.gitignore）
├── doc/              # 文档
└── tests/            # 测试（如果有）
```

### 添加新工具
1. 在 `src/tools/action.py` 的 `process_actions` 方法里添加你的工具逻辑
2. 在Parser里检测对应的工具调用标记
3. 更新提示词系统（如果需要）

### 扩展解析器
Parser使用状态机模式，可以添加新的状态来支持更复杂的交互。

## 常见问题

### 1. "DEEPSEEK_API_KEY 环境变量未设置"
检查 `data/KEY/.env` 文件是否存在，格式是否正确。注意密钥变量名是 `DEEPSEEK_API_KEY_2`（代码里写的是这个，但错误信息显示的是 `DEEPSEEK_API_KEY`，这是代码里的笔误）。

### 2. 连接超时或网络错误
- 检查网络连接
- 确认API地址是否正确（国内用户可能需要用modelscope的地址）
- 确认API密钥是否有效

### 3. Python版本问题
项目需要Python 3.11+。检查你的版本：
```bash
python --version
```

如果版本太低，建议用 `pyenv` 或 `conda` 管理多版本。

### 4. 依赖安装失败
尝试：
```bash
# 更新pip
python -m pip install --upgrade pip

# 或者用uv（推荐）
uv pip install -e .
```

### 5. 流式响应不显示thinking
确认 `enable_thinking` 设置为 `True`，并且你的API密钥支持thinking功能。

## 安全注意事项

1. **不要提交密钥**：`.env` 已经在 `.gitignore` 里，但还是要double-check
2. **不同环境用不同密钥**：开发、测试、生产环境分开
3. **监控使用量**：DeepSeek有免费额度，但超出要收费
4. **定期轮换密钥**：安全起见，定期更换API密钥

## 未来计划

### 短期
- [ ] Web界面（简单的HTML+JS）
- [ ] 更多工具集成（搜索、计算、文件操作）
- [ ] 对话历史持久化

### 长期
- [ ] 插件系统
- [ ] 多模型支持（不只是DeepSeek）
- [ ] 分布式部署

## 贡献

如果你有兴趣一起搞：
1. Fork项目
2. 创建功能分支
3. 提交Pull Request
4. 保持代码风格一致（用ruff格式化）

## 最后

我一开始觉得导论课挺水的，后来加了点东西感觉挺好，所以大作业决定B级认真对待一下

马丢
2025.1.8 凌晨
