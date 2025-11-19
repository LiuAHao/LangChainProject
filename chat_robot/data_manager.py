from langchain_community.utilities import SQLDatabase
from typing import List, Dict, Any
import os
from .log_manager import log_manager

class DataManager:
    """数据库管理器，用于与MySQL数据库交互"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.database_url = os.getenv("MYSQL_URL", "mysql+pymysql://root:123456@localhost:3306/chat_robot")
        self.db = SQLDatabase.from_uri(self.database_url)
        # 记录数据库连接初始化
        log_manager.log_database_operation("system", "init", "connection", {"url": self.database_url}, "database")
    
    def get_connection(self):
        """获取数据库连接"""
        return self.db
    
    def create_tables(self):
        """创建必要的数据表"""
        # 先检查并更新现有表结构
        self._update_table_structure()
        
        create_ai_personas_table = """
        CREATE TABLE IF NOT EXISTS ai_personas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            description TEXT,
            system_prompt TEXT NOT NULL,
            avatar_url VARCHAR(500),
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """

        create_sessions_table = """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            title VARCHAR(255),
            persona_id INT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (persona_id) REFERENCES ai_personas(id) ON DELETE SET NULL
        )
        """

        create_messages_table = """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            role ENUM('system', 'user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            tokens_used INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
        )
        """

        create_summaries_table = """
        CREATE TABLE IF NOT EXISTS chat_summaries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            summary TEXT NOT NULL,
            message_count INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
        )
        """

        try:
            db = self.get_connection()
            # 记录数据库表创建操作
            log_manager.log_database_operation("system", "create_table", "ai_personas", {}, "database")
            db.run(create_ai_personas_table)
            log_manager.log_database_operation("system", "create_table", "chat_sessions", {}, "database")
            db.run(create_sessions_table)
            log_manager.log_database_operation("system", "create_table", "chat_messages", {}, "database")
            db.run(create_messages_table)
            log_manager.log_database_operation("system", "create_table", "chat_summaries", {}, "database")
            db.run(create_summaries_table)

            # 插入默认AI人设
            self._insert_default_personas()
            print("数据表创建成功")
            log_manager.log_database_operation("system", "success", "create_tables", {"status": "success"}, "database")
        except Exception as e:
            print(f"创建数据表时出错: {e}")
            log_manager.log_database_operation("system", "error", "create_tables", {"error": str(e)}, "database")
    
    def _update_table_structure(self):
        """更新现有表结构以匹配最新定义"""
        try:
            db = self.get_connection()
            
            # 检查并添加chat_sessions表缺失的字段
            try:
                # 添加title字段
                db.run("ALTER TABLE chat_sessions ADD COLUMN title VARCHAR(255)")
            except Exception:
                # 字段可能已存在
                pass
            
            try:
                # 添加persona_id字段
                db.run("ALTER TABLE chat_sessions ADD COLUMN persona_id INT")
                # 添加外键约束
                db.run("ALTER TABLE chat_sessions ADD CONSTRAINT fk_persona_id FOREIGN KEY (persona_id) REFERENCES ai_personas(id) ON DELETE SET NULL")
            except Exception:
                # 字段或约束可能已存在
                pass
                
            try:
                # 添加is_active字段
                db.run("ALTER TABLE chat_sessions ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            except Exception:
                # 字段可能已存在
                pass
                
            try:
                # 添加updated_at字段
                db.run("ALTER TABLE chat_sessions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            except Exception:
                # 字段可能已存在
                pass
                
        except Exception as e:
            print(f"更新表结构时出错: {e}")

    def _insert_default_personas(self):
        """插入默认的AI人设"""
        default_personas = [
            {
                "name": "通用助手",
                "description": "一个通用的AI助手，能够回答各种问题",
                "system_prompt": "你是一个有用的AI助手，请根据用户的问题提供准确、有用的回答。",
                "avatar_url": "/static/images/default-avatar.png",
                "is_default": True
            },
            {
                "name": "编程助手",
                "description": "专业的编程助手，擅长各种编程语言和技术问题",
                "system_prompt": "你是一个专业的编程助手，精通多种编程语言，包括Python、JavaScript、Java、C++等。请提供清晰的代码示例和技术解释。",
                "avatar_url": "/static/images/coding-avatar.png",
                "is_default": False
            },
            {
                "name": "写作助手",
                "description": "专业的写作助手，帮助改进文章和创意写作",
                "system_prompt": "你是一个专业的写作助手，擅长文章修改、创意写作、语法纠正和内容优化。请提供建设性的写作建议。",
                "avatar_url": "/static/images/writing-avatar.png",
                "is_default": False
            },
            {
                "name": "学习导师",
                "description": "耐心的学习导师，帮助解释复杂概念",
                "system_prompt": "你是一个耐心的学习导师，擅长用简单易懂的方式解释复杂的概念。请使用类比、例子和循序渐进的方法来帮助用户学习。",
                "avatar_url": "/static/images/tutor-avatar.png",
                "is_default": False
            }
        ]

        for persona in default_personas:
            # 检查人设是否已存在，避免重复插入
            check_query = "SELECT COUNT(*) as count FROM ai_personas WHERE name = '{}'".format(persona["name"].replace("'", "''"))
            try:
                db = self.get_connection()
                result = db.run(check_query)
                result_str = str(result)
                
                # 解析结果判断人设是否存在
                persona_exists = False
                if result_str.startswith("[(") and result_str.endswith(",)]"):
                    count_str = result_str[2:-3]
                    if count_str.isdigit() and int(count_str) > 0:
                        persona_exists = True
                elif result_str.startswith("[") and result_str.endswith("]"):
                    content = result_str[1:-1]
                    content = content.replace("(", "").replace(")", "").replace(",", "")
                    if content.strip().isdigit() and int(content.strip()) > 0:
                        persona_exists = True
                
                if not persona_exists:
                    self.save_persona(
                        persona["name"],
                        persona["description"],
                        persona["system_prompt"],
                        persona["avatar_url"],
                        persona["is_default"]
                    )
            except Exception as e:
                print(f"检查人设是否存在时出错: {e}")
                # 出错时仍然尝试插入，让save_persona方法处理重复键错误
                self.save_persona(
                    persona["name"],
                    persona["description"],
                    persona["system_prompt"],
                    persona["avatar_url"],
                    persona["is_default"]
                )
    
    def save_persona(self, name: str, description: str, system_prompt: str,
                     avatar_url: str | None = None, is_default: bool = False) -> int:
        """保存AI人设"""
        insert_persona_query = """
        INSERT INTO ai_personas (name, description, system_prompt, avatar_url, is_default)
        VALUES ('{}', '{}', '{}', '{}', {})
        """.format(
            name.replace("'", "''"),
            description.replace("'", "''") if description else "",
            system_prompt.replace("'", "''"),
            avatar_url.replace("'", "''") if avatar_url else "",
            "TRUE" if is_default else "FALSE"
        )

        try:
            db = self.get_connection()
            db.run(insert_persona_query)
            # 记录数据库操作
            log_manager.log_database_operation("system", "insert", "ai_personas", {
                "name": name,
                "is_default": is_default
            }, "database")
            return 1
        except Exception as e:
            print(f"保存人设时出错: {e}")
            log_manager.log_database_operation("system", "error", "ai_personas", {
                "operation": "insert",
                "name": name,
                "error": str(e)
            }, "database")
            return 0

    def get_all_personas(self) -> List[Dict[str, Any]]:
        """获取所有AI人设"""
        select_personas_query = """
        SELECT id, name, description, system_prompt, avatar_url, is_default, created_at
        FROM ai_personas
        ORDER BY is_default DESC, name ASC
        """

        try:
            db = self.get_connection()
            result = db.run(select_personas_query)
            personas = []

            result_str = str(result)
            if result_str.startswith("[") and result_str.endswith("]"):
                content = result_str[1:-1]
                tuples = content.split("), (")
                for tuple_str in tuples:
                    tuple_str = tuple_str.replace("(", "").replace(")", "")
                    parts = tuple_str.split(", ", 5)
                    if len(parts) >= 6:
                        personas.append({
                            "id": int(parts[0].strip("'")) if parts[0].strip("'").isdigit() else 0,
                            "name": parts[1].strip("'"),
                            "description": parts[2].strip("'"),
                            "system_prompt": parts[3].strip("'"),
                            "avatar_url": parts[4].strip("'"),
                            "is_default": parts[5].strip("'").lower() == "true",
                            "created_at": parts[6].strip("'") if len(parts) > 6 else ""
                        })

            return personas
        except Exception as e:
            print(f"获取人设列表时出错: {e}")
            return []

    def get_persona_by_id(self, persona_id: int) -> Dict[str, Any]:
        """根据ID获取AI人设"""
        select_persona_query = """
        SELECT id, name, description, system_prompt, avatar_url, is_default
        FROM ai_personas
        WHERE id = {}
        """.format(persona_id)

        try:
            db = self.get_connection()
            result = db.run(select_persona_query)
            result_str = str(result)

            if result_str.startswith("[") and result_str.endswith("]"):
                content = result_str[1:-1]
                if content:
                    parts = content.split(", ", 5)
                    if len(parts) >= 6:
                        return {
                            "id": int(parts[0].strip("'")) if parts[0].strip("'").isdigit() else 0,
                            "name": parts[1].strip("'"),
                            "description": parts[2].strip("'"),
                            "system_prompt": parts[3].strip("'"),
                            "avatar_url": parts[4].strip("'"),
                            "is_default": parts[5].strip("'").lower() == "true"
                        }

            return {}
        except Exception as e:
            print(f"获取人设时出错: {e}")
            return {}

    def save_session(self, session_id: str, title: str | None = None, persona_id: int | None = None):
        """保存新的聊天会话"""
        # 首先检查会话是否已存在
        check_session_query = "SELECT COUNT(*) as count FROM chat_sessions WHERE session_id = '{}'".format(session_id)
        
        try:
            db = self.get_connection()
            result = db.run(check_session_query)
            
            # 解析结果判断会话是否存在
            session_exists = False
            result_str = str(result)
            if result_str.startswith("[(") and result_str.endswith(",)]"):
                count_str = result_str[2:-3]
                if count_str.isdigit() and int(count_str) > 0:
                    session_exists = True
            elif result_str.startswith("[") and result_str.endswith("]"):
                content = result_str[1:-1]
                content = content.replace("(", "").replace(")", "").replace(",", "")
                if content.strip().isdigit() and int(content.strip()) > 0:
                    session_exists = True
            
            if session_exists:
                # 如果会话已存在，更新会话信息而不是插入
                log_manager.log_database_operation(session_id, "update", "chat_sessions", {
                    "title": title,
                    "persona_id": persona_id
                }, "database")
                return self.update_session(session_id, title, persona_id)
            else:
                # 如果会话不存在，插入新会话
                insert_session_query = """
                INSERT INTO chat_sessions (session_id, title, persona_id)
                VALUES ('{}', '{}', {})
                """.format(
                    session_id,
                    title.replace("'", "''") if title else "新对话",
                    persona_id if persona_id else "NULL"
                )
                db.run(insert_session_query)
                # 记录数据库操作
                log_manager.log_database_operation(session_id, "insert", "chat_sessions", {
                    "title": title,
                    "persona_id": persona_id
                }, "database")
                return True
        except Exception as e:
            print(f"保存会话时出错: {e}")
            log_manager.log_database_operation(session_id, "error", "chat_sessions", {
                "operation": "save_session",
                "error": str(e)
            }, "database")
            return False

    def update_session(self, session_id: str, title: str | None = None, persona_id: int | None = None):
        """更新会话信息"""
        updates = []
        if title is not None:
            escaped_title = title.replace("'", "''")
            updates.append(f"title = '{escaped_title}'")
        if persona_id is not None:
            updates.append(f"persona_id = {persona_id if persona_id > 0 else 'NULL'}")

        if not updates:
            return False

        update_session_query = """
        UPDATE chat_sessions
        SET {}
        WHERE session_id = '{}'
        """.format(", ".join(updates), session_id)

        try:
            db = self.get_connection()
            db.run(update_session_query)
            # 记录数据库操作
            log_manager.log_database_operation(session_id, "update", "chat_sessions", {
                "updates": updates
            }, "database")
            return True
        except Exception as e:
            print(f"更新会话时出错: {e}")
            log_manager.log_database_operation(session_id, "error", "chat_sessions", {
                "operation": "update_session",
                "error": str(e)
            }, "database")
            return False

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """获取所有会话"""
        select_sessions_query = """
        SELECT s.session_id, s.title, s.persona_id, s.is_active, s.created_at, s.updated_at,
               p.name as persona_name
        FROM chat_sessions s
        LEFT JOIN ai_personas p ON s.persona_id = p.id
        ORDER BY s.updated_at DESC
        """

        try:
            db = self.get_connection()
            result = db.run(select_sessions_query)
            sessions = []

            # 调试输出
            print(f"数据库查询结果: {result}")
            print(f"结果类型: {type(result)}")

            # 处理查询结果
            if result:
                # 尝试不同的解析方式
                try:
                    # 方式1：如果结果是字符串，需要解析
                    result_str = str(result)
                    print(f"结果字符串: {result_str}")

                    if result_str.startswith("[") and result_str.endswith("]"):
                        content = result_str[1:-1].strip()
                        if content:
                            # 分割行
                            rows = content.split("), (")
                            for row_str in rows:
                                row_str = row_str.replace("(", "").replace(")", "")
                                parts = row_str.split(", ", 6)

                                if len(parts) >= 7:
                                    session_id = parts[0].strip("'").strip()
                                    title = parts[1].strip("'").strip()
                                    persona_id = parts[2].strip("'").strip()
                                    is_active = parts[3].strip("'").strip()
                                    created_at = parts[4].strip("'").strip()
                                    updated_at = parts[5].strip("'").strip()
                                    persona_name = parts[6].strip("'").strip() if len(parts) > 6 else None

                                    sessions.append({
                                        "session_id": session_id,
                                        "title": title if title else "新对话",
                                        "persona_id": int(persona_id) if persona_id and persona_id.isdigit() else None,
                                        "is_active": is_active.lower() == "true" if is_active else False,
                                        "created_at": created_at,
                                        "updated_at": updated_at,
                                        "persona_name": persona_name if persona_name else "通用助手"
                                    })
                except Exception as parse_error:
                    print(f"字符串解析失败: {parse_error}")
                    # 方式2：尝试直接迭代结果
                    try:
                        for row in result:
                            if len(row) >= 7:
                                sessions.append({
                                    "session_id": str(row[0]) if row[0] else None,
                                    "title": str(row[1]) if row[1] else "新对话",
                                    "persona_id": int(row[2]) if row[2] is not None else None,
                                    "is_active": bool(row[3]) if row[3] is not None else False,
                                    "created_at": str(row[4]) if row[4] else None,
                                    "updated_at": str(row[5]) if row[5] else None,
                                    "persona_name": str(row[6]) if len(row) > 6 and row[6] else "通用助手"
                                })
                    except Exception as iter_error:
                        print(f"迭代解析失败: {iter_error}")

            print(f"最终会话数据: {sessions}")
            return sessions
        except Exception as e:
            print(f"获取会话列表时出错: {e}")
            log_manager.log_database_operation("system", "error", "chat_sessions", {
                "operation": "get_all_sessions",
                "error": str(e)
            }, "database")
            return []

    def delete_session(self, session_id: str) -> bool:
        """删除会话及其所有消息"""
        try:
            db = self.get_connection()
            # 由于外键约束，删除会话会自动删除相关消息
            delete_session_query = "DELETE FROM chat_sessions WHERE session_id = '{}'".format(session_id)
            db.run(delete_session_query)
            return True
        except Exception as e:
            print(f"删除会话时出错: {e}")
            return False
    
    def clear_session_messages(self, session_id: str) -> bool:
        """清空会话的所有消息"""
        try:
            db = self.get_connection()
            clear_messages_query = "DELETE FROM chat_messages WHERE session_id = '{}'".format(session_id)
            db.run(clear_messages_query)
            return True
        except Exception as e:
            print(f"清空会话消息时出错: {e}")
            return False
    
    def save_summary(self, session_id: str, summary: str, message_count: int):
        """保存聊天摘要"""
        insert_summary_query = """
        INSERT INTO chat_summaries (session_id, summary, message_count)
        VALUES ('{}', '{}', {})
        """.format(
            session_id,
            summary.replace("'", "''"),
            message_count
        )

        try:
            db = self.get_connection()
            db.run(insert_summary_query)
            # 记录数据库操作
            log_manager.log_database_operation(session_id, "insert", "chat_summaries", {
                "message_count": message_count,
                "summary_length": len(summary)
            }, "database")
            return True
        except Exception as e:
            print(f"保存摘要时出错: {e}")
            log_manager.log_database_operation(session_id, "error", "chat_summaries", {
                "operation": "save_summary",
                "message_count": message_count,
                "error": str(e)
            }, "database")
            return False

    def get_recent_summary(self, session_id: str) -> str:
        """获取最近的摘要"""
        select_summary_query = """
        SELECT summary
        FROM chat_summaries
        WHERE session_id = '{}'
        ORDER BY created_at DESC
        LIMIT 1
        """.format(session_id)

        try:
            db = self.get_connection()
            result = db.run(select_summary_query)
            result_str = str(result)

            if result_str.startswith("[") and result_str.endswith("]"):
                content = result_str[1:-1]  # 移除方括号
                if content:
                    # 处理可能的引号
                    content = content.strip().strip("'").strip('"')
                    if content and content != "None":
                        return content

            return ""
        except Exception as e:
            print(f"获取摘要时出错: {e}")
            return ""
    
    def save_message(self, session_id: str, role: str, content: str):
        """保存聊天消息"""
        # 确保会话存在
        self.save_session(session_id)
        
        insert_message_query = """
        INSERT INTO chat_messages (session_id, role, content) 
        VALUES ('{}', '{}', '{}')
        """.format(session_id, role, content.replace("'", "''"))
        
        try:
            db = self.get_connection()
            db.run(insert_message_query)
            # 记录数据库操作
            log_manager.log_database_operation(session_id, "insert", "chat_messages", {
                "role": role,
                "content_length": len(content)
            }, "database")
            # 注意：这里无法获取lastrowid，所以我们返回一个默认值
            return 1
        except Exception as e:
            print(f"保存消息时出错: {e}")
            log_manager.log_database_operation(session_id, "error", "chat_messages", {
                "operation": "save_message",
                "role": role,
                "error": str(e)
            }, "database")
            return None
    
    def get_recent_messages(self, session_id: str, limit: int = 2) -> List[Dict[str, str]]:
        """获取最近的聊天记录"""
        select_messages_query = """
        SELECT role, content 
        FROM chat_messages 
        WHERE session_id = '{}' 
        ORDER BY created_at DESC 
        LIMIT {}
        """.format(session_id, limit)
        
        try:
            db = self.get_connection()
            # 使用SQLDatabase的run方法执行查询
            result = db.run(select_messages_query)
            # 解析结果
            messages = []
            
            # 处理返回格式 "[('user', '测试消息1'), ('assistant', '回复消息1')]"
            result_str = str(result)
            if result_str.startswith("[") and result_str.endswith("]"):
                # 移除方括号
                content = result_str[1:-1]
                # 分割元组
                tuples = content.split("), (")
                for tuple_str in tuples:
                    # 清理元组字符串
                    tuple_str = tuple_str.replace("(", "").replace(")", "")
                    # 分割角色和内容
                    parts = tuple_str.split(", ", 1)
                    if len(parts) == 2:
                        role = parts[0].strip("'")
                        content = parts[1].strip("'")
                        messages.append({"role": role, "content": content})
            
            # 按时间顺序排列（从旧到新）
            messages.reverse()
            return messages
        except Exception as e:
            print(f"获取聊天记录时出错: {e}")
            return []
    
    def get_history_messages(self, session_id: str, limit: int = 100) -> List[Dict[str, str]]:
        """获取历史聊天记录（用于摘要）"""
        select_messages_query = """
        SELECT role, content 
        FROM chat_messages 
        WHERE session_id = '{}' 
        ORDER BY created_at ASC 
        LIMIT {}
        """.format(session_id, limit)
        
        try:
            db = self.get_connection()
            # 使用SQLDatabase的run方法执行查询
            result = db.run(select_messages_query)
            # 解析结果
            messages = []
            
            # 处理返回格式 "[('user', '测试消息1'), ('assistant', '回复消息1')]"
            result_str = str(result)
            if result_str.startswith("[") and result_str.endswith("]"):
                # 移除方括号
                content = result_str[1:-1]
                # 分割元组
                tuples = content.split("), (")
                for tuple_str in tuples:
                    # 清理元组字符串
                    tuple_str = tuple_str.replace("(", "").replace(")", "")
                    # 分割角色和内容
                    parts = tuple_str.split(", ", 1)
                    if len(parts) == 2:
                        role = parts[0].strip("'")
                        content = parts[1].strip("'")
                        messages.append({"role": role, "content": content})
            return messages
        except Exception as e:
            print(f"获取历史聊天记录时出错: {e}")
            return []
    
    def get_message_count(self, session_id: str) -> int:
        """获取会话中的消息总数"""
        count_query = "SELECT COUNT(*) as count FROM chat_messages WHERE session_id = '{}'".format(session_id)
        
        try:
            db = self.get_connection()
            # 使用SQLDatabase的run方法执行查询
            result = db.run(count_query)
            # 解析结果
            result_str = str(result)
            
            # 处理返回格式 '[(4,)]'
            if result_str.startswith("[(") and result_str.endswith(",)]"):
                # 提取数字
                count_str = result_str[2:-3]  # 移除 '[(" 和 ",)]'
                if count_str.isdigit():
                    return int(count_str)
            
            # 处理其他可能的格式
            if result_str.startswith("[") and result_str.endswith("]"):
                content = result_str[1:-1]
                # 移除括号和逗号
                content = content.replace("(", "").replace(")", "").replace(",", "")
                if content.strip().isdigit():
                    return int(content.strip())
            
            # 如果以上方法都不行，返回0
            return 0
        except Exception as e:
            print(f"获取消息计数时出错: {e}")
            return 0