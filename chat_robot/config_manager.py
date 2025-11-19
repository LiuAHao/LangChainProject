#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
用于管理应用的各种配置选项和开关
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from .log_manager import log_manager

class ConfigManager:
    """配置管理器"""

    def __init__(self):
        """初始化配置管理器"""
        # 加载环境变量
        load_dotenv()

        # 默认配置
        self.default_config = {
            # AI模型配置
            "LOCAL_MODEL_ENABLED": False,
            "OPENAI_API_ENABLED": False,
            "DEEPSEEK_API_ENABLED": False,
            "ZHIPU_API_ENABLED": True,

            # 模型参数配置
            "MODEL_NAME": "qwen2.5:3B",
            "LOCAL_MODEL_NAME": "qwen2.5:3B",
            "ZHIPU_MODEL": "glm-4.6",
            "OPENAI_MODEL": "gpt-3.5-turbo",
            "DEEPSEEK_MODEL": "deepseek-chat",
            "TEMPERATURE": 0.7,
            "MAX_TOKENS": 2000,

            # 上下文管理配置
            "CONTEXT_WINDOW_SIZE": 10,  # 保留的最近消息数量
            "SUMMARY_THRESHOLD": 20,    # 超过多少条消息后开始摘要
            "ENABLE_CONTEXT_COMPRESSION": True,

            # 数据库配置
            "MYSQL_URL": "mysql+pymysql://root:123456@localhost:3306/chat_robot",

            # Web服务配置
            "WEB_HOST": "0.0.0.0",
            "WEB_PORT": 8000,
            "WEB_RELOAD": True,
            "MODEL_SERVICE_PORT": 8001,  # 本地模型服务端口

            # 安全配置
            "ENABLE_CORS": True,
            "CORS_ORIGINS": ["*"],

            # 聊天配置
            "DEFAULT_SYSTEM_PROMPT": "你是一个有用的AI助手，请根据用户的人设要求来回答问题。",
            "MAX_SESSION_LENGTH": 100,  # 每个会话最大消息数
        }

        # 加载配置
        self.config = self._load_config()
        # 记录配置初始化
        log_manager.log_config_change("config_init", None, "initialized", "config")

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config = self.default_config.copy()

        # 从环境变量加载配置
        env_mappings = {
            "LOCAL_MODEL_ENABLED": "LOCAL_MODEL_ENABLED",
            "OPENAI_API_ENABLED": "OPENAI_API_ENABLED",
            "DEEPSEEK_API_ENABLED": "DEEPSEEK_API_ENABLED",
            "MODEL_NAME": "MODEL_NAME",
            "LOCAL_MODEL_NAME": "LOCAL_MODEL_NAME",
            "ZHIPU_MODEL": "ZHIPU_MODEL",
            "OPENAI_MODEL": "OPENAI_MODEL",
            "DEEPSEEK_MODEL": "DEEPSEEK_MODEL",
            "TEMPERATURE": "TEMPERATURE",
            "MAX_TOKENS": "MAX_TOKENS",
            "CONTEXT_WINDOW_SIZE": "CONTEXT_WINDOW_SIZE",
            "SUMMARY_THRESHOLD": "SUMMARY_THRESHOLD",
            "ENABLE_CONTEXT_COMPRESSION": "ENABLE_CONTEXT_COMPRESSION",
            "MYSQL_URL": "MYSQL_URL",
            "WEB_HOST": "WEB_HOST",
            "WEB_PORT": "WEB_PORT",
            "WEB_RELOAD": "WEB_RELOAD",
            "OPENAI_API_KEY": "OPENAI_API_KEY",
            "OPENAI_BASE_URL": "OPENAI_BASE_URL",
            "DEEPSEEK_API_KEY": "DEEPSEEK_API_KEY",
            "DEEPSEEK_BASE_URL": "DEEPSEEK_BASE_URL",
            "ZHIPU_API_KEY": "ZHIPU_API_KEY",
            "ZHIPU_BASE_URL": "ZHIPU_BASE_URL",
            "LOCAL_MODEL_BASE_URL": "LOCAL_MODEL_BASE_URL",
        }

        for config_key, env_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # 处理布尔值
                if config_key in ["LOCAL_MODEL_ENABLED", "OPENAI_API_ENABLED", "DEEPSEEK_API_ENABLED", "ZHIPU_API_ENABLED",
                                "ENABLE_CONTEXT_COMPRESSION", "WEB_RELOAD", "ENABLE_CORS"]:
                    config[config_key] = env_value.lower() in ("true", "1", "yes", "on")
                    # 调试信息
                    if config_key == "ZHIPU_API_ENABLED":
                        print(f"DEBUG: ZHIPU_API_ENABLED env_value={env_value}, result={config[config_key]}")
                # 处理数字
                elif config_key in ["TEMPERATURE", "MAX_TOKENS", "CONTEXT_WINDOW_SIZE",
                                  "SUMMARY_THRESHOLD", "WEB_PORT", "MAX_SESSION_LENGTH"]:
                    try:
                        config[config_key] = float(env_value) if "." in env_value else int(env_value)
                    except ValueError:
                        pass
                # 处理列表
                elif config_key == "CORS_ORIGINS":
                    if isinstance(env_value, str):
                        config[config_key] = [origin.strip() for origin in env_value.split(",")]
                else:
                    config[config_key] = env_value

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置值（仅在内存中）"""
        old_value = self.config.get(key)
        self.config[key] = value
        # 记录配置变更
        log_manager.log_config_change(key, old_value, value, "config")

    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI模型相关配置"""
        return {
            "local_model_enabled": self.get("LOCAL_MODEL_ENABLED"),
            "openai_api_enabled": self.get("OPENAI_API_ENABLED"),
            "deepseek_api_enabled": self.get("DEEPSEEK_API_ENABLED"),
            "zhipu_api_enabled": self.get("ZHIPU_API_ENABLED"),
            "model_name": self.get("MODEL_NAME"),
            "local_model_name": self.get("LOCAL_MODEL_NAME"),
            "zhipu_model": self.get("ZHIPU_MODEL"),
            "openai_model": self.get("OPENAI_MODEL"),
            "deepseek_model": self.get("DEEPSEEK_MODEL"),
            "temperature": self.get("TEMPERATURE"),
            "max_tokens": self.get("MAX_TOKENS"),
            "openai_api_key": self.get("OPENAI_API_KEY"),
            "openai_base_url": self.get("OPENAI_BASE_URL"),
            "deepseek_api_key": self.get("DEEPSEEK_API_KEY"),
            "deepseek_base_url": self.get("DEEPSEEK_BASE_URL"),
            "zhipu_api_key": self.get("ZHIPU_API_KEY"),
            "zhipu_base_url": self.get("ZHIPU_BASE_URL"),
            "local_model_base_url": self.get("LOCAL_MODEL_BASE_URL"),
        }

    def get_context_config(self) -> Dict[str, Any]:
        """获取上下文管理配置"""
        return {
            "window_size": self.get("CONTEXT_WINDOW_SIZE"),
            "summary_threshold": self.get("SUMMARY_THRESHOLD"),
            "enable_compression": self.get("ENABLE_CONTEXT_COMPRESSION"),
            "max_session_length": self.get("MAX_SESSION_LENGTH"),
        }

    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            "mysql_url": self.get("MYSQL_URL"),
        }

    def get_web_config(self) -> Dict[str, Any]:
        """获取Web服务配置"""
        return {
            "host": self.get("WEB_HOST"),
            "port": self.get("WEB_PORT"),
            "reload": self.get("WEB_RELOAD"),
            "enable_cors": self.get("ENABLE_CORS"),
            "cors_origins": self.get("CORS_ORIGINS"),
        }
    
    def get_model_service_config(self) -> Dict[str, Any]:
        """获取模型服务配置"""
        return {
            "port": self.get("MODEL_SERVICE_PORT"),
        }

    def reload_config(self):
        """重新加载配置"""
        self.config = self._load_config()

    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置（隐藏敏感信息）"""
        all_config = self.config.copy()
        # 隐藏敏感信息
        sensitive_keys = ["OPENAI_API_KEY", "DEEPSEEK_API_KEY", "ZHIPU_API_KEY"]
        for key in sensitive_keys:
            if key in all_config:
                all_config[key] = "***隐藏***" if all_config[key] else None
        return all_config

# 创建全局配置管理器实例
config_manager = ConfigManager()