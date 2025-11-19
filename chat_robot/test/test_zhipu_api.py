#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智普API调用测试
用于测试智普API的连接和基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from openai import OpenAI
from chat_robot.config_manager import config_manager

# 重新加载配置以确保获取最新的环境变量
config_manager.reload_config()


def test_zhipu_api_connection():
    """测试智普API连接"""
    print("🔍 测试智普API连接...")
    
    # 获取智普API配置
    ai_config = config_manager.get_ai_config()
    
    # 检查智普API是否启用
    if not ai_config.get('zhipu_api_enabled', False):
        print("⚠️  智普API未启用，跳过测试")
        return True
    
    try:
        # 初始化智普API客户端
        client = OpenAI(
            api_key=ai_config.get('zhipu_api_key', ''),
            base_url=ai_config.get('zhipu_base_url', 'https://open.bigmodel.cn/api/paas/v4/')
        )
        
        # 发送测试请求
        print("🔄 正在发送测试请求...")
        # 使用智普专用的模型名称
        zhipu_model = ai_config.get('zhipu_model', 'glm-4')
        print(f"正在使用智普模型: {zhipu_model}")
        
        # 使用更完整的参数配置，类似于官方示例
        response = client.chat.completions.create(
            model=zhipu_model,
            messages=[
                {"role": "system", "content": "你是一个有用的AI助手"},
                {"role": "user", "content": "你好，这是一个连接测试。"}
            ],
            top_p=0.7,
            temperature=0.9,
            max_tokens=100
        )
        
        # 检查响应
        print(f"响应对象类型: {type(response)}")
        print(f"响应对象内容: {response}")
        
        if hasattr(response, 'choices') and response.choices:
            if response.choices[0].message and response.choices[0].message.content:
                print("✅ 智普API连接成功!")
                print(f"模型响应: {response.choices[0].message.content}")
                print(f"使用的模型: {response.model}")
                if response.usage:
                    print(f"Token使用: 提示{response.usage.prompt_tokens}, 补全{response.usage.completion_tokens}, 总计{response.usage.total_tokens}")
                return True
            else:
                print("❌ 智普API响应异常: choices[0].message.content为空")
                print(f"message对象: {response.choices[0].message}")
                return False
        else:
            print("❌ 智普API响应异常: 没有收到有效响应或choices为空")
            print(f"响应的choices属性: {getattr(response, 'choices', '无choices属性')}")
            return False
            
    except Exception as e:
        print(f"❌ 智普API连接失败: {e}")
        
        # 提供常见错误的解决建议
        error_str = str(e).lower()
        if "authentication" in error_str or "unauthorized" in error_str or "401" in error_str:
            print("\n💡 可能的解决方案:")
            print("  1. 检查ZHIPU_API_KEY是否正确配置")
            print("  2. 确认API密钥是否有效且未过期")
            print("  3. 检查账户余额是否充足")
        elif "connection" in error_str or "timeout" in error_str:
            print("\n💡 可能的解决方案:")
            print("  1. 检查网络连接")
            print("  2. 确认ZHIPU_BASE_URL是否正确")
            print("  3. 检查防火墙设置")
        elif "model" in error_str or "not found" in error_str:
            print("\n💡 可能的解决方案:")
            print("  1. 检查使用的模型名称是否正确")
            print("  2. 确认该模型在您的账户中可用")
            print("  3. 尝试使用其他模型，如'glm-4', 'glm-3-turbo'等")
        
        return False


def test_zhipu_api_config():
    """测试智普API配置"""
    print("🔍 检查智普API配置...")
    
    # 打印环境变量值用于调试
    import os
    print(f"ZHIPU_API_ENABLED env var: {os.getenv('ZHIPU_API_ENABLED')}")
    
    ai_config = config_manager.get_ai_config()
    print(f"zhipu_api_enabled in config: {ai_config.get('zhipu_api_enabled')}")
    
    # 检查必要配置项
    required_configs = [
        ('zhipu_api_enabled', '智普API启用开关'),
        ('zhipu_api_key', '智普API密钥'),
        ('zhipu_base_url', '智普API基础URL'),
        ('zhipu_model', '智普模型名称')
    ]
    
    all_good = True
    for config_key, config_desc in required_configs:
        value = ai_config.get(config_key)
        if value is None:
            print(f"❌ 缺少配置项: {config_desc} ({config_key})")
            all_good = False
        else:
            # 对于密钥类配置，只显示是否配置而不显示具体值
            if 'key' in config_key.lower():
                print(f"✅ {config_desc}: {'已配置' if value else '未配置'}")
            else:
                print(f"✅ {config_desc}: {value}")
    
    return all_good


def main():
    """主测试函数"""
    print("🤖 智普API调用测试")
    print("=" * 50)
    
    # 测试配置
    config_ok = test_zhipu_api_config()
    
    if not config_ok:
        print("\n❌ 配置检查失败，请检查配置项")
        return 1
    
    # 测试连接
    connection_ok = test_zhipu_api_connection()
    
    print("\n" + "=" * 50)
    if config_ok and connection_ok:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("💥 部分测试失败!")
        return 1


if __name__ == "__main__":
    exit(main())