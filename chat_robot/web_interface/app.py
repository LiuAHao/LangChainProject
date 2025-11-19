#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web界面应用主文件
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import sys
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from chat_robot.chat_api import ChatAPI
from chat_robot.data_manager import DataManager
from chat_robot.config_manager import config_manager

# 创建FastAPI应用实例
app = FastAPI(
    title="Qwen AI聊天助手",
    description="基于本地Qwen模型的现代化聊天机器人Web界面",
    version="2.0.0"
)

# 配置CORS
web_config = config_manager.get_web_config()
if web_config["enable_cors"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=web_config["cors_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 配置静态文件和模板目录
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# 初始化组件
data_manager = DataManager()
chat_api = ChatAPI()

# 确保数据库表存在
try:
    data_manager.create_tables()
except Exception as e:
    print(f"创建数据表时出错: {e}")

# 定义请求模型
class ChatRequest(BaseModel):
    session_id: str
    message: str
    persona_id: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class PersonaCreateRequest(BaseModel):
    name: str
    description: str
    system_prompt: str
    avatar_url: Optional[str] = None

class SessionCreateRequest(BaseModel):
    persona_id: Optional[int] = None
    title: Optional[str] = None

class SettingsUpdateRequest(BaseModel):
    settings: Dict[str, Any]

class SessionPersonaUpdateRequest(BaseModel):
    persona_id: int

# 主页路由
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """返回聊天机器人页面"""
    return templates.TemplateResponse("chat_robot.html", {"request": request})

# API路由：获取所有人设
@app.get("/api/personas")
async def get_personas():
    """获取所有AI人设"""
    try:
        personas = data_manager.get_all_personas()
        return personas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人设列表时出错: {str(e)}")

# API路由：创建新人设
@app.post("/api/personas")
async def create_persona(request: PersonaCreateRequest):
    """创建新的AI人设"""
    try:
        result = data_manager.save_persona(
            request.name,
            request.description,
            request.system_prompt,
            request.avatar_url
        )
        if result:
            return {"success": True, "message": "人设创建成功"}
        else:
            raise HTTPException(status_code=400, detail="人设创建失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建人设时出错: {str(e)}")

# API路由：获取所有会话
@app.get("/api/sessions")
async def get_sessions():
    """获取所有聊天会话"""
    try:
        sessions = data_manager.get_all_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话列表时出错: {str(e)}")

# API路由：创建新会话
@app.post("/api/session")
async def create_session(request: Optional[SessionCreateRequest] = None):
    """创建新的聊天会话"""
    try:
        session_id = str(uuid.uuid4())
        persona_id = request.persona_id if request else None
        title = request.title if request else None

        # 保存会话
        data_manager.save_session(session_id, title, persona_id)
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话时出错: {str(e)}")

# API路由：更新会话人设
@app.put("/api/session/{session_id}/persona")
async def update_session_persona(session_id: str, request: SessionPersonaUpdateRequest):
    """更新会话的AI人设"""
    try:
        success = data_manager.update_session(session_id, persona_id=request.persona_id)
        if success:
            # 重新加载会话信息以返回更新后的数据
            sessions = data_manager.get_all_sessions()
            current_session = next((s for s in sessions if s["session_id"] == session_id), None)

            # 获取人设信息
            persona_info = None
            if request.persona_id:
                persona_info = data_manager.get_persona_by_id(request.persona_id)

            return {
                "success": True,
                "message": "会话人设更新成功",
                "session": current_session,
                "persona": persona_info
            }
        else:
            raise HTTPException(status_code=400, detail="会话人设更新失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新会话人设时出错: {str(e)}")

# API路由：清空会话消息
@app.delete("/api/session/{session_id}/clear")
async def clear_session_messages(session_id: str):
    """清空会话的所有消息"""
    try:
        # 这里需要实现清空消息的逻辑
        # 由于当前的data_manager没有直接清空消息的方法，我们需要添加一个
        success = data_manager.clear_session_messages(session_id)
        if success:
            return {"success": True, "message": "会话消息已清空"}
        else:
            raise HTTPException(status_code=400, detail="清空会话消息失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空会话消息时出错: {str(e)}")

# API路由：删除会话
@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """删除整个会话及其所有消息"""
    try:
        success = data_manager.delete_session(session_id)
        if success:
            return {"success": True, "message": "会话删除成功"}
        else:
            raise HTTPException(status_code=400, detail="会话删除失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除会话时出错: {str(e)}")

# API路由：处理聊天消息
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """处理聊天消息的POST请求"""
    try:
        # 如果指定了人设，先更新会话的人设
        if chat_request.persona_id:
            data_manager.update_session(
                chat_request.session_id,
                persona_id=chat_request.persona_id
            )

        # 调用ChatAPI处理聊天请求
        response = chat_api.chat_with_history(
            chat_request.session_id,
            chat_request.message,
            persona_id=chat_request.persona_id
        )

        return ChatResponse(response=response, session_id=chat_request.session_id)
    except Exception as e:
        print(f"处理聊天请求时出错: {e}")
        raise HTTPException(status_code=500, detail=f"处理聊天请求时出错: {str(e)}")

# API路由：获取聊天历史
@app.get("/api/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 100):
    """获取指定会话的聊天历史"""
    try:
        recent_messages = data_manager.get_history_messages(session_id, limit=limit)
        return {"session_id": session_id, "messages": recent_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取聊天历史时出错: {str(e)}")

# API路由：保存设置
@app.post("/api/settings")
async def save_settings(request: SettingsUpdateRequest):
    """保存用户设置"""
    try:
        # 这里可以实现设置的持久化存储
        # 目前只是更新配置管理器中的设置
        for key, value in request.settings.items():
            config_manager.set(key, value)
        return {"success": True, "message": "设置保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存设置时出错: {str(e)}")

# API路由：获取当前设置
@app.get("/api/settings")
async def get_settings():
    """获取当前设置"""
    try:
        return config_manager.get_all_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置时出错: {str(e)}")

# API路由：获取系统状态
@app.get("/api/status")
async def get_system_status():
    """获取系统状态信息"""
    try:
        ai_config = config_manager.get_ai_config()
        context_config = config_manager.get_context_config()

        return {
            "status": "running",
            "ai_config": {
                "provider": ai_config["provider"],
                "local_model_enabled": ai_config["local_model_enabled"],
                "openai_api_enabled": ai_config["openai_api_enabled"],
                "deepseek_api_enabled": ai_config["deepseek_api_enabled"],
                "model_name": ai_config["model_name"],
            },
            "context_config": context_config,
            "features": {
                "multi_session": True,
                "ai_personas": True,
                "context_compression": context_config["enable_compression"],
                "custom_personas": True,
                "chat_export": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统状态时出错: {str(e)}")

# 健康检查路由
@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": str(uuid.uuid4())}

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "接口不存在"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )

# 运行服务器的说明
if __name__ == "__main__":
    import uvicorn
    web_config = config_manager.get_web_config()
    print("🤖 Qwen AI 聊天助手启动中...")
    print(f"📍 地址: http://{web_config['host']}:{web_config['port']}")
    print("🎯 功能特性:")
    print("   • 多会话管理")
    print("   • AI人设系统")
    print("   • 上下文压缩")
    print("   • 现代化界面")
    print(f"🚀 启动命令: uvicorn chat_robot.web_interface.app:app --host {web_config['host']} --port {web_config['port']} --reload")