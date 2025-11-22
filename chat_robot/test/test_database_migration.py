#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库架构迁移和测试脚本

测试新的v2.0.0数据库架构设计
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 直接导入模块
from data_manager import DataManager
from log_manager import log_manager

def test_database_migration():
    """测试数据库迁移和新架构"""
    print("🚀 开始测试数据库架构v2.0.0...")

    try:
        # 初始化DataManager
        data_manager = DataManager()
        print(f"✅ DataManager初始化成功，当前架构版本: {data_manager.current_schema_version}")

        # 创建新的表结构
        print("\n📋 创建新的数据库表结构...")
        data_manager.create_tables()
        print("✅ 数据库表创建成功")

        # 测试用户功能
        print("\n👤 测试用户功能...")
        user_result = data_manager.save_user(
            username="test_user",
            display_name="测试用户",
            email="test@example.com"
        )
        print(f"✅ 用户创建结果: {user_result}")

        # 测试AI人设功能（应该已经有默认人设）
        print("\n🤖 测试AI人设功能...")
        personas = data_manager.get_all_personas()
        print(f"✅ 获取到 {len(personas)} 个AI人设")
        for persona in personas:
            print(f"  - {persona['name']}: {persona['description'][:50]}...")

        # 测试新会话功能
        print("\n💬 测试新会话功能...")
        test_session_id = "test_session_v2_001"
        session_result = data_manager.save_session_v2(
            session_id=test_session_id,
            user_id=1,
            title="测试会话v2",
            persona_id=1 if personas else None,
            model_name="test-model",
            settings={"theme": "dark", "language": "zh-CN"}
        )
        print(f"✅ 会话创建结果: {session_result}")

        # 测试新消息功能
        print("\n📝 测试新消息功能...")
        message1_id = data_manager.save_message_v2(
            session_id=test_session_id,
            role="user",
            content="你好，这是测试消息",
            model_name="test-model",
            tokens_used=10,
            metadata={"source": "test"}
        )
        print(f"✅ 消息1保存结果: {message1_id}")

        message2_id = data_manager.save_message_v2(
            session_id=test_session_id,
            role="assistant",
            content="您好！我是AI助手，很高兴为您服务。",
            model_name="test-model",
            tokens_used=15,
            parent_message_id=message1_id
        )
        print(f"✅ 消息2保存结果: {message2_id}")

        # 测试消息检索
        print("\n🔍 测试消息检索...")
        messages = data_manager.get_recent_messages_v2(test_session_id, limit=10)
        print(f"✅ 获取到 {len(messages)} 条消息")
        for msg in messages:
            print(f"  - {msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}...")

        # 测试摘要功能
        print("\n📄 测试摘要功能...")
        summary_result = data_manager.save_summary_v2(
            session_id=test_session_id,
            summary_text="这是一段测试摘要，总结了用户与AI的基本对话。",
            message_count=2,
            summary_type="auto",
            model_name="test-model",
            tokens_saved=25
        )
        print(f"✅ 摘要保存结果: {summary_result}")

        # 测试会话列表
        print("\n📋 测试会话列表...")
        sessions = data_manager.get_all_sessions_v2(status='active', limit=10)
        print(f"✅ 获取到 {len(sessions)} 个会话")
        for session in sessions:
            print(f"  - {session.get('session_id', 'unknown')}: {session.get('title', 'Untitled')}")

        # 测试统计信息
        print("\n📊 测试统计信息...")
        message_count = data_manager.get_message_count(test_session_id)
        print(f"✅ 会话消息总数: {message_count}")

        print("\n🎉 所有测试完成！新的数据库架构工作正常。")

        # 记录测试成功
        log_manager.log_database_operation("system", "test", "migration_success",
                                          {"version": data_manager.current_schema_version}, "database")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

        # 记录测试失败
        log_manager.log_database_operation("system", "error", "migration_test",
                                          {"error": str(e)}, "database")
        return False

    return True

def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n🔄 测试向后兼容性...")

    try:
        data_manager = DataManager()

        # 测试旧的方法是否仍然工作
        test_session_id = "compat_test_session"

        # 使用旧方法保存会话
        old_session_result = data_manager.save_session(test_session_id, "兼容性测试会话")
        print(f"✅ 旧方法保存会话: {old_session_result}")

        # 使用旧方法保存消息
        old_message_result = data_manager.save_message(test_session_id, "user", "兼容性测试消息")
        print(f"✅ 旧方法保存消息: {old_message_result}")

        # 使用旧方法获取消息
        old_messages = data_manager.get_recent_messages(test_session_id, limit=5)
        print(f"✅ 旧方法获取消息: {len(old_messages)} 条")

        print("✅ 向后兼容性测试通过")

    except Exception as e:
        print(f"❌ 向后兼容性测试失败: {e}")
        return False

    return True

def print_database_schema():
    """打印数据库架构信息"""
    print("\n📐 数据库架构v2.0.0详情:")
    print("""
主要改进:
1. 🔗 外键关联优化
   - 使用整数主键替代字符串外键
   - 完善的级联删除和约束
   - 用户与会话关联

2. 📊 数据表增强
   - users: 用户管理
   - ai_personas: 增强的AI人设（支持激活状态、创建者）
   - chat_sessions: 重构的会话管理（状态、统计、设置）
   - chat_messages: 增强的消息（父子关系、元数据、软删除）
   - chat_summaries: 增强的摘要（类型、范围、统计）

3. 🚀 性能优化
   - 全面的索引覆盖
   - 复合索引优化
   - 查询性能提升

4. 🛡️ 数据完整性
   - 外键约束
   - 枚举类型限制
   - 审计字段
   - 软删除机制

5. 🔄 向后兼容
   - 保留原有API接口
   - 渐进式迁移支持
   - 新旧功能并存
    """)

if __name__ == "__main__":
    print("=" * 60)
    print("🗄️ LangChain聊天机器人 - 数据库架构迁移测试")
    print("=" * 60)

    # 打印架构信息
    print_database_schema()

    # 测试新架构
    migration_success = test_database_migration()

    if migration_success:
        # 测试向后兼容性
        compatibility_success = test_backward_compatibility()

        if compatibility_success:
            print("\n🎊 所有测试成功！数据库重构完成。")
        else:
            print("\n⚠️ 新架构测试成功，但向后兼容性测试失败。")
    else:
        print("\n💥 新架构测试失败，请检查配置和连接。")

    print("\n" + "=" * 60)