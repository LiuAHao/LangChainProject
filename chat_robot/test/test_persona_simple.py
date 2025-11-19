#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版人设功能测试脚本（不依赖LangChain）
"""

import sys
import os
import json

def test_mysql_connection():
    """测试MySQL连接"""
    try:
        import pymysql
        print("✅ PyMySQL 已安装")

        # 测试数据库连接
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='chat_robot',
            charset='utf8mb4'
        )

        with connection.cursor() as cursor:
            # 测试查询
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            if result and result[0] == 1:
                print("✅ 数据库连接成功")
                connection.close()
                return True
            else:
                print("❌ 数据库查询失败")
                return False

    except ImportError:
        print("❌ PyMySQL 未安装")
        return False
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_database_tables():
    """测试数据库表结构"""
    try:
        import pymysql

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='chat_robot',
            charset='utf8mb4'
        )

        with connection.cursor() as cursor:
            # 检查ai_personas表
            cursor.execute("SHOW TABLES LIKE 'ai_personas'")
            if cursor.fetchone():
                print("✅ ai_personas 表存在")

                # 检查表结构
                cursor.execute("DESCRIBE ai_personas")
                columns = cursor.fetchall()
                print(f"   ai_personas 表有 {len(columns)} 个字段")

                # 检查数据
                cursor.execute("SELECT COUNT(*) FROM ai_personas")
                count = cursor.fetchone()[0]
                print(f"   ai_personas 表有 {count} 条数据")

                if count == 0:
                    # 插入测试数据
                    print("   插入默认人设数据...")
                    cursor.execute("""
                        INSERT INTO ai_personas (name, description, system_prompt, is_default) VALUES
                        ('通用助手', '一个通用的AI助手', '你是一个有用的AI助手。', 1),
                        ('编程助手', '专业的编程助手', '你是一个专业的编程助手。', 0)
                    """)
                    connection.commit()
                    print("   ✅ 默认人设数据插入成功")
            else:
                print("❌ ai_personas 表不存在")

            # 检查chat_sessions表
            cursor.execute("SHOW TABLES LIKE 'chat_sessions'")
            if cursor.fetchone():
                print("✅ chat_sessions 表存在")
            else:
                print("❌ chat_sessions 表不存在")

        connection.close()
        return True

    except Exception as e:
        print(f"❌ 数据库表测试失败: {e}")
        return False

def test_persona_data():
    """测试人设数据操作"""
    try:
        import pymysql

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='chat_robot',
            charset='utf8mb4'
        )

        with connection.cursor() as cursor:
            # 获取所有人设
            cursor.execute("""
                SELECT id, name, description, system_prompt, is_default
                FROM ai_personas
                ORDER BY is_default DESC, name ASC
            """)
            personas = cursor.fetchall()

            print(f"📋 获取到 {len(personas)} 个人设:")
            for persona in personas:
                id, name, description, system_prompt, is_default = persona
                print(f"   - ID: {id}, 名称: {name}, 默认: {is_default}")
                print(f"     描述: {description[:50]}...")
                print(f"     提示: {system_prompt[:50]}...")
                print()

            # 测试根据ID获取人设
            if personas:
                persona_id = personas[0][0]
                cursor.execute("""
                    SELECT id, name, description, system_prompt, is_default
                    FROM ai_personas
                    WHERE id = %s
                """, (persona_id,))
                persona_detail = cursor.fetchone()

                if persona_detail:
                    print(f"🔍 根据ID {persona_id} 查询人设成功:")
                    print(f"   名称: {persona_detail[1]}")
                    print(f"   系统提示: {persona_detail[3]}")

        connection.close()
        return True

    except Exception as e:
        print(f"❌ 人设数据测试失败: {e}")
        return False

def test_session_data():
    """测试会话数据操作"""
    try:
        import pymysql
        import uuid

        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='chat_robot',
            charset='utf8mb4'
        )

        with connection.cursor() as cursor:
            # 创建测试会话
            session_id = str(uuid.uuid4())
            cursor.execute("""
                SELECT id FROM ai_personas WHERE is_default = 1 LIMIT 1
            """)
            result = cursor.fetchone()
            persona_id = result[0] if result else None

            cursor.execute("""
                INSERT INTO chat_sessions (session_id, title, persona_id)
                VALUES (%s, %s, %s)
            """, (session_id, "测试会话", persona_id))
            connection.commit()
            print(f"✅ 创建测试会话成功: {session_id[:8]}...")

            # 获取会话列表
            cursor.execute("""
                SELECT s.session_id, s.title, s.persona_id, p.name as persona_name
                FROM chat_sessions s
                LEFT JOIN ai_personas p ON s.persona_id = p.id
                ORDER BY s.updated_at DESC
                LIMIT 5
            """)
            sessions = cursor.fetchall()

            print(f"📝 最近 {len(sessions)} 个会话:")
            for session in sessions:
                sid, title, pid, persona_name = session
                print(f"   - ID: {sid[:8]}..., 标题: {title}, 人设: {persona_name or '无'}")

        connection.close()
        return True

    except Exception as e:
        print(f"❌ 会话数据测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🤖 Qwen AI 聊天机器人 - 简化版人设功能测试")
    print("=" * 60)

    # 测试数据库连接
    print("1. 测试数据库连接...")
    db_ok = test_mysql_connection()

    if not db_ok:
        print("\n❌ 数据库连接失败，请检查:")
        print("   - MySQL 服务是否启动")
        print("   - 数据库配置是否正确")
        print("   - PyMySQL 是否安装: pip install pymysql")
        return

    # 测试数据库表
    print("\n2. 测试数据库表...")
    tables_ok = test_database_tables()

    # 测试人设数据
    print("\n3. 测试人设数据操作...")
    persona_ok = test_persona_data()

    # 测试会话数据
    print("\n4. 测试会话数据操作...")
    session_ok = test_session_data()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"   数据库连接: {'✅ 通过' if db_ok else '❌ 失败'}")
    print(f"   数据库表: {'✅ 通过' if tables_ok else '❌ 失败'}")
    print(f"   人设数据: {'✅ 通过' if persona_ok else '❌ 失败'}")
    print(f"   会话数据: {'✅ 通过' if session_ok else '❌ 失败'}")

    if db_ok and tables_ok and persona_ok and session_ok:
        print("\n🎉 所有测试通过！人设功能基础组件正常工作。")
        print("\n📝 接下来需要:")
        print("   1. 安装Web依赖: pip install fastapi uvicorn jinja2")
        print("   2. 安装AI依赖: pip install langchain langchain_community")
        print("   3. 启动Web服务: python3 web_interface/app.py")
        print("   4. 在浏览器中测试完整功能")
    else:
        print("\n⚠️  部分测试失败，请检查数据库和配置。")

if __name__ == "__main__":
    main()