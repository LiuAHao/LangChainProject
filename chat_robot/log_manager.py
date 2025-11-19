import os
import json
import datetime
from typing import Dict, Any, List
from pathlib import Path

class LogManager:
    """日志管理器，用于记录API调用和关键信息"""
    
    def __init__(self, log_dir: str = "chat_robot/log"):
        """初始化日志管理器"""
        # 使用绝对路径确保在不同环境下都能正确创建日志目录
        project_root = Path(__file__).parent.parent
        self.log_dir = project_root / log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_log_file_path(self, session_id: str, module: str = "default") -> Path:
        """获取日志文件路径，支持模块分类"""
        # 创建模块子目录
        module_dir = self.log_dir / module
        module_dir.mkdir(exist_ok=True)
        return module_dir / f"{session_id}.log"
    
    def _write_log_entry(self, session_id: str, entry: Dict[str, Any], module: str = "default"):
        """写入日志条目"""
        log_file = self._get_log_file_path(session_id, module)
        timestamp = datetime.datetime.now().isoformat()
        entry["timestamp"] = timestamp
        entry["module"] = module
        
        # 确保日志目录存在
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def log_api_request(self, session_id: str, messages: List[Dict[str, str]], 
                       model: str, max_tokens: int, temperature: float, module: str = "api"):
        """记录API请求"""
        entry = {
            "type": "api_request",
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        self._write_log_entry(session_id, entry, module)
    
    def log_api_response(self, session_id: str, response: str, 
                        prompt_tokens: int = 0, completion_tokens: int = 0, module: str = "api"):
        """记录API响应"""
        entry = {
            "type": "api_response",
            "response": response,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        }
        self._write_log_entry(session_id, entry, module)
    
    def log_system_prompt(self, session_id: str, system_prompt: str, module: str = "prompt"):
        """记录系统提示词"""
        entry = {
            "type": "system_prompt",
            "system_prompt": system_prompt
        }
        self._write_log_entry(session_id, entry, module)
    
    def log_error(self, session_id: str, error_type: str, error_message: str, module: str = "error"):
        """记录错误信息"""
        entry = {
            "type": "error",
            "error_type": error_type,
            "error_message": error_message
        }
        self._write_log_entry(session_id, entry, module)
    
    def log_database_operation(self, session_id: str, operation: str, table: str, details: Dict[str, Any] = None, module: str = "database"):
        """记录数据库操作"""
        entry = {
            "type": "database_operation",
            "operation": operation,
            "table": table,
            "details": details or {}
        }
        self._write_log_entry(session_id, entry, module)
    
    def log_config_change(self, key: str, old_value: Any, new_value: Any, module: str = "config"):
        """记录配置变更"""
        entry = {
            "type": "config_change",
            "key": key,
            "old_value": old_value,
            "new_value": new_value
        }
        # 使用特殊session_id记录配置变更
        self._write_log_entry("config_changes", entry, module)
    
    def get_session_logs(self, session_id: str, module: str = "default") -> List[Dict[str, Any]]:
        """获取会话的所有日志"""
        log_file = self._get_log_file_path(session_id, module)
        logs = []
        
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
                        
        return logs

# 全局日志管理器实例
log_manager = LogManager()