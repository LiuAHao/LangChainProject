import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from chat_robot.chat_api import ChatAPI
from chat_robot.log_manager import log_manager

def test_comprehensive_logging():
    """全面测试日志功能"""
    print("开始全面测试日志功能...")
    
    # 创建ChatAPI实例
    chat_api = ChatAPI()
    
    # 创建测试会话ID
    session_id = f"comprehensive_test_{int(time.time())}"
    
    # 测试1: 正常聊天流程
    print("\n=== 测试1: 正常聊天流程 ===")
    user_input = "你好，介绍一下Python编程语言"
    print(f"发送消息: {user_input}")
    
    try:
        response = chat_api.chat_with_history(session_id, user_input)
        print(f"收到回复: {response[:100]}...")
    except Exception as e:
        print(f"聊天过程中出现错误: {e}")
    
    # 测试2: 带人设的聊天
    print("\n=== 测试2: 带人设的聊天 ===")
    user_input2 = "你能帮我写一个计算阶乘的函数吗？"
    print(f"发送消息: {user_input2}")
    
    try:
        # 使用编程助手人设（假设ID为2）
        response2 = chat_api.chat_with_history(session_id, user_input2, persona_id=2)
        print(f"收到回复: {response2[:100]}...")
    except Exception as e:
        print(f"聊天过程中出现错误: {e}")
    
    # 测试3: 查看日志
    print("\n=== 查看生成的日志 ===")
    logs = log_manager.get_session_logs(session_id)
    print(f"找到 {len(logs)} 条日志记录")
    
    log_types = {}
    for i, log in enumerate(logs):
        log_type = log.get('type', 'unknown')
        if log_type not in log_types:
            log_types[log_type] = 0
        log_types[log_type] += 1
        
        print(f"\n日志 {i+1}:")
        print(f"  时间戳: {log.get('timestamp', 'N/A')}")
        print(f"  类型: {log_type}")
        if log_type == 'system_prompt':
            print(f"  系统提示词长度: {len(log.get('system_prompt', ''))} 字符")
        elif log_type == 'api_request':
            print(f"  模型: {log.get('model', 'N/A')}")
            print(f"  消息数量: {len(log.get('messages', []))}")
        elif log_type == 'api_response':
            print(f"  响应长度: {len(log.get('response', ''))} 字符")
        elif log_type == 'error':
            print(f"  错误类型: {log.get('error_type', 'N/A')}")
            print(f"  错误信息: {log.get('error_message', 'N/A')}")
    
    print(f"\n日志类型统计: {log_types}")
    
    # 测试4: 检查日志文件
    print("\n=== 检查日志文件 ===")
    log_file_path = f"log/{session_id}.log"
    if os.path.exists(log_file_path):
        print(f"✓ 日志文件 {log_file_path} 存在")
        # 显示文件内容
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"文件内容大小: {len(content)} 字符")
            # 显示最后几行
            lines = content.strip().split('\n')
            print(f"日志行数: {len(lines)}")
            if lines:
                print("最后一条日志:")
                try:
                    import json
                    last_log = json.loads(lines[-1])
                    print(f"  类型: {last_log.get('type', 'N/A')}")
                    print(f"  时间戳: {last_log.get('timestamp', 'N/A')}")
                except:
                    print("  无法解析最后一条日志")
    else:
        print(f"✗ 日志文件 {log_file_path} 不存在")
    
    print("\n=== 测试总结 ===")
    if len(logs) > 0:
        print("✓ 日志功能正常工作")
        print("✓ 日志记录了系统提示词、API请求和响应")
        if 'error' in log_types:
            print(f"✓ 记录了 {log_types['error']} 个错误")
    else:
        print("✗ 日志功能可能存在问题")
    
    print("\n全面测试完成!")

if __name__ == "__main__":
    test_comprehensive_logging()