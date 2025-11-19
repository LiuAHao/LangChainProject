from typing import List, Dict, Any, Optional
from openai import OpenAI
from .log_manager import log_manager

class PromptManager:
    """提示词管理器，负责构建和管理聊天提示词"""
    
    def __init__(self, client: OpenAI):
        """初始化提示词管理器"""
        self.client = client
        # 记录提示词管理器初始化
        log_manager.log_system_prompt("system", "PromptManager initialized", "prompt")
    
    def build_system_prompt(self, base_prompt: str, persona_prompt: str = "", history_summary: str = "") -> str:
        """
        构建系统提示词
        
        Args:
            base_prompt (str): 基础系统提示词
            persona_prompt (str): 人设提示词
            history_summary (str): 历史对话摘要
            
        Returns:
            str: 完整的系统提示词
        """
        # 使用模板提示用户需要扮演的人设是什么
        template = "你必须严格扮演以下角色，不得透露自己是AI或语言模型：\n\n{}\n\n如果未提供具体人设，你可以自由回答用户的问题。"
        
        # 如果有人设提示词，使用人设提示词
        if persona_prompt:
            full_system_prompt = template.format(persona_prompt)
        # 如果有基础提示词，使用基础提示词
        elif base_prompt:
            full_system_prompt = template.format(base_prompt)
        # 如果都没有，使用默认模板
        else:
            full_system_prompt = "你是一个AI助手，请根据用户的需求提供准确、有用的回答。"
            
        # 如果有历史摘要，添加到系统提示词中
        if history_summary:
            full_system_prompt = f"{full_system_prompt}\n\n历史对话摘要：{history_summary}"
            
        # 记录系统提示词构建
        log_manager.log_system_prompt("system", f"Built system prompt with persona: {bool(persona_prompt)}, history: {bool(history_summary)}", "prompt")
        
        return full_system_prompt
    
    def build_messages(self, system_prompt: str, recent_messages: List[Dict[str, str]], 
                      user_input: str) -> List[Dict[str, str]]:
        """
        构建完整的消息列表
        
        Args:
            system_prompt (str): 系统提示词
            recent_messages (List[Dict[str, str]]): 最近的对话记录
            user_input (str): 当前用户输入
            
        Returns:
            List[Dict[str, str]]: 完整的消息列表
        """
        # 构造完整的提示词
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加最近的对话记录
        for msg in recent_messages:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def summarize_history(self, session_id: str, history_messages: List[Dict[str, str]], 
                         model_name: str, max_tokens: int = 512) -> str:
        """
        对历史聊天记录进行摘要
        
        Args:
            session_id (str): 会话ID
            history_messages (List[Dict[str, str]]): 历史消息列表
            model_name (str): 模型名称
            max_tokens (int): 最大token数
            
        Returns:
            str: 历史记录摘要
        """
        if not history_messages:
            # 记录空历史消息
            log_manager.log_system_prompt(session_id, "No history messages to summarize", "prompt")
            return ""
        
        # 格式化历史消息
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history_messages])
        
        # 记录摘要生成请求
        log_manager.log_system_prompt(session_id, f"Generating summary for {len(history_messages)} messages", "prompt")
        
        # 调用模型生成摘要
        try:
            messages = [
                {"role": "system", "content": "你是一个专业的对话摘要助手。请将用户与AI的对话历史总结成简洁的摘要，保留关键信息和上下文。摘要应该清晰、准确、便于后续对话参考。"},
                {"role": "user", "content": f"请将以下对话历史总结成一个简洁的摘要，以便在后续对话中提供上下文：\n\n{history_text}\n\n摘要："}
            ]
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3  # 使用较低温度确保摘要准确性
            )
            
            content = response.choices[0].message.content
            # 记录摘要生成结果
            if content:
                log_manager.log_system_prompt(session_id, f"Generated summary with {len(content)} characters", "prompt")
            return content.strip() if content else ""
        except Exception as e:
            print(f"生成摘要时出错: {e}")
            # 记录摘要生成错误
            log_manager.log_error(session_id, "summary_generation_error", str(e), "prompt")
            return ""