# src/core/main.py
"""
主程序 - 使用包结构导入LLM API
"""
# 现在可以直接导入
from api.LLM import init, step

def main():
    """主函数"""
    print("开始LLM对话...")
    
    # 获取响应
    response = init()
    
    # 处理流式输出
    step(response)
    
    print("\n对话结束")

if __name__ == "__main__":
    main()
