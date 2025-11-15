#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试聊天功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from chat_robot.chat_api import ChatAPI
import uuid


def test_chat_functionality():
    """测试聊天功能"""
    print("开始测试聊天功能...")
    
    # 创建聊天API实例
    chat_api = ChatAPI()
    
    # 生成测试会话ID
    session_id = str(uuid.uuid4())
    print(f"测试会话ID: {session_id}")
    
    try:
        # 第一轮对话
        print("\n=== 第一轮对话 ===")
        user_input = "你好，介绍一下你自己"
        response = chat_api.chat_with_history(session_id, user_input)
        print(f"用户: {user_input}")
        print(f"助手: {response}")
        
        # 第二轮对话
        print("\n=== 第二轮对话 ===")
        user_input = "你能告诉我一些关于人工智能的知识吗？"
        response = chat_api.chat_with_history(session_id, user_input)
        print(f"用户: {user_input}")
        print(f"助手: {response}")
        
        # 测试历史记录摘要功能
        print("\n=== 测试历史记录摘要功能 ===")
        # 添加更多消息以触发摘要功能
        for i in range(5):
            chat_api.data_manager.save_message(session_id, "user", f"测试消息 {i+1}")
            chat_api.data_manager.save_message(session_id, "assistant", f"回复消息 {i+1}")
        
        # 检查消息总数
        message_count = chat_api.data_manager.get_message_count(session_id)
        print(f"当前会话消息总数: {message_count}")
        
        # 测试摘要功能
        summary = chat_api.summarize_history(session_id)
        print(f"历史摘要: {summary}")
        
        print("\n聊天功能测试完成!")
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_chat_functionality()
    if success:
        print("\n聊天功能测试成功!")
    else:
        print("\n聊天功能测试失败!")