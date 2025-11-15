from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict, Any

class PromptManager:
    """提示词与上下文管理器，使用LangChain的ChatPromptTemplate"""
    
    def __init__(self):
        """初始化提示词管理器"""
        self.system_template = """你是通义千问，由阿里云开发的大语言模型。
你是一个有用的助手，请用{language}回答所有问题。"""
        
        self.user_template = "{user_input}"
        
        # 创建ChatPromptTemplate实例
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_template),
            ("user", self.user_template)
        ])
    
    def format_prompt(self, user_input: str, language: str = "中文"):
        """
        格式化提示词
        
        Args:
            user_input (str): 用户输入
            language (str): 语言设置，默认为中文
            
        Returns:
            格式化后的提示词
        """
        return self.prompt_template.format_prompt(user_input=user_input, language=language)
    
    def add_context(self, messages: List[Dict[str, str]]):
        """
        添加对话上下文
        
        Args:
            messages (List[Dict[str, str]]): 对话历史消息列表
            
        Returns:
            包含上下文的提示词模板
        """
        # 构建包含历史对话的提示词模板
        context_messages = [("system", self.system_template)]
        
        # 添加历史对话
        for message in messages:
            context_messages.append((message["role"], message["content"]))
        
        return ChatPromptTemplate.from_messages(context_messages)
    
    def get_prompt_template(self):
        """
        获取当前的提示词模板
        
        Returns:
            当前的提示词模板
        """
        return self.prompt_template