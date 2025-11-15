#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启动脚本：同时启动Qwen模型服务和Web界面服务
"""

import subprocess
import sys
import time
import os

def start_services():
    """启动所有服务"""
    print("正在启动Qwen聊天机器人服务...")
    print("=" * 50)
    
    # 启动Qwen模型服务 (在端口8001)
    print("1. 启动Qwen模型服务...")
    qwen_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "chat_robot.qwen_server:app", 
        "--host", "0.0.0.0", 
        "--port", "8001"
    ])
    
    # 等待几秒钟让模型服务启动
    print("等待模型服务启动...")
    time.sleep(5)
    
    # 启动Web界面服务 (在端口8000)
    print("2. 启动Web界面服务...")
    web_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "chat_robot.web_interface.app:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])
    
    print("服务启动完成!")
    print("访问地址:")
    print("  - Web界面: http://localhost:8000")
    print("  - 模型API: http://localhost:8001")
    print("按 Ctrl+C 停止所有服务")
    print("=" * 50)
    
    try:
        # 等待任一进程结束
        while True:
            if qwen_process.poll() is not None:
                print("Qwen模型服务已停止")
                web_process.terminate()
                break
            if web_process.poll() is not None:
                print("Web界面服务已停止")
                qwen_process.terminate()
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止所有服务...")
        qwen_process.terminate()
        web_process.terminate()
        print("所有服务已停止")

if __name__ == "__main__":
    start_services()