#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Gemini API连接的脚本
"""

import sys
import os
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 加载环境变量
load_dotenv()

def test_gemini_connection():
    """测试Gemini API连接"""
    print("=== 测试Gemini API连接 ===")
    
    # 读取配置
    api_key = os.getenv("GEMINI_API_KEY")
    base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_enabled = os.getenv("GEMINI_API_ENABLED", "false").lower() == "true"
    
    print(f"Gemini API启用: {gemini_enabled}")
    print(f"API密钥: {'已设置' if api_key else '未设置'}")
    print(f"Base URL: {base_url}")
    print(f"模型名称: {model_name}")
    
    if not api_key:
        print("\n❌ 错误: GEMINI_API_KEY未设置")
        return False
    
    # 尝试导入OpenAI
    try:
        from openai import OpenAI
        print("\n✅ OpenAI库导入成功")
    except ImportError as e:
        print(f"\n❌ 错误: 无法导入OpenAI库 - {e}")
        print("请安装: pip install openai")
        return False
    
    # 测试连接
    try:
        print(f"\n🔄 正在测试连接到 {base_url}...")
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 发送测试请求
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Explain to me how AI works"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        if response.choices and response.choices[0].message.content:
            print("✅ API连接成功!")
            print(f"模型响应: {response.choices[0].message.content}")
            print(f"使用的模型: {response.model}")
            print(f"Token使用: {response.usage.total_tokens if response.usage else '未知'}")
            return True
        else:
            print("❌ API响应异常: 没有收到有效响应")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        
        # 提供常见错误的解决建议
        error_str = str(e).lower()
        
        if "authentication" in error_str or "unauthorized" in error_str or "401" in error_str:
            print("\n💡 可能的解决方案:")
            print("  1. 检查GEMINI_API_KEY是否正确")
            print("  2. 确认API密钥是否有效且未过期")
            print("  3. 检查账户余额是否充足")
            
        elif "connection" in error_str or "timeout" in error_str:
            print("\n💡 可能的解决方案:")
            print("  1. 检查网络连接")
            print("  2. 检查BASE_URL是否正确")
            print("  3. 如果使用代理，请检查代理设置")
            
        elif "model" in error_str or "not found" in error_str:
            print("\n💡 可能的解决方案:")
            print("  1. 检查GEMINI_MODEL是否正确")
            print("  2. 确认该模型在你的账户中可用")
            
        return False

def test_config_manager():
    """测试配置管理器"""
    print("\n=== 测试配置管理器 ===")
    
    try:
        from config_manager import config_manager
        
        ai_config = config_manager.get_ai_config()
        print("配置管理器获取的AI配置:")
        for key, value in ai_config.items():
            if "key" in key.lower():
                print(f"  {key}: {'已设置' if value else '未设置'}")
            else:
                print(f"  {key}: {value}")
                
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试Gemini API连接...")
    
    # 测试配置管理器
    config_ok = test_config_manager()
    
    # 测试API连接
    connection_ok = test_gemini_connection()
    
    print("\n" + "="*50)
    print("测试结果:")
    print(f"  配置管理器: {'✅ 正常' if config_ok else '❌ 异常'}")
    print(f"  API连接: {'✅ 正常' if connection_ok else '❌ 异常'}")
    
    if config_ok and connection_ok:
        print("\n🎉 所有测试通过! 可以正常使用Gemini API")
    else:
        print("\n⚠️ 存在问题，请根据上述提示进行修复")
        print("\n📖 修复建议:")
        print("  1. 确保GEMINI_API_KEY正确设置")
        print("  2. 确保网络连接正常")
        print("  3. 重启Web服务以应用新配置")
        print("  4. 检查防火墙和代理设置")