import os
import json
import datetime
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import threading
from datetime import timezone

class LogManager:
    """日志管理器，用于记录API调用和关键信息"""

    def __init__(self, log_dir: str = "chat_robot/log"):
        """初始化日志管理器"""
        # 使用绝对路径确保在不同环境下都能正确创建日志目录
        project_root = Path(__file__).parent.parent
        self.log_dir = project_root / log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 线程锁确保日志写入安全
        self._lock = threading.Lock()

        # 日志轮转配置
        self.max_log_files = 30  # 保留最近30天的日志
        self.max_file_size = 10 * 1024 * 1024  # 10MB最大文件大小

    def _format_timestamp(self, dt: Optional[datetime.datetime] = None) -> str:
        """格式化时间戳为易读格式"""
        if dt is None:
            dt = datetime.datetime.now(timezone.utc)
        # 转换为本地时间并格式化
        local_dt = dt.astimezone()
        return local_dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 保留毫秒

    def _get_log_file_path(self, session_id: str, module: str = "default", date: Optional[datetime.date] = None) -> Path:
        """获取日志文件路径，支持模块分类和日期"""
        if date is None:
            date = datetime.date.today()

        # 创建模块子目录
        module_dir = self.log_dir / module
        module_dir.mkdir(exist_ok=True)

        # 使用日期和session_id作为文件名，避免文件名混乱
        # 格式: YYYY-MM-DD_session-id.log
        clean_session_id = session_id.replace('/', '_').replace('\\', '_')[:50]  # 清理文件名
        filename = f"{date.strftime('%Y-%m-%d')}_{clean_session_id}.log"
        return module_dir / filename
    
    def _write_log_entry(self, session_id: str, entry: Dict[str, Any], module: str = "default"):
        """写入日志条目"""
        with self._lock:  # 确保线程安全
            # 添加格式化的时间戳
            current_time = datetime.datetime.now(timezone.utc)
            entry["readable_time"] = self._format_timestamp(current_time)
            entry["timestamp"] = current_time.isoformat()
            entry["module"] = module
            entry["session_id"] = session_id

            # 获取日志文件路径（按日期）
            log_file = self._get_log_file_path(session_id, module, current_time.date())

            # 检查文件大小，如果过大则轮转
            self._rotate_log_if_needed(log_file)

            # 确保日志目录存在
            log_file.parent.mkdir(parents=True, exist_ok=True)

            # 格式化日志输出，提高可读性
            formatted_entry = self._format_log_entry(entry)

            # 写入日志
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(formatted_entry + "\n")

    def _format_log_entry(self, entry: Dict[str, Any]) -> str:
        """格式化日志条目为易读格式"""
        # 创建一个简化的日志条目用于显示
        display_entry = {
            "time": entry["readable_time"],
            "type": entry.get("type", "unknown"),
            "session": entry.get("session_id", "unknown")[:8]  # 只显示session ID前8位
        }

        # 根据类型添加特定字段
        entry_type = entry.get("type")

        if entry_type == "api_request":
            display_entry.update({
                "model": entry.get("model", ""),
                "msg_count": len(entry.get("messages", [])),
                "temp": entry.get("temperature", 0)
            })
        elif entry_type == "api_response":
            usage = entry.get("usage", {})
            display_entry.update({
                "tokens": usage.get("total_tokens", 0),
                "resp_len": len(entry.get("response", ""))
            })
        elif entry_type == "database_operation":
            display_entry.update({
                "op": entry.get("operation", ""),
                "table": entry.get("table", ""),
                "details": entry.get("details", {})
            })
        elif entry_type == "error":
            display_entry.update({
                "error_type": entry.get("error_type", ""),
                "error": entry.get("error_message", "")[:100] + "..." if len(entry.get("error_message", "")) > 100 else entry.get("error_message", "")
            })

        # 返回格式化的JSON字符串
        return json.dumps(display_entry, ensure_ascii=False, separators=(',', ':'))

    def _rotate_log_if_needed(self, log_file: Path):
        """如果日志文件过大，进行轮转"""
        if log_file.exists() and log_file.stat().st_size > self.max_file_size:
            # 重命名当前文件
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_file = log_file.parent / f"{log_file.stem}_{timestamp}{log_file.suffix}"
            log_file.rename(rotated_file)

            # 清理旧日志文件
            self._cleanup_old_logs(log_file.parent)

    def _cleanup_old_logs(self, log_dir: Path):
        """清理超过保留天数的日志文件"""
        try:
            current_time = datetime.datetime.now(timezone.utc)
            cutoff_time = current_time - datetime.timedelta(days=self.max_log_files)

            for log_file in log_dir.glob("*.log"):
                try:
                    # 从文件名中提取日期
                    if log_file.stem.startswith("20"):  # 假设文件名以日期开头
                        date_str = log_file.stem.split('_')[0]
                        file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

                        if file_date < cutoff_time:
                            log_file.unlink()
                            print(f"已删除旧日志文件: {log_file}")
                except (ValueError, IndexError):
                    # 如果无法解析日期，跳过该文件
                    continue
        except Exception as e:
            print(f"清理日志文件时出错: {e}")
    
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
    
    def get_session_logs(self, session_id: str, module: str = "default", days: int = 7) -> List[Dict[str, Any]]:
        """获取会话的所有日志（支持多天）"""
        logs = []
        current_date = datetime.date.today()

        for i in range(days):
            log_date = current_date - datetime.timedelta(days=i)
            log_file = self._get_log_file_path(session_id, module, log_date)

            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    logs.append(json.loads(line))
                                except json.JSONDecodeError:
                                    continue
                except Exception as e:
                    print(f"读取日志文件失败 {log_file}: {e}")
                    continue

        # 按时间排序
        logs.sort(key=lambda x: x.get("timestamp", ""))
        return logs

    def get_log_summary(self, session_id: str, module: str = "default", days: int = 7) -> Dict[str, Any]:
        """获取日志摘要信息"""
        logs = self.get_session_logs(session_id, module, days)

        summary = {
            "total_logs": len(logs),
            "date_range": f"{(datetime.date.today() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')} 至 {datetime.date.today().strftime('%Y-%m-%d')}",
            "log_types": {},
            "total_tokens": 0,
            "total_api_calls": 0,
            "errors": 0
        }

        for log in logs:
            log_type = log.get("type", "unknown")
            summary["log_types"][log_type] = summary["log_types"].get(log_type, 0) + 1

            if log_type == "api_response":
                summary["total_tokens"] += log.get("tokens", 0)
                summary["total_api_calls"] += 1
            elif log_type == "error":
                summary["errors"] += 1

        return summary

    def list_log_files(self, module: str = "default") -> List[Dict[str, Any]]:
        """列出所有日志文件及其信息"""
        log_files = []
        module_dir = self.log_dir / module

        if module_dir.exists():
            for log_file in module_dir.glob("*.log"):
                try:
                    stat = log_file.stat()
                    # 从文件名提取日期和session_id
                    stem = log_file.stem
                    if '_' in stem and stem.startswith("20"):
                        date_str = stem.split('_')[0]
                        session_id = '_'.join(stem.split('_')[1:])  # 处理session_id中包含下划线的情况

                        log_files.append({
                            "filename": log_file.name,
                            "date": date_str,
                            "session_id": session_id,
                            "size": stat.st_size,
                            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"解析日志文件信息失败 {log_file}: {e}")
                    continue

        # 按日期和时间排序
        log_files.sort(key=lambda x: (x["date"], x["session_id"]), reverse=True)
        return log_files

    def cleanup_logs(self, days_to_keep: int = None, module: str = None):
        """手动清理日志文件"""
        if days_to_keep is None:
            days_to_keep = self.max_log_files

        if module:
            modules = [module]
        else:
            # 获取所有模块目录
            modules = [d.name for d in self.log_dir.iterdir() if d.is_dir()]

        total_deleted = 0
        for mod in modules:
            module_dir = self.log_dir / mod
            if module_dir.exists():
                deleted = self._cleanup_old_logs(module_dir, days_to_keep)
                total_deleted += deleted

        return total_deleted

    def _cleanup_old_logs(self, log_dir: Path, days_to_keep: int) -> int:
        """清理指定天数之前的日志文件，返回删除的文件数量"""
        deleted_count = 0
        try:
            current_time = datetime.datetime.now(timezone.utc)
            cutoff_time = current_time - datetime.timedelta(days=days_to_keep)

            for log_file in log_dir.glob("*.log"):
                try:
                    # 从文件名中提取日期
                    stem = log_file.stem
                    if '_' in stem and stem.startswith("20"):
                        date_str = stem.split('_')[0]
                        file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

                        if file_date < cutoff_time:
                            log_file.unlink()
                            deleted_count += 1
                            print(f"已删除旧日志文件: {log_file}")
                except (ValueError, IndexError):
                    continue
        except Exception as e:
            print(f"清理日志文件时出错: {e}")

        return deleted_count

# 全局日志管理器实例
log_manager = LogManager()