#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试ChatAPI的功能
"""

from chat_robot.chat_api import ChatAPI


def test_chat_api():
    """测试聊天API的基本功能"""
    print("开始测试ChatAPI...")
    
    # 创建聊天API实例
    chat_api = ChatAPI()
    
    # 测试会话ID
    session_id = "test_session_001"
    
    # 第一轮对话
    print("=== 第一轮对话 ===")
    user_input = "你好，介绍一下你自己"
    response = chat_api.chat_with_history(session_id, user_input)
    print(f"用户: {user_input}")
    print(f"助手: {response}\n")
    
    # 第二轮对话
    print("=== 第二轮对话 ===")
    user_input = "你能帮我写一个Python函数来计算斐波那契数列吗？"
    response = chat_api.chat_with_history(session_id, user_input)
    print(f"用户: {user_input}")
    print(f"助手: {response}\n")
    
    print("测试完成!")


if __name__ == "__main__":
    test_chat_api()