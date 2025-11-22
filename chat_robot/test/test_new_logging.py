#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的日志系统
"""

import time
from log_manager import log_manager

def test_logging():
    """测试新的日志功能"""
    print("开始测试新的日志系统...")

    session_id = "test_session_123"
    module = "test"

    # 测试各种日志类型
    print("1. 测试API请求日志...")
    log_manager.log_api_request(
        session_id=session_id,
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        model="test-model",
        max_tokens=1000,
        temperature=0.7,
        module=module
    )

    time.sleep(0.1)

    print("2. 测试API响应日志...")
    log_manager.log_api_response(
        session_id=session_id,
        response="I'm doing well, thank you for asking!",
        prompt_tokens=15,
        completion_tokens=20,
        module=module
    )

    time.sleep(0.1)

    print("3. 测试系统提示词日志...")
    log_manager.log_system_prompt(
        session_id=session_id,
        system_prompt="You are a helpful AI assistant.",
        module=module
    )

    time.sleep(0.1)

    print("4. 测试数据库操作日志...")
    log_manager.log_database_operation(
        session_id=session_id,
        operation="save",
        table="messages",
        details={"message_id": 123, "content_length": 50},
        module=module
    )

    time.sleep(0.1)

    print("5. 测试错误日志...")
    log_manager.log_error(
        session_id=session_id,
        error_type="TestError",
        error_message="这是一个测试错误消息",
        module=module
    )

    time.sleep(0.1)

    print("6. 测试配置变更日志...")
    log_manager.log_config_change(
        key="test_setting",
        old_value="old",
        new_value="new",
        module="config"
    )

    print("\n日志测试完成!")

    # 测试日志读取功能
    print("\n7. 测试日志读取功能...")
    logs = log_manager.get_session_logs(session_id, module=module, days=1)
    print(f"读取到 {len(logs)} 条日志记录")

    # 测试日志摘要
    print("\n8. 测试日志摘要...")
    summary = log_manager.get_log_summary(session_id, module=module, days=1)
    print("日志摘要:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # 测试日志文件列表
    print("\n9. 测试日志文件列表...")
    log_files = log_manager.list_log_files(module=module)
    print(f"找到 {len(log_files)} 个日志文件:")
    for log_file in log_files:
        print(f"  - {log_file['filename']} ({log_file['size']} bytes)")

    print("\n所有测试完成!")

if __name__ == "__main__":
    test_logging()