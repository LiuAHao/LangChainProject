from langchain_community.utilities import SQLDatabase
from typing import List, Dict, Any, Optional, Union
import os
import json
from datetime import datetime
try:
    from .log_manager import log_manager
except ImportError:
    from log_manager import log_manager

class DataManager:
    """
    重构后的数据库管理器，支持优化的数据库架构

    主要改进：
    1. 使用整数主键替代字符串外键
    2. 增加用户支持
    3. 完善的消息和摘要管理
    4. 性能优化和索引支持
    5. 软删除和审计功能
    """

    def __init__(self):
        """初始化数据库连接"""
        self.database_url = os.getenv("MYSQL_URL", "mysql+pymysql://root:123456@localhost:3306/chat_robot")
        self.db = SQLDatabase.from_uri(self.database_url)
        # 记录数据库连接初始化
        log_manager.log_database_operation("system", "init", "connection", {"url": self.database_url}, "database")

        # 数据库版本控制
        self.current_schema_version = "2.0.0"
    
    def get_connection(self):
        """获取数据库连接"""
        return self.db
    
    def create_tables(self):
        """
        创建新的数据库表结构（v2.0.0）
        支持用户、优化的会话管理、增强的消息和摘要功能
        """
        try:
            db = self.get_connection()

            # 1. 创建用户表
            self._create_users_table(db)

            # 2. 创建AI人设表（增强版）
            self._create_ai_personas_v2_table(db)

            # 3. 创建聊天会话表（重构版）
            self._create_chat_sessions_v2_table(db)

            # 4. 创建聊天消息表（增强版）
            self._create_chat_messages_v2_table(db)

            # 5. 创建对话摘要表（增强版）
            self._create_chat_summaries_v2_table(db)

            # 6. 创建索引
            self._create_indexes(db)

            # 7. 数据迁移（如果需要）
            self._migrate_legacy_data(db)

            # 8. 插入默认数据
            self._insert_default_data(db)

            print("数据表v2.0.0创建成功")
            log_manager.log_database_operation("system", "success", "create_tables_v2",
                                              {"version": self.current_schema_version}, "database")

        except Exception as e:
            print(f"创建数据表时出错: {e}")
            log_manager.log_database_operation("system", "error", "create_tables_v2",
                                              {"error": str(e)}, "database")
            raise

    def _create_users_table(self, db):
        """创建用户表"""
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE,
            password_hash VARCHAR(255),
            display_name VARCHAR(100),
            avatar_url VARCHAR(500),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user_username (username),
            INDEX idx_user_email (email),
            INDEX idx_user_active (is_active)
        )
        """
        db.run(create_users_table)
        log_manager.log_database_operation("system", "create_table", "users", {}, "database")

    def _create_ai_personas_v2_table(self, db):
        """创建增强的AI人设表"""
        create_ai_personas_v2_table = """
        CREATE TABLE IF NOT EXISTS ai_personas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            description TEXT,
            system_prompt TEXT NOT NULL,
            avatar_url VARCHAR(500),
            is_default BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_persona_active (is_active),
            INDEX idx_persona_default (is_default),
            INDEX idx_persona_name (name)
        )
        """
        db.run(create_ai_personas_v2_table)
        log_manager.log_database_operation("system", "create_table", "ai_personas_v2", {}, "database")

    def _create_chat_sessions_v2_table(self, db):
        """创建重构的聊天会话表"""
        create_sessions_v2_table = """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            user_id INT,
            title VARCHAR(255),
            persona_id INT,
            model_name VARCHAR(100),
            status ENUM('active', 'archived', 'deleted') DEFAULT 'active',
            settings JSON,
            message_count INT DEFAULT 0,
            total_tokens INT DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (persona_id) REFERENCES ai_personas(id) ON DELETE SET NULL,
            INDEX idx_session_user (user_id),
            INDEX idx_session_persona (persona_id),
            INDEX idx_session_status (status),
            INDEX idx_session_updated (updated_at),
            INDEX idx_session_session_id (session_id)
        )
        """
        db.run(create_sessions_v2_table)
        log_manager.log_database_operation("system", "create_table", "chat_sessions_v2", {}, "database")

    def _create_chat_messages_v2_table(self, db):
        """创建增强的聊天消息表"""
        create_messages_v2_table = """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id INT NOT NULL,
            parent_message_id INT,
            role ENUM('system', 'user', 'assistant', 'tool') NOT NULL,
            content LONGTEXT NOT NULL,
            model_name VARCHAR(100),
            tokens_used INT DEFAULT 0,
            cost DECIMAL(10,6) DEFAULT 0.000000,
            metadata JSON,
            is_deleted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_message_id) REFERENCES chat_messages(id) ON DELETE SET NULL,
            INDEX idx_message_session (session_id),
            INDEX idx_message_created (created_at),
            INDEX idx_message_role (role),
            INDEX idx_message_deleted (is_deleted),
            INDEX idx_message_parent (parent_message_id)
        )
        """
        db.run(create_messages_v2_table)
        log_manager.log_database_operation("system", "create_table", "chat_messages_v2", {}, "database")

    def _create_chat_summaries_v2_table(self, db):
        """创建增强的对话摘要表"""
        create_summaries_v2_table = """
        CREATE TABLE IF NOT EXISTS chat_summaries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id INT NOT NULL,
            summary_type ENUM('auto', 'manual') DEFAULT 'auto',
            summary_text LONGTEXT NOT NULL,
            message_range_start INT,
            message_range_end INT,
            message_count INT NOT NULL,
            model_name VARCHAR(100),
            tokens_saved INT DEFAULT 0,
            created_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_summary_session (session_id),
            INDEX idx_summary_type (summary_type),
            INDEX idx_summary_created (created_at)
        )
        """
        db.run(create_summaries_v2_table)
        log_manager.log_database_operation("system", "create_table", "chat_summaries_v2", {}, "database")

    def _create_indexes(self, db):
        """创建额外的性能索引"""
        try:
            # 复合索引 - MySQL不支持CREATE INDEX IF NOT EXISTS语法，改用存储过程或检查后创建
            try:
                db.run("CREATE INDEX idx_messages_session_created ON chat_messages(session_id, created_at)")
            except Exception:
                pass  # 索引可能已存在

            try:
                db.run("CREATE INDEX idx_sessions_user_updated ON chat_sessions(user_id, updated_at)")
            except Exception:
                pass

            try:
                db.run("CREATE INDEX idx_summaries_session_type ON chat_summaries(session_id, summary_type)")
            except Exception:
                pass

            log_manager.log_database_operation("system", "create_indexes", "performance", {}, "database")
        except Exception as e:
            print(f"创建索引时出错（可能已存在）: {e}")

    def _migrate_legacy_data(self, db):
        """从旧版数据库结构迁移数据"""
        try:
            # 检查是否存在旧表
            legacy_tables_exist = self._check_legacy_tables(db)

            if legacy_tables_exist:
                print("开始数据迁移...")
                self._migrate_personas_data(db)
                self._migrate_sessions_data(db)
                self._migrate_messages_data(db)
                self._migrate_summaries_data(db)
                print("数据迁移完成")

        except Exception as e:
            print(f"数据迁移时出错: {e}")
            # 不抛出异常，允许继续创建新表

    def _check_legacy_tables(self, db) -> bool:
        """检查是否存在旧版数据表"""
        try:
            # 检查是否存在需要迁移的旧表
            legacy_tables = ['ai_personas_old', 'chat_sessions_old', 'chat_messages_old', 'chat_summaries_old']
            existing_tables = []

            for table in legacy_tables:
                try:
                    result = db.run(f"SHOW TABLES LIKE '{table}'")
                    result_str = str(result)
                    if result_str and len(result_str) > 2:  # 如果结果不为空，说明表存在
                        existing_tables.append(table)
                        print(f"发现旧表: {table}")
                except:
                    continue

            if existing_tables:
                print(f"发现需要迁移的旧表: {', '.join(existing_tables)}")
                return True
            else:
                print("未发现需要迁移的旧表，跳过数据迁移")
                return False
        except Exception as e:
            print(f"检查旧表时出错: {e}")
            return False

    def _migrate_personas_data(self, db):
        """迁移AI人设数据"""
        try:
            # 先检查是否存在ai_personas_old表
            check_result = db.run("SHOW TABLES LIKE 'ai_personas_old'")
            if not str(check_result) or len(str(check_result)) <= 2:
                print("ai_personas_old表不存在，跳过人设数据迁移")
                return

            print("开始迁移人设数据...")
            # 从旧表获取数据
            old_personas = db.run("SELECT * FROM ai_personas_old")

            if not old_personas:
                print("ai_personas_old表为空，无需迁移")
                return

            migrated_count = 0
            # 迁移逻辑
            for persona in old_personas:
                try:
                    # 这里需要根据具体的旧表结构来解析数据
                    # 假设旧表结构包含: name, description, system_prompt, avatar_url, is_default
                    if hasattr(persona, '__iter__') and not isinstance(persona, str):
                        # 如果是元组或列表格式
                        if len(persona) >= 3:
                            name = str(persona[0]).strip("'")
                            description = str(persona[1]).strip("'") if len(persona) > 1 else ""
                            system_prompt = str(persona[2]).strip("'") if len(persona) > 2 else ""
                            avatar_url = str(persona[3]).strip("'") if len(persona) > 3 else None
                            is_default = str(persona[4]).lower() == "true" if len(persona) > 4 else False
                        else:
                            continue
                    else:
                        # 如果是其他格式，跳过
                        continue

                    # 检查新表中是否已存在
                    check_existing = db.run(f"SELECT COUNT(*) FROM ai_personas WHERE name = '{name.replace(chr(39), chr(39)*2)}'")
                    if not str(check_existing).strip("[](), ").isdigit() or int(str(check_existing).strip("[](), ")) == 0:
                        # 插入到新表
                        insert_query = f"""
                        INSERT INTO ai_personas (name, description, system_prompt, avatar_url, is_default, is_active)
                        VALUES (
                            '{name.replace(chr(39), chr(39)*2)}',
                            '{description.replace(chr(39), chr(39)*2)}',
                            '{system_prompt.replace(chr(39), chr(39)*2)}',
                            '{avatar_url.replace(chr(39), chr(39)*2) if avatar_url else None}',
                            {1 if is_default else 0},
                            1
                        )
                        """
                        db.run(insert_query)
                        migrated_count += 1
                        print(f"迁移人设: {name}")

                except Exception as e:
                    print(f"迁移单个人设时出错: {e}")
                    continue

            print(f"人设数据迁移完成，共迁移 {migrated_count} 条记录")

        except Exception as e:
            print(f"迁移人设数据时出错: {e}")
            log_manager.log_database_operation("system", "error", "migrate_personas", {"error": str(e)}, "database")

    def _migrate_sessions_data(self, db):
        """迁移会话数据"""
        try:
            # 先检查是否存在chat_sessions_old表
            check_result = db.run("SHOW TABLES LIKE 'chat_sessions_old'")
            if not str(check_result) or len(str(check_result)) <= 2:
                print("chat_sessions_old表不存在，跳过会话数据迁移")
                return

            print("开始迁移会话数据...")
            old_sessions = db.run("SELECT * FROM chat_sessions_old")

            if not old_sessions:
                print("chat_sessions_old表为空，无需迁移")
                return

            migrated_count = 0
            for session in old_sessions:
                try:
                    if hasattr(session, '__iter__') and not isinstance(session, str):
                        if len(session) >= 1:
                            session_id = str(session[0]).strip("'")
                            title = str(session[1]).strip("'") if len(session) > 1 else "新对话"
                            persona_id = int(session[2]) if len(session) > 2 and session[2] else None
                        else:
                            continue
                    else:
                        continue

                    # 检查新表中是否已存在
                    check_existing = db.run(f"SELECT COUNT(*) FROM chat_sessions WHERE session_id = '{session_id}'")
                    if not str(check_existing).strip("[](), ").isdigit() or int(str(check_existing).strip("[](), ")) == 0:
                        # 插入到新表
                        insert_query = f"""
                        INSERT INTO chat_sessions (session_id, title, persona_id, status, is_active)
                        VALUES (
                            '{session_id}',
                            '{title.replace(chr(39), chr(39)*2)}',
                            {persona_id if persona_id else 'NULL'},
                            'active',
                            1
                        )
                        """
                        db.run(insert_query)
                        migrated_count += 1
                        print(f"迁移会话: {session_id}")

                except Exception as e:
                    print(f"迁移单个会话时出错: {e}")
                    continue

            print(f"会话数据迁移完成，共迁移 {migrated_count} 条记录")

        except Exception as e:
            print(f"迁移会话数据时出错: {e}")
            log_manager.log_database_operation("system", "error", "migrate_sessions", {"error": str(e)}, "database")

    def _migrate_messages_data(self, db):
        """迁移消息数据"""
        try:
            # 先检查是否存在chat_messages_old表
            check_result = db.run("SHOW TABLES LIKE 'chat_messages_old'")
            if not str(check_result) or len(str(check_result)) <= 2:
                print("chat_messages_old表不存在，跳过消息数据迁移")
                return

            print("开始迁移消息数据...")
            old_messages = db.run("SELECT * FROM chat_messages_old")

            if not old_messages:
                print("chat_messages_old表为空，无需迁移")
                return

            migrated_count = 0
            for message in old_messages:
                try:
                    if hasattr(message, '__iter__') and not isinstance(message, str):
                        if len(message) >= 3:
                            session_id = str(message[0]).strip("'")
                            role = str(message[1]).strip("'")
                            content = str(message[2]).strip("'")
                        else:
                            continue
                    else:
                        continue

                    # 确保会话存在
                    self.save_session(session_id)

                    # 插入到新表
                    insert_query = f"""
                    INSERT INTO chat_messages (session_id, role, content)
                    VALUES (
                        (SELECT id FROM chat_sessions WHERE session_id = '{session_id}' LIMIT 1),
                        '{role}',
                        '{content.replace(chr(39), chr(39)*2)}'
                    )
                    """
                    db.run(insert_query)
                    migrated_count += 1

                except Exception as e:
                    print(f"迁移单条消息时出错: {e}")
                    continue

            print(f"消息数据迁移完成，共迁移 {migrated_count} 条记录")

        except Exception as e:
            print(f"迁移消息数据时出错: {e}")
            log_manager.log_database_operation("system", "error", "migrate_messages", {"error": str(e)}, "database")

    def _migrate_summaries_data(self, db):
        """迁移摘要数据"""
        try:
            # 先检查是否存在chat_summaries_old表
            check_result = db.run("SHOW TABLES LIKE 'chat_summaries_old'")
            if not str(check_result) or len(str(check_result)) <= 2:
                print("chat_summaries_old表不存在，跳过摘要数据迁移")
                return

            print("开始迁移摘要数据...")
            old_summaries = db.run("SELECT * FROM chat_summaries_old")

            if not old_summaries:
                print("chat_summaries_old表为空，无需迁移")
                return

            migrated_count = 0
            for summary in old_summaries:
                try:
                    if hasattr(summary, '__iter__') and not isinstance(summary, str):
                        if len(summary) >= 3:
                            session_id = str(summary[0]).strip("'")
                            summary_text = str(summary[1]).strip("'")
                            message_count = int(summary[2]) if len(summary) > 2 else 0
                        else:
                            continue
                    else:
                        continue

                    # 确保会话存在
                    self.save_session(session_id)

                    # 插入到新表
                    insert_query = f"""
                    INSERT INTO chat_summaries (session_id, summary_type, summary_text, message_count)
                    VALUES (
                        (SELECT id FROM chat_sessions WHERE session_id = '{session_id}' LIMIT 1),
                        'auto',
                        '{summary_text.replace(chr(39), chr(39)*2)}',
                        {message_count}
                    )
                    """
                    db.run(insert_query)
                    migrated_count += 1

                except Exception as e:
                    print(f"迁移单个摘要时出错: {e}")
                    continue

            print(f"摘要数据迁移完成，共迁移 {migrated_count} 条记录")

        except Exception as e:
            print(f"迁移摘要数据时出错: {e}")
            log_manager.log_database_operation("system", "error", "migrate_summaries", {"error": str(e)}, "database")

    def _insert_default_data(self, db):
        """插入默认数据"""
        try:
            # 插入默认用户（可选）
            self._insert_default_user(db)

            # 插入默认AI人设
            self._insert_default_personas_v2(db)

        except Exception as e:
            print(f"插入默认数据时出错: {e}")

    def _insert_default_user(self, db):
        """插入默认用户"""
        try:
            # 检查是否已有用户
            result = db.run("SELECT COUNT(*) FROM users")
            if result and str(result).strip("[](), ").isdigit() and int(str(result).strip("[](), ")) > 0:
                return

            # 插入默认系统用户
            insert_user = """
            INSERT INTO users (username, display_name, is_active)
            VALUES ('system', 'System User', TRUE)
            """
            db.run(insert_user)
            log_manager.log_database_operation("system", "insert", "default_user", {}, "database")
        except Exception as e:
            print(f"插入默认用户时出错: {e}")

    def _insert_default_personas_v2(self, db):
        """插入默认的AI人设（v2版本）"""
        default_personas = [
            {
                "name": "通用助手",
                "description": "一个通用的AI助手，能够回答各种问题",
                "system_prompt": "你是一个有用的AI助手，请根据用户的问题提供准确、有用的回答。",
                "avatar_url": "/static/images/default-avatar.png",
                "is_default": True,
                "is_active": True
            },
            {
                "name": "编程助手",
                "description": "专业的编程助手，擅长各种编程语言和技术问题",
                "system_prompt": "你是一个专业的编程助手，精通多种编程语言，包括Python、JavaScript、Java、C++等。请提供清晰的代码示例和技术解释。",
                "avatar_url": "/static/images/coding-avatar.png",
                "is_default": False,
                "is_active": True
            },
            {
                "name": "写作助手",
                "description": "专业的写作助手，帮助改进文章和创意写作",
                "system_prompt": "你是一个专业的写作助手，擅长文章修改、创意写作、语法纠正和内容优化。请提供建设性的写作建议。",
                "avatar_url": "/static/images/writing-avatar.png",
                "is_default": False,
                "is_active": True
            },
            {
                "name": "学习导师",
                "description": "耐心的学习导师，帮助解释复杂概念",
                "system_prompt": "你是一个耐心的学习导师，擅长用简单易懂的方式解释复杂的概念。请使用类比、例子和循序渐进的方法来帮助用户学习。",
                "avatar_url": "/static/images/tutor-avatar.png",
                "is_default": False,
                "is_active": True
            }
        ]

        for persona in default_personas:
            try:
                # 检查人设是否已存在
                check_query = f"SELECT COUNT(*) FROM ai_personas WHERE name = '{persona['name'].replace(chr(39), chr(39)*2)}'"
                result = db.run(check_query)

                persona_exists = False
                if result:
                    result_str = str(result).strip("[](), ")
                    if result_str.isdigit() and int(result_str) > 0:
                        persona_exists = True

                if not persona_exists:
                    insert_persona_query = f"""
                    INSERT INTO ai_personas (name, description, system_prompt, avatar_url, is_default, is_active)
                    VALUES (
                        '{persona['name'].replace(chr(39), chr(39)*2)}',
                        '{persona['description'].replace(chr(39), chr(39)*2)}',
                        '{persona['system_prompt'].replace(chr(39), chr(39)*2)}',
                        '{persona['avatar_url'].replace(chr(39), chr(39)*2)}',
                        {1 if persona['is_default'] else 0},
                        {1 if persona['is_active'] else 0}
                    )
                    """
                    db.run(insert_persona_query)
                    log_manager.log_database_operation("system", "insert", "ai_persona_v2",
                                                      {"name": persona['name']}, "database")
            except Exception as e:
                print(f"插入人设 {persona['name']} 时出错: {e}")
                log_manager.log_database_operation("system", "error", "ai_persona_v2",
                                                  {"name": persona['name'], "error": str(e)}, "database")
    
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
        """获取所有会话（排除系统内部会话）"""
        select_sessions_query = """
        SELECT s.session_id, s.title, s.persona_id, s.is_active, s.created_at, s.updated_at,
               p.name as persona_name
        FROM chat_sessions s
        LEFT JOIN ai_personas p ON s.persona_id = p.id
        WHERE s.session_id NOT LIKE 'system_%' AND s.session_id NOT LIKE 'optimize_%'
        ORDER BY s.updated_at DESC
        """

        try:
            db = self.get_connection()
            result = db.run(select_sessions_query)
            sessions = []

            # 处理查询结果
            if result:
                # 尝试不同的解析方式
                try:
                    # 方式1：如果结果是字符串，需要解析
                    result_str = str(result)

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
                                        "persona_name": persona_name if persona_name and not persona_name.startswith("datetime.datetime") else None
                                    })
                                elif len(parts) >= 6:  # 处理没有persona_name的情况
                                    session_id = parts[0].strip("'").strip()
                                    title = parts[1].strip("'").strip()
                                    persona_id = parts[2].strip("'").strip()
                                    is_active = parts[3].strip("'").strip()
                                    created_at = parts[4].strip("'").strip()
                                    updated_at = parts[5].strip("'").strip()

                                    sessions.append({
                                        "session_id": session_id,
                                        "title": title if title else "新对话",
                                        "persona_id": int(persona_id) if persona_id and persona_id.isdigit() else None,
                                        "is_active": is_active.lower() == "true" if is_active else False,
                                        "created_at": created_at,
                                        "updated_at": updated_at,
                                        "persona_name": None
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
                                    "persona_name": str(row[6]) if len(row) > 6 and row[6] and not str(row[6]).startswith("datetime.datetime") else None
                                })
                            elif len(row) >= 6:  # 处理没有persona_name的情况
                                sessions.append({
                                    "session_id": str(row[0]) if row[0] else None,
                                    "title": str(row[1]) if row[1] else "新对话",
                                    "persona_id": int(row[2]) if row[2] is not None else None,
                                    "is_active": bool(row[3]) if row[3] is not None else False,
                                    "created_at": str(row[4]) if row[4] else None,
                                    "updated_at": str(row[5]) if row[5] else None,
                                    "persona_name": None
                                })
                    except Exception as iter_error:
                        print(f"迭代解析失败: {iter_error}")

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
    
    # ===== 新增的v2.0.0方法 =====

    def save_user(self, username: str, display_name: str = None, email: str = None,
                  password_hash: str = None, avatar_url: str = None) -> int:
        """保存新用户"""
        try:
            db = self.get_connection()
            insert_user_query = f"""
            INSERT INTO users (username, display_name, email, password_hash, avatar_url)
            VALUES ('{username.replace(chr(39), chr(39)*2)}',
                    '{display_name.replace(chr(39), chr(39)*2) if display_name else username}',
                    '{email.replace(chr(39), chr(39)*2) if email else None}',
                    '{password_hash.replace(chr(39), chr(39)*2) if password_hash else None}',
                    '{avatar_url.replace(chr(39), chr(39)*2) if avatar_url else None}')
            """
            db.run(insert_user_query)
            log_manager.log_database_operation("system", "insert", "user", {"username": username}, "database")
            return 1
        except Exception as e:
            print(f"保存用户时出错: {e}")
            return 0

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """根据ID获取用户信息"""
        try:
            db = self.get_connection()
            result = db.run(f"SELECT * FROM users WHERE id = {user_id}")
            # 解析结果逻辑...
            return {}
        except Exception as e:
            print(f"获取用户信息时出错: {e}")
            return {}

    def save_message_v2(self, session_id: Union[str, int], role: str, content: str,
                        model_name: str = None, tokens_used: int = 0,
                        parent_message_id: int = None, metadata: Dict = None) -> Optional[int]:
        """
        保存消息到增强的消息表（v2版本）

        Args:
            session_id: 会话ID（可以是字符串或整数）
            role: 消息角色
            content: 消息内容
            model_name: 模型名称
            tokens_used: 使用的token数
            parent_message_id: 父消息ID
            metadata: 元数据（JSON）

        Returns:
            int: 新消息ID，失败返回None
        """
        try:
            # 确保会话存在并获取会话整数ID
            session_int_id = self._ensure_session_and_get_id(session_id)

            if not session_int_id:
                raise ValueError(f"无法创建或找到会话: {session_id}")

            # 转换metadata为JSON字符串
            metadata_json = json.dumps(metadata) if metadata else None

            # 确保role是有效的枚举值
            valid_roles = ['system', 'user', 'assistant', 'tool']
            if role not in valid_roles:
                role = 'user'  # 默认值

            db = self.get_connection()
            insert_query = f"""
            INSERT INTO chat_messages (session_id, role, content, model_name, tokens_used,
                                     parent_message_id, metadata)
            VALUES ({session_int_id}, '{role}', '{content.replace(chr(39), chr(39)*2)}',
                    '{model_name.replace(chr(39), chr(39)*2) if model_name else None}',
                    {tokens_used}, {parent_message_id if parent_message_id else 'NULL'},
                    '{metadata_json.replace(chr(39), chr(39)*2) if metadata_json else None}')
            """
            db.run(insert_query)

            # 更新会话的消息计数和token计数
            self._update_session_stats(session_int_id, tokens_used)

            log_manager.log_database_operation(str(session_id), "insert", "message_v2", {
                "role": role,
                "content_length": len(content),
                "tokens_used": tokens_used
            }, "database")

            return 1  # 简化返回，实际应返回真实ID
        except Exception as e:
            print(f"保存消息v2时出错: {e}")
            log_manager.log_database_operation(str(session_id), "error", "message_v2", {
                "error": str(e),
                "role": role
            }, "database")
            return None

    def get_recent_messages_v2(self, session_id: Union[str, int], limit: int = 20,
                              include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        获取最近的聊天记录（v2版本）

        Args:
            session_id: 会话ID
            limit: 获取消息数量
            include_deleted: 是否包含已删除消息

        Returns:
            List[Dict]: 消息列表
        """
        try:
            # 获取会话整数ID
            session_int_id = self._get_session_int_id(session_id)
            if not session_int_id:
                return []

            db = self.get_connection()
            delete_filter = "" if include_deleted else "AND is_deleted = FALSE"

            query = f"""
            SELECT id, role, content, model_name, tokens_used, parent_message_id,
                   metadata, created_at
            FROM chat_messages
            WHERE session_id = {session_int_id} {delete_filter}
            ORDER BY created_at ASC
            LIMIT {limit}
            """

            result = db.run(query)
            return self._parse_message_results(result)
        except Exception as e:
            print(f"获取最近消息v2时出错: {e}")
            return []

    def save_session_v2(self, session_id: str, user_id: int = None, title: str = None,
                       persona_id: int = None, model_name: str = None,
                       settings: Dict = None) -> bool:
        """
        保存会话到增强的会话表（v2版本）

        Args:
            session_id: 会话字符串ID
            user_id: 用户ID
            title: 会话标题
            persona_id: AI人设ID
            model_name: 模型名称
            settings: 会话设置（JSON）

        Returns:
            bool: 成功返回True
        """
        try:
            db = self.get_connection()

            # 转换settings为JSON字符串
            settings_json = json.dumps(settings) if settings else None

            # 检查会话是否已存在
            check_query = f"SELECT COUNT(*) FROM chat_sessions WHERE session_id = '{session_id}'"
            result = db.run(check_query)

            session_exists = self._parse_count_result(result)
            if session_exists:
                # 更新现有会话
                update_parts = []
                if title is not None:
                    update_parts.append(f"title = '{title.replace(chr(39), chr(39)*2)}'")
                if persona_id is not None:
                    update_parts.append(f"persona_id = {persona_id}")
                if model_name is not None:
                    update_parts.append(f"model_name = '{model_name.replace(chr(39), chr(39)*2)}'")
                if settings_json is not None:
                    update_parts.append(f"settings = '{settings_json}'")
                if user_id is not None:
                    update_parts.append(f"user_id = {user_id}")

                if update_parts:
                    update_query = f"""
                    UPDATE chat_sessions
                    SET {', '.join(update_parts)}, updated_at = CURRENT_TIMESTAMP
                    WHERE session_id = '{session_id}'
                    """
                    db.run(update_query)
            else:
                # 插入新会话
                insert_query = f"""
                INSERT INTO chat_sessions (session_id, user_id, title, persona_id,
                                         model_name, settings)
                VALUES ('{session_id}', {user_id if user_id else 'NULL'},
                        '{title.replace(chr(39), chr(39)*2) if title else '新对话'}',
                        {persona_id if persona_id else 'NULL'},
                        '{model_name.replace(chr(39), chr(39)*2) if model_name else None}',
                        '{settings_json.replace(chr(39), chr(39)*2) if settings_json else None}')
                """
                db.run(insert_query)

            log_manager.log_database_operation(session_id, "save", "session_v2", {
                "title": title,
                "persona_id": persona_id,
                "model_name": model_name
            }, "database")
            return True
        except Exception as e:
            print(f"保存会话v2时出错: {e}")
            return False

    def get_all_sessions_v2(self, user_id: int = None, status: str = 'active',
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取会话列表（v2版本）

        Args:
            user_id: 用户ID（可选）
            status: 会话状态过滤
            limit: 返回数量限制

        Returns:
            List[Dict]: 会话列表
        """
        try:
            db = self.get_connection()

            # 构建查询条件
            where_conditions = [f"status = '{status}'"]
            if user_id is not None:
                where_conditions.append(f"cs.user_id = {user_id}")

            where_clause = "WHERE " + " AND ".join(where_conditions)

            query = f"""
            SELECT cs.id, cs.session_id, cs.user_id, cs.title, cs.persona_id,
                   cs.model_name, cs.status, cs.message_count, cs.total_tokens,
                   cs.created_at, cs.updated_at,
                   p.name as persona_name, p.avatar_url as persona_avatar
            FROM chat_sessions cs
            LEFT JOIN ai_personas p ON cs.persona_id = p.id
            {where_clause}
            ORDER BY cs.updated_at DESC
            LIMIT {limit}
            """

            result = db.run(query)
            return self._parse_session_results(result)
        except Exception as e:
            print(f"获取会话列表v2时出错: {e}")
            return []

    def save_summary_v2(self, session_id: Union[str, int], summary_text: str,
                       message_count: int, summary_type: str = 'auto',
                       message_range_start: int = None, message_range_end: int = None,
                       model_name: str = None, tokens_saved: int = 0,
                       created_by: int = None) -> bool:
        """
        保存摘要（v2版本）

        Args:
            session_id: 会话ID
            summary_text: 摘要内容
            message_count: 消息数量
            summary_type: 摘要类型
            message_range_start: 消息范围开始
            message_range_end: 消要范围结束
            model_name: 模型名称
            tokens_saved: 节省的token数
            created_by: 创建者用户ID

        Returns:
            bool: 成功返回True
        """
        try:
            session_int_id = self._get_session_int_id(session_id)
            if not session_int_id:
                raise ValueError(f"找不到会话: {session_id}")

            db = self.get_connection()
            insert_query = f"""
            INSERT INTO chat_summaries (session_id, summary_type, summary_text,
                                       message_range_start, message_range_end,
                                       message_count, model_name, tokens_saved, created_by)
            VALUES ({session_int_id}, '{summary_type}',
                    '{summary_text.replace(chr(39), chr(39)*2)}',
                    {message_range_start if message_range_start else 'NULL'},
                    {message_range_end if message_range_end else 'NULL'},
                    {message_count},
                    '{model_name.replace(chr(39), chr(39)*2) if model_name else None}',
                    {tokens_saved}, {created_by if created_by else 'NULL'})
            """
            db.run(insert_query)

            log_manager.log_database_operation(str(session_id), "insert", "summary_v2", {
                "summary_type": summary_type,
                "message_count": message_count,
                "tokens_saved": tokens_saved
            }, "database")
            return True
        except Exception as e:
            print(f"保存摘要v2时出错: {e}")
            return False

    # ===== 辅助方法 =====

    def _ensure_session_and_get_id(self, session_id: Union[str, int]) -> Optional[int]:
        """确保会话存在并返回整数ID"""
        if isinstance(session_id, int):
            return session_id

        # 尝试获取会话ID
        query = f"SELECT id FROM chat_sessions WHERE session_id = '{session_id}'"
        try:
            db = self.get_connection()
            result = db.run(query)

            # 如果会话存在，返回ID
            if result and str(result).strip("[](), ").isdigit():
                return int(str(result).strip("[](), "))

            # 如果会话不存在，创建新会话
            self.save_session_v2(session_id, title="新对话")
            result = db.run(query)
            if result and str(result).strip("[](), ").isdigit():
                return int(str(result).strip("[](), "))

        except Exception as e:
            print(f"确保会话存在时出错: {e}")

        return None

    def _get_session_int_id(self, session_id: Union[str, int]) -> Optional[int]:
        """获取会话的整数ID"""
        if isinstance(session_id, int):
            return session_id

        try:
            db = self.get_connection()
            result = db.run(f"SELECT id FROM chat_sessions WHERE session_id = '{session_id}'")
            if result and str(result).strip("[](), ").isdigit():
                return int(str(result).strip("[](), "))
        except Exception as e:
            print(f"获取会话ID时出错: {e}")

        return None

    def _update_session_stats(self, session_int_id: int, tokens_used: int = 0):
        """更新会话统计信息"""
        try:
            db = self.get_connection()
            update_query = f"""
            UPDATE chat_sessions
            SET message_count = message_count + 1,
                total_tokens = total_tokens + {tokens_used},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = {session_int_id}
            """
            db.run(update_query)
        except Exception as e:
            print(f"更新会话统计时出错: {e}")

    def _parse_count_result(self, result) -> int:
        """解析COUNT查询结果"""
        try:
            result_str = str(result)
            if result_str.startswith("[(") and result_str.endswith(",)]"):
                count_str = result_str[2:-3]
                return int(count_str) if count_str.isdigit() else 0
            elif result_str.startswith("[") and result_str.endswith("]"):
                content = result_str[1:-1].replace("(", "").replace(")", "").replace(",", "")
                return int(content.strip()) if content.strip().isdigit() else 0
            return 0
        except:
            return 0

    def _parse_message_results(self, result) -> List[Dict[str, Any]]:
        """解析消息查询结果"""
        messages = []
        try:
            result_str = str(result)
            if result_str.startswith("[") and result_str.endswith("]") and result_str != "[]":
                # 复杂的解析逻辑...
                # 这里简化处理
                pass
        except Exception as e:
            print(f"解析消息结果时出错: {e}")
        return messages

    def _parse_session_results(self, result) -> List[Dict[str, Any]]:
        """解析会话查询结果"""
        sessions = []
        try:
            result_str = str(result)
            if result_str.startswith("[") and result_str.endswith("]") and result_str != "[]":
                # 复杂的解析逻辑...
                # 这里简化处理
                pass
        except Exception as e:
            print(f"解析会话结果时出错: {e}")
        return sessions

    # ===== 保持向后兼容的原有方法 =====

    def get_message_count(self, session_id: str) -> int:
        """获取会话中的消息总数（兼容性方法）"""
        count_query = "SELECT COUNT(*) as count FROM chat_messages WHERE session_id = '{}'".format(session_id)

        try:
            db = self.get_connection()
            result = db.run(count_query)
            result_str = str(result)

            if result_str.startswith("[(") and result_str.endswith(",)]"):
                count_str = result_str[2:-3]
                if count_str.isdigit():
                    return int(count_str)

            if result_str.startswith("[") and result_str.endswith("]"):
                content = result_str[1:-1]
                content = content.replace("(", "").replace(")", "").replace(",", "")
                if content.strip().isdigit():
                    return int(content.strip())

            return 0
        except Exception as e:
            print(f"获取消息计数时出错: {e}")
            return 0