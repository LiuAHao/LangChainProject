#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试数据库查询
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from chat_robot.data_manager import DataManager
import uuid


def debug_database():
    """调试数据库查询"""
    print("开始调试数据库查询...")
    
    # 创建数据管理器实例
    data_manager = DataManager()
    
    # 生成测试会话ID
    session_id = str(uuid.uuid4())
    print(f"测试会话ID: {session_id}")
    
    try:
        # 先保存会话
        data_manager.save_session(session_id)
        print("会话保存成功")
        
        # 添加几条测试消息
        print("\n=== 添加测试消息 ===")
        test_messages = [
            ("user", "测试消息1"),
            ("assistant", "回复消息1"),
            ("user", "测试消息2"),
            ("assistant", "回复消息2")
        ]
        
        for role, content in test_messages:
            result = data_manager.save_message(session_id, role, content)
            print(f"保存消息 [{role}]: {content} {'成功' if result else '失败'}")
        
        # 调试查询
        print("\n=== 调试查询 ===")
        
        # 直接执行计数查询
        count_query = "SELECT COUNT(*) as count FROM chat_messages WHERE session_id = '{}'".format(session_id)
        print(f"计数查询: {count_query}")
        
        try:
            db = data_manager.get_connection()
            result = db.run(count_query)
            print(f"计数查询结果: {repr(result)}")
        except Exception as e:
            print(f"计数查询出错: {e}")
        
        # 直接执行选择查询
        select_query = "SELECT role, content FROM chat_messages WHERE session_id = '{}'".format(session_id)
        print(f"\n选择查询: {select_query}")
        
        try:
            db = data_manager.get_connection()
            result = db.run(select_query)
            print(f"选择查询结果: {repr(result)}")
        except Exception as e:
            print(f"选择查询出错: {e}")
        
        # 使用get_message_count方法
        message_count = data_manager.get_message_count(session_id)
        print(f"\nget_message_count方法结果: {message_count}")
        
        # 使用get_recent_messages方法
        recent_messages = data_manager.get_recent_messages(session_id)
        print(f"get_recent_messages方法结果: {recent_messages}")
        
        print("\n调试完成!")
        return True
        
    except Exception as e:
        print(f"调试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    debug_database()