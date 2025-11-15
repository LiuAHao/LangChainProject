#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试摘要功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from chat_robot.chat_api import ChatAPI
import uuid


def test_summary_function():
    """测试摘要功能"""
    print("开始测试摘要功能...")
    
    # 创建聊天API实例
    chat_api = ChatAPI()
    
    # 生成测试会话ID
    session_id = str(uuid.uuid4())
    print(f"测试会话ID: {session_id}")
    
    try:
        # 确保会话存在
        chat_api.data_manager.save_session(session_id)
        
        # 添加多条消息以触发摘要功能
        print("\n=== 添加测试消息 ===")
        for i in range(10):
            # 添加用户消息
            user_msg = f"这是第{i+1}条测试消息，内容是关于人工智能的发展趋势。"
            chat_api.data_manager.save_message(session_id, "user", user_msg)
            print(f"保存用户消息: {user_msg}")
            
            # 添加助手回复
            assistant_msg = f"这是对第{i+1}条消息的回复，讨论了人工智能在{i+1}个不同领域的应用。"
            chat_api.data_manager.save_message(session_id, "assistant", assistant_msg)
            print(f"保存助手消息: {assistant_msg}")
        
        # 检查消息总数
        message_count = chat_api.data_manager.get_message_count(session_id)
        print(f"\n当前会话消息总数: {message_count}")
        
        # 获取历史消息
        history_messages = chat_api.data_manager.get_history_messages(session_id, limit=message_count-4)
        print(f"用于摘要的历史消息数量: {len(history_messages)}")
        
        if history_messages:
            print("历史消息内容:")
            for i, msg in enumerate(history_messages[:3]):  # 只显示前3条
                print(f"  {i+1}. {msg['role']}: {msg['content']}")
            if len(history_messages) > 3:
                print(f"  ... 还有 {len(history_messages) - 3} 条消息")
        
        # 测试摘要功能
        print("\n=== 测试摘要功能 ===")
        summary = chat_api.summarize_history(session_id)
        print(f"生成的摘要: {summary}")
        
        print("\n摘要功能测试完成!")
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_summary_function()
    if success:
        print("\n摘要功能测试成功!")
    else:
        print("\n摘要功能测试失败!")