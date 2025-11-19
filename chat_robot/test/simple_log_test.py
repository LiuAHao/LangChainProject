import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat_robot.log_manager import log_manager

def test_simple_logging():
    """简单测试日志功能"""
    print("开始简单日志测试...")
    
    # 测试API请求日志
    log_manager.log_api_request("simple_test", [
        {"role": "user", "content": "Hello, this is a simple test message"}
    ], "test_model", 100, 0.7, "api")
    
    # 测试数据库操作日志
    log_manager.log_database_operation("simple_test", "insert", "test_table", {
        "test_field": "test_value"
    }, "database")
    
    # 测试系统提示词日志
    log_manager.log_system_prompt("simple_test", "This is a simple test system prompt", "prompt")
    
    # 测试配置变更日志
    log_manager.log_config_change("simple_test_config", "old_value", "new_value", "config")
    
    # 测试错误日志
    log_manager.log_error("simple_test", "simple_test_error", "This is a simple test error message", "error")
    
    print("简单日志测试完成。请检查chat_robot/log目录下的日志文件。")

if __name__ == "__main__":
    test_simple_logging()