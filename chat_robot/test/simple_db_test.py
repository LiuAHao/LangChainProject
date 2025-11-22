#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的数据库测试脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data_manager import DataManager

def test_database_migration():
    """测试数据库迁移和新架构"""
    print("开始测试数据库架构v2.0.0...")

    try:
        # 初始化DataManager
        data_manager = DataManager()
        print(f"DataManager初始化成功，当前架构版本: {data_manager.current_schema_version}")

        # 创建新的表结构
        print("\n创建新的数据库表结构...")
        data_manager.create_tables()
        print("数据库表创建成功")

        # 测试AI人设功能（应该已经有默认人设）
        print("\n测试AI人设功能...")
        personas = data_manager.get_all_personas()
        print(f"获取到 {len(personas)} 个AI人设")
        for persona in personas[:2]:  # 只显示前两个
            print(f"  - {persona['name']}: {persona['description'][:30]}...")

        # 测试新会话功能
        print("\n测试新会话功能...")
        test_session_id = "test_session_v2_001"
        session_result = data_manager.save_session_v2(
            session_id=test_session_id,
            user_id=None,
            title="测试会话v2",
            persona_id=1 if personas else None,
            model_name="test-model"
        )
        print(f"会话创建结果: {session_result}")

        # 测试新消息功能
        print("\n测试新消息功能...")
        message1_id = data_manager.save_message_v2(
            session_id=test_session_id,
            role="user",
            content="你好，这是测试消息",
            model_name="test-model",
            tokens_used=10
        )
        print(f"消息1保存结果: {message1_id}")

        message2_id = data_manager.save_message_v2(
            session_id=test_session_id,
            role="assistant",
            content="您好！我是AI助手，很高兴为您服务。",
            model_name="test-model",
            tokens_used=15
        )
        print(f"消息2保存结果: {message2_id}")

        # 测试消息检索
        print("\n测试消息检索...")
        messages = data_manager.get_recent_messages_v2(test_session_id, limit=10)
        print(f"获取到 {len(messages)} 条消息")

        # 测试摘要功能
        print("\n测试摘要功能...")
        summary_result = data_manager.save_summary_v2(
            session_id=test_session_id,
            summary_text="这是一段测试摘要，总结了用户与AI的基本对话。",
            message_count=2,
            summary_type="auto",
            model_name="test-model",
            tokens_saved=25
        )
        print(f"摘要保存结果: {summary_result}")

        # 测试统计信息
        print("\n测试统计信息...")
        message_count = data_manager.get_message_count(test_session_id)
        print(f"会话消息总数: {message_count}")

        print("\n所有测试完成！新的数据库架构工作正常。")

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def print_database_schema_info():
    """打印数据库架构信息"""
    print("\n数据库架构v2.0.0主要改进:")
    print("""
1. 外键关联优化 - 使用整数主键替代字符串外键
2. 数据表增强 - 用户管理、增强的人设、会话状态管理
3. 性能优化 - 全面的索引覆盖和复合索引
4. 数据完整性 - 外键约束、枚举类型、审计字段
5. 向后兼容 - 保留原有API接口，支持渐进式迁移
    """)

if __name__ == "__main__":
    print("=" * 60)
    print("LangChain聊天机器人 - 数据库架构迁移测试")
    print("=" * 60)

    # 打印架构信息
    print_database_schema_info()

    # 测试新架构
    migration_success = test_database_migration()

    if migration_success:
        print("\n测试成功！数据库重构完成。")
    else:
        print("\n测试失败，请检查配置和连接。")

    print("=" * 60)