#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单测试摘要功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from chat_robot.chat_api import ChatAPI
from chat_robot.data_manager import DataManager
import uuid


def test_simple_summary():
    """简单测试摘要功能"""
    print("开始简单测试摘要功能...")
    
    # 创建数据管理器实例
    data_manager = DataManager()
    
    # 生成测试会话ID
    session_id = str(uuid.uuid4())
    print(f"测试会话ID: {session_id}")
    
    try:
        # 先保存会话
        data_manager.save_session(session_id)
        print("会话保存成功")
        
        # 添加多条消息以触发摘要功能
        print("\n=== 添加测试消息 ===")
        test_messages = [
            ("user", "你好，我想了解人工智能的发展历史。"),
            ("assistant", "人工智能的发展历史可以追溯到20世纪50年代。"),
            ("user", "能详细介绍一下早期的重要里程碑吗？"),
            ("assistant", "当然可以。1956年达特茅斯会议被认为是AI的诞生标志。"),
            ("user", "那后来有哪些重要发展？"),
            ("assistant", "后来的重要发展包括专家系统的兴起、机器学习的发展等。"),
            ("user", "深度学习是什么时候兴起的？"),
            ("assistant", "深度学习在21世纪初开始兴起，特别是2006年以后。"),
            ("user", "现在AI主要应用在哪些领域？"),
            ("assistant", "现在AI广泛应用于图像识别、自然语言处理、自动驾驶等领域。"),
            ("user", "未来AI的发展趋势是什么？"),
            ("assistant", "未来AI可能会在通用人工智能、可解释性等方面有重要发展。")
        ]
        
        for role, content in test_messages:
            result = data_manager.save_message(session_id, role, content)
            print(f"保存消息 [{role}]: {content[:30]}... {'成功' if result else '失败'}")
        
        # 检查消息总数
        message_count = data_manager.get_message_count(session_id)
        print(f"\n当前会话消息总数: {message_count}")
        
        # 测试摘要功能
        print("\n=== 测试摘要功能 ===")
        # 创建聊天API实例
        chat_api = ChatAPI()
        summary = chat_api.summarize_history(session_id)
        print(f"生成的摘要: {summary}")
        
        print("\n简单摘要功能测试完成!")
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_simple_summary()
    if success:
        print("\n简单摘要功能测试成功!")
    else:
        print("\n简单摘要功能测试失败!")