import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from chat_robot.log_manager import log_manager
import time

def debug_logging():
    """调试日志功能"""
    print("开始调试日志功能...")
    
    # 检查日志目录
    print(f"日志目录: {log_manager.log_dir}")
    print(f"日志目录是否存在: {log_manager.log_dir.exists()}")
    
    if log_manager.log_dir.exists():
        print(f"日志目录内容: {list(log_manager.log_dir.iterdir())}")
    
    # 创建测试会话ID
    session_id = f"debug_test_{int(time.time())}"
    
    # 尝试记录不同类型的日志
    print(f"\n记录测试日志到会话: {session_id}")
    
    # 记录系统提示词
    log_manager.log_system_prompt(session_id, "这是一个测试系统提示词")
    
    # 记录API请求
    log_manager.log_api_request(
        session_id, 
        [{"role": "user", "content": "测试消息"}], 
        "test-model", 
        100, 
        0.7
    )
    
    # 记录API响应
    log_manager.log_api_response(session_id, "这是测试响应")
    
    # 记录错误
    log_manager.log_error(session_id, "test_error", "这是一个测试错误")
    
    print("日志记录完成")
    
    # 检查日志文件是否创建
    log_file_path = log_manager._get_log_file_path(session_id)
    print(f"日志文件路径: {log_file_path}")
    print(f"日志文件是否存在: {log_file_path.exists()}")
    
    if log_file_path.exists():
        print("日志文件内容:")
        with open(log_file_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(content)
    
    # 使用get_session_logs方法获取日志
    print("\n使用get_session_logs方法获取日志:")
    logs = log_manager.get_session_logs(session_id)
    print(f"获取到 {len(logs)} 条日志")
    
    for i, log in enumerate(logs):
        print(f"日志 {i+1}: {log}")

if __name__ == "__main__":
    debug_logging()