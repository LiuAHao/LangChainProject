#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试前后端接口连接
"""

import requests
import json
import time

def test_model_api():
    """测试模型API接口"""
    print("测试模型API接口...")
    
    try:
        # 测试模型列表接口
        response = requests.get("http://localhost:8001/v1/models")
        if response.status_code == 200:
            print("✓ 模型API接口正常")
            print(f"  返回数据: {response.json()}")
        else:
            print(f"✗ 模型API接口异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到模型API: {e}")
        return False
    
    return True

def test_web_api():
    """测试Web API接口"""
    print("测试Web API接口...")
    
    try:
        # 测试创建会话
        response = requests.post("http://localhost:8000/api/session")
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get("session_id")
            print(f"✓ 会话创建成功: {session_id}")
        else:
            print(f"✗ 会话创建失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到Web API: {e}")
        return False
    
    try:
        # 测试聊天接口
        chat_data = {
            "session_id": session_id,
            "message": "你好，介绍一下你自己"
        }
        response = requests.post(
            "http://localhost:8000/api/chat",
            headers={"Content-Type": "application/json"},
            data=json.dumps(chat_data)
        )
        
        if response.status_code == 200:
            chat_response = response.json()
            print("✓ 聊天接口正常")
            print(f"  模型回复: {chat_response.get('response', '无回复')[:100]}...")
        else:
            print(f"✗ 聊天接口异常: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 聊天接口调用失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始测试Qwen聊天机器人接口连接...")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(5)
    
    success = True
    success &= test_model_api()
    print()
    success &= test_web_api()
    
    print("=" * 50)
    if success:
        print("所有接口测试通过！前后端连接正常。")
        print("您可以通过以下地址访问聊天机器人:")
        print("  Web界面: http://localhost:8000")
        print("  模型API: http://localhost:8001")
    else:
        print("部分接口测试失败，请检查服务状态。")

if __name__ == "__main__":
    main()