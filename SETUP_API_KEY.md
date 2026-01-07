# API 密钥设置指南

## 安全存储 API 密钥

本项目使用环境变量安全存储 API 密钥，避免将敏感信息硬编码在代码中。

## 当前配置

API 密钥存储在：`data/KEY/.env`

`.env` 文件内容：
```
DEEPSEEK_API_KEY=ms-1c9cc707-01e0-46ef-8f53-d202a207d74f
```

## 代码实现

在 `src/api/LLM.py` 中，代码从指定路径加载 `.env` 文件：

```python
import os
from dotenv import load_dotenv

# 加载指定路径的 .env 文件
env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'KEY', '.env')
load_dotenv(env_path)

# 从环境变量读取 API 密钥
api_key = os.getenv('DEEPSEEK_API_KEY')
if not api_key:
    raise ValueError(f"DEEPSEEK_API_KEY 环境变量未设置。请检查 .env 文件: {env_path}")
```

## 安全注意事项

1. **`.env` 文件已加入 `.gitignore`**：确保不会提交到版本控制系统
2. **路径固定**：代码明确指定 `.env` 文件位置，避免配置错误
3. **错误提示**：如果 API 密钥未设置，会显示明确的错误信息

## 如何更改 API 密钥位置

如果需要更改 `.env` 文件位置，修改 `src/api/LLM.py` 中的 `env_path`：

```python
# 示例：改为项目根目录下的 .env 文件
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')

# 示例：改为绝对路径
env_path = "T:/Mardio's G4/C_thinking/KEY/.env"
```

## 依赖

需要安装 `python-dotenv` 包：
```bash
pip install python-dotenv
```

## 验证

运行测试验证 API 密钥是否正确加载：
```bash
python test_api_key.py
```

## 最佳实践

1. **不同环境不同密钥**：开发、测试、生产环境使用不同的 API 密钥
2. **定期轮换**：定期更换 API 密钥以提高安全性
3. **最小权限**：为 API 密钥设置最小必要权限
4. **监控使用**：监控 API 使用情况，检测异常行为
