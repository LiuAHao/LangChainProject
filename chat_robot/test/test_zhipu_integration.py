#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智普API集成测试
用于测试智普API的连接和基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from chat_robot.config_manager import config_manager
from chat_robot.chat_api import ChatAPI


def test_zhipu_config():
    """测试智普API配置"""
    print("🔍 测试智普API配置...")
    
    ai_config = config_manager.get_ai_config()
    
    print(f"  ZHIPU_API_ENABLED: {ai_config['zhipu_api_enabled']}")
    print(f"  ZHIPU_API_KEY: {ai_config['zhipu_api_key']}")
    print(f"  ZHIPU_BASE_URL: {ai_config['zhipu_base_url']}")
    
    if ai_config['zhipu_api_enabled']:
        print("✅ 智普API已启用")
        return True
    else:
        print("⚠️  智普API未启用")
        return True


def test_zhipu_connection():
    """测试智普API连接"""
    print("\n🔍 测试智普API连接...")
    
    try:
        # 创建ChatAPI实例，这会自动初始化客户端
        chat_api = ChatAPI()
        
        # 检查是否使用智普API
        ai_config = config_manager.get_ai_config()
        if not ai_config['zhipu_api_enabled']:
            print("⚠️  智普API未启用，跳过连接测试")
            return True
            
        # 测试连接
        success = chat_api._test_model_connection()
        if success:
            print("✅ 智普API连接测试成功")
            return True
        else:
            print("❌ 智普API连接测试失败")
            return False
            
    except Exception as e:
        # 如果智普API未启用，这是预期的行为
        ai_config = config_manager.get_ai_config()
        if not ai_config['zhipu_api_enabled']:
            print("⚠️  智普API未启用，跳过连接测试")
            return True
        print(f"❌ 测试过程中出错: {e}")
        return False


def main():
    """主测试函数"""
    print("🤖 智普API集成测试")
    print("=" * 50)
    
    success = True
    success &= test_zhipu_config()
    success &= test_zhipu_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("💥 部分测试失败!")
        return 1


if __name__ == "__main__":
    exit(main())