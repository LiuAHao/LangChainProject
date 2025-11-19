import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat_robot.chat_api import ChatAPI
from chat_robot.config_manager import config_manager
from chat_robot.log_manager import log_manager

def test_logging():
    """测试日志功能"""
    print("开始测试日志功能...")
    
    # 测试配置变更日志
    config_manager.set("TEST_CONFIG", "test_value")
    
    # 测试数据库操作日志
    log_manager.log_database_operation("test_session", "test_operation", "test_table", {
        "test_field": "test_value"
    })
    
    # 测试系统提示词日志
    log_manager.log_system_prompt("test_session", "This is a test system prompt")
    
    # 测试API请求日志
    log_manager.log_api_request("test_session", [
        {"role": "user", "content": "Hello, this is a test message"}
    ], "test_model", 100, 0.7)
    
    # 测试API响应日志
    log_manager.log_api_response("test_session", "This is a test response", 10, 20)
    
    # 测试错误日志
    log_manager.log_error("test_session", "test_error", "This is a test error message")
    
    # 测试ChatAPI初始化日志
    try:
        chat_api = ChatAPI()
        print("ChatAPI初始化成功，检查日志记录...")
    except Exception as e:
        print(f"ChatAPI初始化失败: {e}")
    
    print("日志功能测试完成。请检查chat_robot/log目录下的日志文件。")

if __name__ == "__main__":
    test_logging()