import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from chat_robot.chat_api import ChatAPI
from chat_robot.log_manager import log_manager

def test_logging_function():
    """测试日志功能是否正常工作"""
    print("开始测试日志功能...")
    
    # 创建ChatAPI实例
    chat_api = ChatAPI()
    
    # 创建测试会话ID
    session_id = f"test_logging_{int(time.time())}"
    
    # 测试聊天功能
    user_input = "你好，这是一个测试消息"
    print(f"发送消息: {user_input}")
    
    try:
        response = chat_api.chat_with_history(session_id, user_input)
        print(f"收到回复: {response}")
    except Exception as e:
        print(f"聊天过程中出现错误: {e}")
    
    # 查看日志
    print("\n查看生成的日志:")
    logs = log_manager.get_session_logs(session_id)
    print(f"找到 {len(logs)} 条日志记录")
    
    for i, log in enumerate(logs):
        print(f"\n日志 {i+1}:")
        print(f"  时间戳: {log.get('timestamp', 'N/A')}")
        print(f"  类型: {log.get('type', 'N/A')}")
        if log.get('type') == 'system_prompt':
            print(f"  系统提示词: {log.get('system_prompt', 'N/A')[:100]}...")
        elif log.get('type') == 'api_request':
            print(f"  模型: {log.get('model', 'N/A')}")
            print(f"  消息数量: {len(log.get('messages', []))}")
        elif log.get('type') == 'api_response':
            print(f"  响应: {log.get('response', 'N/A')[:100]}...")
        elif log.get('type') == 'error':
            print(f"  错误类型: {log.get('error_type', 'N/A')}")
            print(f"  错误信息: {log.get('error_message', 'N/A')}")
    
    # 检查日志文件是否存在
    log_file_path = f"log/{session_id}.log"
    if os.path.exists(log_file_path):
        print(f"\n✓ 日志文件 {log_file_path} 存在")
        # 显示文件内容
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"文件内容大小: {len(content)} 字符")
    else:
        print(f"\n✗ 日志文件 {log_file_path} 不存在")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_logging_function()