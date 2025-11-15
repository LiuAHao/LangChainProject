from langchain_community.utilities import SQLDatabase
from typing import List, Dict, Any
import os

class DataManager:
    """数据库管理器，用于与MySQL数据库交互"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.database_url = os.getenv("MYSQL_URL", "mysql+pymysql://root:123456@localhost:3306/chat_robot")
        self.db = SQLDatabase.from_uri(self.database_url)
    
    def get_connection(self):
        """获取数据库连接"""
        return self.db
    
    def create_tables(self):
        """创建必要的数据表"""
        create_sessions_table = """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        create_messages_table = """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            role ENUM('system', 'user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
        )
        """
        
        try:
            db = self.get_connection()
            db.run(create_sessions_table)
            db.run(create_messages_table)
            print("数据表创建成功")
        except Exception as e:
            print(f"创建数据表时出错: {e}")
    
    def save_session(self, session_id: str):
        """保存新的聊天会话"""
        insert_session_query = "INSERT IGNORE INTO chat_sessions (session_id) VALUES ('{}')".format(session_id)
        
        try:
            db = self.get_connection()
            db.run(insert_session_query)
            # 注意：这里无法获取rowcount，所以我们假设操作成功
            return True
        except Exception as e:
            print(f"保存会话时出错: {e}")
            return False
    
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
            # 注意：这里无法获取lastrowid，所以我们返回一个默认值
            return 1
        except Exception as e:
            print(f"保存消息时出错: {e}")
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
            
            # 如果以上方法都不行，返回0
            return 0
        except Exception as e:
            print(f"获取消息计数时出错: {e}")
            return 0