#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试人设功能脚本
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

def test_persona_functions():
    """测试人设相关的核心功能"""
    print("=" * 50)
    print("开始测试人设功能...")

    try:
        # 导入数据管理器
        from data_manager import DataManager

        # 初始化数据管理器
        print("1. 初始化数据管理器...")
        data_manager = DataManager()

        # 创建数据表
        print("2. 创建数据表...")
        data_manager.create_tables()

        # 测试获取所有人设
        print("3. 测试获取所有人设...")
        personas = data_manager.get_all_personas()
        print(f"   获取到 {len(personas)} 个人设:")
        for persona in personas:
            print(f"   - ID: {persona['id']}, 名称: {persona['name']}, 默认: {persona['is_default']}")

        # 测试根据ID获取人设
        if personas:
            print("4. 测试根据ID获取人设...")
            first_persona = personas[0]
            persona_detail = data_manager.get_persona_by_id(first_persona['id'])
            print(f"   人设详情: {persona_detail['name']}")
            print(f"   系统提示: {persona_detail['system_prompt'][:100]}...")

        # 测试创建会话
        print("5. 测试创建会话...")
        import uuid
        session_id = str(uuid.uuid4())
        persona_id = personas[0]['id'] if personas else None
        success = data_manager.save_session(session_id, "测试会话", persona_id)
        print(f"   会话创建: {'成功' if success else '失败'}")

        # 测试获取会话列表
        print("6. 测试获取会话列表...")
        sessions = data_manager.get_all_sessions()
        print(f"   获取到 {len(sessions)} 个会话:")
        for session in sessions[:3]:  # 只显示前3个
            print(f"   - ID: {session['session_id'][:8]}..., 标题: {session['title']}, 人设: {session.get('persona_name', '无')}")

        # 测试更新会话人设
        if personas and len(personas) > 1:
            print("7. 测试更新会话人设...")
            new_persona_id = personas[1]['id']
            success = data_manager.update_session(session_id, persona_id=new_persona_id)
            print(f"   人设更新: {'成功' if success else '失败'}")

        print("\n✅ 所有人设功能测试通过!")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_api_calls():
    """模拟API调用测试"""
    print("\n" + "=" * 50)
    print("模拟API调用测试...")

    try:
        from data_manager import DataManager
        data_manager = DataManager()

        # 模拟 /api/personas 接口
        print("1. 模拟 GET /api/personas")
        personas = data_manager.get_all_personas()
        api_response = json.dumps(personas, ensure_ascii=False, indent=2)
        print(f"   响应数据: {api_response[:200]}...")

        # 模拟创建新人设
        print("2. 模拟 POST /api/personas")
        success = data_manager.save_persona(
            name="测试助手",
            description="用于测试的AI助手",
            system_prompt="你是一个测试用的AI助手，请简洁明了地回答问题。",
            is_default=False
        )
        print(f"   创建结果: {'成功' if success else '失败'}")

        # 模拟会话创建
        print("3. 模拟 POST /api/session")
        import uuid
        session_id = str(uuid.uuid4())
        personas = data_manager.get_all_personas()
        if personas:
            test_persona = [p for p in personas if p['name'] == '测试助手']
            if test_persona:
                persona_id = test_persona[0]['id']
                data_manager.save_session(session_id, "API测试会话", persona_id)
                print(f"   会话创建成功，使用人设: {test_persona[0]['name']}")

        print("\n✅ API模拟测试通过!")
        return True

    except Exception as e:
        print(f"\n❌ API模拟测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🤖 Qwen AI 聊天机器人 - 人设功能测试")

    # 测试核心功能
    persona_test_passed = test_persona_functions()

    # 模拟API调用
    api_test_passed = simulate_api_calls()

    # 总结
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"   人设功能: {'✅ 通过' if persona_test_passed else '❌ 失败'}")
    print(f"   API模拟: {'✅ 通过' if api_test_passed else '❌ 失败'}")

    if persona_test_passed and api_test_passed:
        print("\n🎉 所有测试通过！人设功能可以正常使用。")
        print("\n📝 接下来可以:")
        print("   1. 启动Web服务: python3 web_interface/app.py")
        print("   2. 在浏览器中访问: http://localhost:8000")
        print("   3. 测试人设选择和聊天功能")
    else:
        print("\n⚠️  部分测试失败，请检查数据库连接和依赖安装。")

if __name__ == "__main__":
    main()