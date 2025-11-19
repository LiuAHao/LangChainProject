#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试会话管理问题的脚本
"""

import sys
import os
import asyncio
import json

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_manager import DataManager
from chat_api import ChatAPI

def debug_database_connection():
    """调试数据库连接和数据"""
    print("=== 调试数据库连接和数据 ===")

    try:
        data_manager = DataManager()
        db = data_manager.get_connection()

        # 检查表是否存在
        print("\n1. 检查数据库表...")
        try:
            tables_result = db.run("SHOW TABLES")
            print(f"数据库表: {tables_result}")
        except Exception as e:
            print(f"检查表时出错: {e}")
            return False

        # 检查会话数量
        print("\n2. 检查会话数量...")
        try:
            count_result = db.run("SELECT COUNT(*) as count FROM chat_sessions")
            print(f"会话数量查询结果: {count_result}")

            # 解析结果
            result_str = str(count_result)
            print(f"原始结果字符串: {result_str}")

            if result_str.startswith("[(") and result_str.endswith(",)]"):
                count_str = result_str[2:-3]
                session_count = int(count_str)
                print(f"解析后的会话数量: {session_count}")
            else:
                print("无法解析会话数量")
                return False

        except Exception as e:
            print(f"查询会话数量时出错: {e}")
            return False

        # 检查具体会话数据
        print("\n3. 检查具体会话数据...")
        try:
            sessions_result = db.run("SELECT session_id, title, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC")
            print(f"会话数据: {sessions_result}")

            # 使用data_manager的方法获取会话
            sessions = data_manager.get_all_sessions()
            print(f"通过data_manager获取的会话: {json.dumps(sessions, indent=2, ensure_ascii=False, default=str)}")

            return len(sessions) > 0

        except Exception as e:
            print(f"查询会话数据时出错: {e}")
            return False

    except Exception as e:
        print(f"数据库连接出错: {e}")
        return False

def debug_api_endpoints():
    """调试API端点"""
    print("\n=== 调试API端点 ===")

    import requests
    import time

    base_url = "http://localhost:8000"

    # 测试会话API
    endpoints = [
        "/api/health",
        "/api/sessions",
        "/api/personas"
    ]

    for endpoint in endpoints:
        try:
            print(f"\n测试 {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}..." if len(response.text) > 200 else f"响应: {response.text}")
        except Exception as e:
            print(f"请求 {endpoint} 失败: {e}")

def debug_javascript_logic():
    """调试JavaScript逻辑的问题"""
    print("\n=== JavaScript逻辑分析 ===")

    print("当前问题分析:")
    print("1. init() 方法中的异步加载时序问题:")
    print("   - loadSessions() 可能还没完成就执行了 initChat()")
    print("   - this.sessions 数组可能为空或不完整")

    print("\n2. initChat() 方法的逻辑:")
    print("   - 第332行: if (this.sessions && this.sessions.length > 0)")
    print("   - 如果sessions为空，就会创建新会话")

    print("\n3. 可能的解决方案:")
    print("   - 在loadSessions()完成后使用await确保数据加载")
    print("   - 添加更多调试日志来跟踪数据流")
    print("   - 改进异步操作的协调")

def create_test_session():
    """创建一个测试会话来验证功能"""
    print("\n=== 创建测试会话 ===")

    try:
        data_manager = DataManager()

        # 创建测试会话
        import uuid
        session_id = str(uuid.uuid4())
        title = "测试会话_" + str(int(time.time()))

        print(f"创建测试会话: {session_id}")
        success = data_manager.save_session(session_id, title, 1)  # 使用默认人设ID=1

        if success:
            print("测试会话创建成功")

            # 验证会话是否真的保存了
            sessions = data_manager.get_all_sessions()
            print(f"创建后的会话数量: {len(sessions)}")

            # 查找刚创建的会话
            test_session = next((s for s in sessions if s["session_id"] == session_id), None)
            if test_session:
                print(f"找到测试会话: {test_session}")
                return True
            else:
                print("未找到刚创建的测试会话")
                return False
        else:
            print("测试会话创建失败")
            return False

    except Exception as e:
        print(f"创建测试会话时出错: {e}")
        return False

if __name__ == "__main__":
    print("开始调试会话管理问题...")

    # 1. 调试数据库连接和数据
    has_sessions = debug_database_connection()

    # 2. 如果有会话数据，尝试启动Web服务进行API测试
    if has_sessions:
        print("\n数据库中存在会话数据，问题可能在前端逻辑")
    else:
        print("\n数据库中没有会话数据，尝试创建测试会话...")
        create_test_session()

    # 3. 分析JavaScript逻辑
    debug_javascript_logic()

    # 4. 提供修复建议
    print("\n=== 修复建议 ===")
    print("1. 确保数据库中有会话数据")
    print("2. 修复JavaScript中的异步加载问题")
    print("3. 添加更详细的调试日志")
    print("4. 改进错误处理机制")