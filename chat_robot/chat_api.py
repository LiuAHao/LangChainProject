import os
from typing import List, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from .data_manager import DataManager
from .prompt_manager import PromptManager
from .config_manager import config_manager
from .log_manager import log_manager

class ChatAPI:
    """聊天API接口，集成数据管理、提示词管理和模型调用"""

    def __init__(self):
        """初始化聊天API"""
        # 初始化组件
        self.data_manager = DataManager()

        # 获取配置
        self.ai_config = config_manager.get_ai_config()
        self.context_config = config_manager.get_context_config()

        # 初始化OpenAI客户端
        self.client = self._initialize_client()
        
        # 初始化提示词管理器
        self.prompt_manager = PromptManager(self.client)

        # 创建数据表
        try:
            self.data_manager.create_tables()
            # 记录API初始化成功
            log_manager.log_api_request("system", [{"role": "system", "content": "ChatAPI initialized"}], 
                                      self.ai_config["model_name"], 0, 0, "api")
                    
            # 测试模型连接
            self._test_model_connection()
        except Exception as e:
            print(f"创建数据表时出错: {e}")
            log_manager.log_error("system", "initialization_error", str(e), "api")
    
    def _initialize_client(self):
        """根据配置初始化AI模型客户端"""
        # 根据启用的开关来确定使用的提供商
        if self.ai_config["local_model_enabled"]:
            return OpenAI(
                api_key=self.ai_config["openai_api_key"] or "local-key",
                base_url=self.ai_config["openai_base_url"] or "http://localhost:8001/v1"
            )
        elif self.ai_config["openai_api_enabled"]:
            return OpenAI(
                api_key=self.ai_config["openai_api_key"],
                base_url=self.ai_config["openai_base_url"]
            )
        elif self.ai_config["deepseek_api_enabled"]:
            return OpenAI(
                api_key=self.ai_config["deepseek_api_key"],
                base_url=self.ai_config["deepseek_base_url"]
            )
        elif self.ai_config["zhipu_api_enabled"]:
            return OpenAI(
                api_key=self.ai_config["zhipu_api_key"],
                base_url=self.ai_config["zhipu_base_url"]
            )
        else:
            # 默认使用本地模型
            return OpenAI(
                api_key=self.ai_config["openai_api_key"] or "local-key",
                base_url=self.ai_config["openai_base_url"] or "http://localhost:8001/v1"
            )
    
    def _get_model_name(self):
        """根据当前启用的AI提供商获取相应的模型名称"""
        if self.ai_config["local_model_enabled"]:
            return self.ai_config["local_model_name"] or self.ai_config["model_name"]
        elif self.ai_config["openai_api_enabled"]:
            return self.ai_config["openai_model"] or self.ai_config["model_name"]
        elif self.ai_config["deepseek_api_enabled"]:
            return self.ai_config["deepseek_model"] or self.ai_config["model_name"]
        elif self.ai_config["zhipu_api_enabled"]:
            return self.ai_config["zhipu_model"] or self.ai_config["model_name"]
        else:
            # 默认使用本地模型名称
            return self.ai_config["local_model_name"] or self.ai_config["model_name"]
    
    def _test_model_connection(self):
        """测试模型连接"""
        try:
            # 获取当前应该使用的模型名称
            model_name = self._get_model_name()
            
            # 发送一个简单的测试请求
            messages = [{"role": "user", "content": "你好"}]
            log_manager.log_api_request("test_session", messages, model_name, 10, 0.7)
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=10
            )
            log_manager.log_api_response("test_session", response.choices[0].message.content if response.choices[0].message.content else "")
            print(f"✅ AI模型连接测试成功")
            return True
        except Exception as e:
            print(f"❌ 模型连接测试失败: {e}")
            return False
    
    def summarize_history(self, session_id: str) -> str:
        """
        对历史聊天记录进行摘要

        Args:
            session_id (str): 会话ID

        Returns:
            str: 历史记录摘要
        """
        # 检查是否启用上下文压缩
        if not self.context_config["enable_compression"]:
            return ""

        # 获取消息总数
        message_count = self.data_manager.get_message_count(session_id)
        threshold = self.context_config["summary_threshold"]

        # 如果消息少于阈值，则不需要摘要
        if message_count <= threshold:
            return ""

        # 检查是否已有最近的摘要
        existing_summary = self.data_manager.get_recent_summary(session_id)
        if existing_summary:
            return existing_summary

        # 计算需要摘要的消息数量（除了最近的消息）
        window_size = self.context_config["window_size"]
        summary_limit = max(0, message_count - window_size)
        if summary_limit == 0:
            return ""

        # 获取需要摘要的历史消息
        history_messages = self.data_manager.get_history_messages(session_id, limit=summary_limit)

        if not history_messages:
            return ""

        # 格式化历史消息用于日志记录
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history_messages])
        
        # 使用PromptManager生成摘要
        summary_model_name = self._get_model_name()
        try:
            summary = self.prompt_manager.summarize_history(
                session_id, 
                history_messages, 
                summary_model_name, 
                512
            )
            # 构造用于日志记录的消息
            log_messages = [
                {"role": "system", "content": "你是一个专业的对话摘要助手。请将用户与AI的对话历史总结成简洁的摘要，保留关键信息和上下文。摘要应该清晰、准确、便于后续对话参考。"},
                {"role": "user", "content": f"请将以下对话历史总结成一个简洁的摘要，以便在后续对话中提供上下文：\n\n{history_text}\n\n摘要："}
            ]
            log_manager.log_api_request(session_id, log_messages, summary_model_name, 512, 0.3)
            log_manager.log_api_response(session_id, summary)

            # 保存摘要到数据库
            if summary:
                self.data_manager.save_summary(session_id, summary, len(history_messages))

            return summary
        except Exception as e:
            print(f"生成摘要时出错: {e}")
            return ""
    
    def chat_with_history(self, session_id: str, user_input: str, persona_id: int = None) -> str:
        """
        带历史记录的聊天

        Args:
            session_id (str): 会话ID
            user_input (str): 用户输入
            persona_id (int): 人设ID，可选

        Returns:
            str: 模型回复
        """
        # 获取当前应该使用的模型名称
        model_name = self._get_model_name()
        
        # 记录聊天请求开始
        log_manager.log_api_request(session_id, [{"role": "user", "content": "Chat request started"}], 
                                  model_name, 0, 0, "api")
        # 首先获取人设信息
        persona_system_prompt = ""
        if persona_id:
            try:
                persona = self.data_manager.get_persona_by_id(persona_id)
                if persona and persona.get("system_prompt"):
                    persona_system_prompt = persona["system_prompt"]
                    # 更新会话的人设信息
                    self.data_manager.update_session(session_id, persona_id=persona_id)
            except Exception as e:
                print(f"获取人设信息失败: {e}")

        # 处理可能包含系统提示的用户输入（已弃用，保留兼容性）
        if "[系统提示:" in user_input:
            # 提取系统提示词
            start_idx = user_input.find("[系统提示:") + 6
            end_idx = user_input.find("]", start_idx)
            if end_idx > start_idx:
                legacy_system_prompt = user_input[start_idx:end_idx]
                # 如果没有现代人设，使用旧的方式
                if not persona_system_prompt:
                    persona_system_prompt = legacy_system_prompt
                # 移除系统提示部分
                user_input = user_input[end_idx + 1:].strip()

        # 确保会话存在
        try:
            self.data_manager.save_session(session_id, "新对话", persona_id=persona_id)
        except Exception as e:
            # 如果会话已存在或其他问题，继续执行
            print(f"会话处理信息: {e}")
            
        # 保存用户消息
        try:
            self.data_manager.save_message(session_id, "user", user_input)
            # 记录用户消息保存成功
            log_manager.log_database_operation(session_id, "save", "user_message", {
                "content_length": len(user_input)
            }, "api")
        except Exception as e:
            print(f"保存用户消息失败: {e}")
            log_manager.log_error(session_id, "save_message_error", str(e), "api")
            return "抱歉，我在处理您的请求时遇到了问题。请稍后再试。"

        # 获取最近的对话记录
        window_size = self.context_config["window_size"]
        recent_messages = self.data_manager.get_recent_messages(session_id, limit=window_size)

        # 生成历史摘要
        history_summary = self.summarize_history(session_id)
        # 记录历史摘要生成结果
        log_manager.log_system_prompt(session_id, f"History summary generated: {len(history_summary) if history_summary else 0} characters", "api")

        # 使用PromptManager构建系统提示词
        base_system_prompt = "你是一个AI助手，请根据用户的需求提供准确、有用的回答。"
        full_system_prompt = self.prompt_manager.build_system_prompt(
            base_system_prompt, 
            persona_system_prompt, 
            history_summary
        )
        # 记录系统提示词构建
        log_manager.log_system_prompt(session_id, f"System prompt built with {len(full_system_prompt)} characters", "api")

        # 使用PromptManager构建完整的消息列表
        messages: List[ChatCompletionMessageParam] = self.prompt_manager.build_messages(
            full_system_prompt, 
            recent_messages, 
            user_input
        )  # type: ignore

        try:
            # 记录系统提示词
            log_manager.log_system_prompt(session_id, full_system_prompt, "api")
            
            # 记录API请求
            log_manager.log_api_request(
                session_id, 
                [{"role": msg["role"], "content": msg["content"]} for msg in messages], 
                model_name, 
                self.ai_config["max_tokens"], 
                self.ai_config["temperature"],
                "api"
            )
            
            # 调用模型
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=self.ai_config["max_tokens"],
                temperature=self.ai_config["temperature"]
            )

            # 获取模型回复
            content = response.choices[0].message.content
            assistant_response = content if content else ""
            
            # 记录API响应
            log_manager.log_api_response(session_id, assistant_response, 
                                       response.usage.prompt_tokens if response.usage else 0,
                                       response.usage.completion_tokens if response.usage else 0,
                                       "api")

            # 保存模型回复
            try:
                self.data_manager.save_message(session_id, "assistant", assistant_response)
                # 记录模型回复保存成功
                log_manager.log_database_operation(session_id, "save", "assistant_response", {
                    "content_length": len(assistant_response)
                }, "api")
            except Exception as e:
                print(f"保存模型回复失败: {e}")
                log_manager.log_error(session_id, "save_response_error", str(e), "api")

            return assistant_response
        except Exception as e:
            error_msg = f"调用模型时出错: {e}"
            print(error_msg)
            # 记录错误日志
            log_manager.log_error(session_id, "model_call_error", str(e))
            # 提供降级响应
            fallback_response = "您好！我是Qwen AI助手。我暂时无法处理您的请求，请稍后再试。您可以尝试重新启动服务或检查网络连接。"
            # 保存错误信息到数据库
            try:
                self.data_manager.save_message(session_id, "assistant", fallback_response)
            except:
                pass
            return fallback_response

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