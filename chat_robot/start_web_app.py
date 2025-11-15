#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启动Web界面应用的脚本
"""

import os
import sys
import subprocess
import time

def start_web_app():
    """
    启动Web界面应用
    """
    print("正在启动Qwen聊天机器人Web界面...")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 构建uvicorn命令
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "chat_robot.web_interface.app:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ]
    
    print("启动命令:", " ".join(cmd))
    print("工作目录:", project_root)
    print("=" * 50)
    print("Web界面将在以下地址可用:")
    print("http://localhost:8000")
    print("=" * 50)
    print("按 Ctrl+C 停止服务")
    print()
    
    process = None
    try:
        # 启动Web服务
        process = subprocess.Popen(cmd, cwd=project_root)
        process.wait()
    except KeyboardInterrupt:
        print("\n正在停止Web服务...")
        if process:
            process.terminate()
            process.wait()
        print("Web服务已停止")
    except Exception as e:
        print(f"启动Web服务时出错: {e}")

if __name__ == "__main__":
    start_web_app()