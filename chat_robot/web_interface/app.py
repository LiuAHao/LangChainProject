#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web界面应用主文件
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from chat_robot.chat_api import ChatAPI

# 创建FastAPI应用实例
app = FastAPI(title="Qwen聊天机器人", description="基于本地Qwen模型的聊天机器人Web界面")

# 配置静态文件和模板目录
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# 初始化聊天API
chat_api = ChatAPI()

# 定义请求模型
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

# 主页路由
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    返回聊天机器人页面
    """
    return templates.TemplateResponse("chat_robot.html", {"request": request})

# API路由：处理聊天消息
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """
    处理聊天消息的POST请求
    
    Args:
        chat_request: 包含会话ID和用户消息的请求对象
        
    Returns:
        ChatResponse: 包含模型回复的响应对象
    """
    try:
        # 调用ChatAPI处理聊天请求
        response = chat_api.chat_with_history(chat_request.session_id, chat_request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理聊天请求时出错: {str(e)}")

# API路由：获取聊天历史
@app.get("/api/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    获取指定会话的聊天历史
    
    Args:
        session_id: 会话ID
        
    Returns:
        dict: 包含聊天历史的响应
    """
    try:
        # 获取最近的聊天记录
        recent_messages = chat_api.data_manager.get_recent_messages(session_id, limit=100)
        return {"session_id": session_id, "messages": recent_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取聊天历史时出错: {str(e)}")

# API路由：创建新的聊天会话
@app.post("/api/session")
async def create_session():
    """
    创建新的聊天会话
    
    Returns:
        dict: 包含新会话ID的响应
    """
    import uuid
    session_id = str(uuid.uuid4())
    # 保存会话
    chat_api.data_manager.save_session(session_id)
    return {"session_id": session_id}

# 运行服务器的说明
if __name__ == "__main__":
    import uvicorn
    print("请使用以下命令启动服务器:")
    print("uvicorn chat_robot.web_interface.app:app --host 0.0.0.0 --port 8000 --reload")