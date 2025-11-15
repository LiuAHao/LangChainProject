import os
from typing import List, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from .data_manager import DataManager
from .prompt_manager import PromptManager

class ChatAPI:
    """聊天API接口，集成数据管理、提示词管理和模型调用"""
    
    def __init__(self):
        """初始化聊天API"""
        # 初始化组件
        self.data_manager = DataManager()
        self.prompt_manager = PromptManager()
        
        # 初始化OpenAI客户端（连接本地Qwen服务）
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:8001/v1")
        )
        
        # 创建数据表
        self.data_manager.create_tables()
    
    def summarize_history(self, session_id: str) -> str:
        """
        对历史聊天记录进行摘要
        
        Args:
            session_id (str): 会话ID
            
        Returns:
            str: 历史记录摘要
        """
        # 获取消息总数
        message_count = self.data_manager.get_message_count(session_id)
        
        # 如果消息少于等于4条，则不需要摘要
        if message_count <= 4:
            return ""
        
        # 计算需要摘要的消息数量（除了最近的4条）
        summary_limit = max(0, message_count - 4)
        if summary_limit == 0:
            return ""
        
        # 获取需要摘要的历史消息（除了最近的4条）
        history_messages = self.data_manager.get_history_messages(session_id, limit=summary_limit)
        
        if not history_messages:
            return ""
        
        # 格式化历史消息
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history_messages])
        
        # 调用模型生成摘要
        try:
            response = self.client.chat.completions.create(
                model="qwen2.5-3b",
                messages=[
                    {"role": "system", "content": "你是一个有用的助手，请用中文回答所有问题。"},
                    {"role": "user", "content": f"请将以下对话历史总结成一个简洁的摘要，以便在后续对话中提供上下文：\n\n{history_text}\n\n摘要："}
                ],
                max_tokens=512,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            print(f"生成摘要时出错: {e}")
            return ""
    
    def chat_with_history(self, session_id: str, user_input: str) -> str:
        """
        带历史记录的聊天
        
        Args:
            session_id (str): 会话ID
            user_input (str): 用户输入
            
        Returns:
            str: 模型回复
        """
        # 保存会话和用户消息
        self.data_manager.save_session(session_id)
        self.data_manager.save_message(session_id, "user", user_input)
        
        # 获取最近的两条完整对话记录
        recent_messages = self.data_manager.get_recent_messages(session_id, limit=2)
        
        # 生成历史摘要
        history_summary = self.summarize_history(session_id)
        
        # 使用PromptManager构造提示词
        if history_summary:
            # 如果有历史摘要，则在系统提示词中加入摘要信息
            system_prompt = f"你是通义千问，由阿里云开发的大语言模型。你是一个有用的助手，请用中文回答所有问题。\n\n历史对话摘要：{history_summary}"
        else:
            # 如果没有历史摘要，使用默认系统提示词
            system_prompt = "你是通义千问，由阿里云开发的大语言模型。你是一个有用的助手，请用中文回答所有问题。"
        
        # 使用PromptManager处理提示词
        prompt_template = self.prompt_manager.get_prompt_template()
        
        # 构造完整的提示词
        messages: List[ChatCompletionMessageParam] = [{"role": "system", "content": system_prompt}]
        
        # 添加最近的对话记录
        for msg in recent_messages:
            messages.append({"role": msg["role"], "content": msg["content"]})  # type: ignore
        
        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})  # type: ignore
        
        try:
            # 调用模型
            response = self.client.chat.completions.create(
                model="qwen2.5-3b",
                messages=messages,
                max_tokens=512,
                temperature=0.7
            )
            
            # 获取模型回复
            content = response.choices[0].message.content
            assistant_response = content if content else ""
            
            # 保存模型回复
            self.data_manager.save_message(session_id, "assistant", assistant_response)
            
            return assistant_response
        except Exception as e:
            error_msg = f"调用模型时出错: {e}"
            print(error_msg)
            return "抱歉，我在处理您的请求时遇到了问题。"

# 使用示例
if __name__ == "__main__":
    # 创建聊天API实例
    chat_api = ChatAPI()
    
    # 示例对话
    session_id = "test_session_001"
    
    # 第一轮对话
    user_input = "你好，介绍一下你自己"
    response = chat_api.chat_with_history(session_id, user_input)
    print(f"用户: {user_input}")
    print(f"助手: {response}\n")
    
    # 第二轮对话
    user_input = "你能帮我写一个Python函数来计算斐波那契数列吗？"
    response = chat_api.chat_with_history(session_id, user_input)
    print(f"用户: {user_input}")
    print(f"助手: {response}\n")