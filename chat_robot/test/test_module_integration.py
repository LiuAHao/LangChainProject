#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试三个模块之间的集成
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from chat_robot.chat_api import ChatAPI


def test_module_integration():
    """测试模块集成"""
    print("开始测试模块集成...")
    
    # 创建聊天API实例（这会同时初始化DataManager和PromptManager）
    chat_api = ChatAPI()
    
    print("1. 模块初始化成功")
    print(f"   - DataManager: {chat_api.data_manager}")
    print(f"   - PromptManager: {chat_api.prompt_manager}")
    print(f"   - OpenAI Client: {chat_api.client}")
    
    # 测试数据库连接
    try:
        # 测试创建表
        chat_api.data_manager.create_tables()
        print("2. 数据库连接和表创建成功")
        
        # 测试保存会话
        session_id = "test_integration_session"
        result = chat_api.data_manager.save_session(session_id)
        print(f"3. 会话保存测试: {'成功' if result else '失败'}")
        
        # 测试保存消息
        save_result = chat_api.data_manager.save_message(session_id, "user", "测试消息")
        print(f"4. 消息保存测试: {'成功' if save_result else '失败'}")
        
        # 测试获取消息
        messages = chat_api.data_manager.get_recent_messages(session_id)
        print(f"5. 消息获取测试: 获取到 {len(messages)} 条消息")
        
        # 测试PromptManager
        prompt_template = chat_api.prompt_manager.get_prompt_template()
        print(f"6. PromptManager测试: 成功获取提示词模板")
        print(f"   - 模板类型: {type(prompt_template)}")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        return False
    
    print("所有模块集成测试完成!")
    return True


if __name__ == "__main__":
    success = test_module_integration()
    if success:
        print("模块集成测试成功!")
    else:
        print("模块集成测试失败!")