#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启动Web界面应用的脚本
"""

import os
import sys

def start_web_app():
    """
    启动Web界面应用
    """
    print("正在启动Qwen聊天机器人Web界面...")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, project_root)
    
    # 直接导入并运行Web应用
    try:
        from chat_robot.web_interface.app import app
        import uvicorn
        
        print("启动命令: uvicorn chat_robot.web_interface.app:app --host 0.0.0.0 --port 8000 --reload")
        print("工作目录:", project_root)
        print("=" * 50)
        print("Web界面将在以下地址可用:")
        print("http://localhost:8000")
        print("=" * 50)
        print("按 Ctrl+C 停止服务")
        print()
        
        # 使用uvicorn直接启动Web服务（阻塞方式）
        uvicorn.run(
            "chat_robot.web_interface.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            root_path=project_root
        )
    except Exception as e:
        print(f"启动Web服务时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_web_app()