#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建chat_robot数据库
"""

import pymysql

def create_chat_robot_database():
    """创建chat_robot数据库"""
    try:
        # 连接到MySQL服务器
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            port=3306,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS chat_robot")
            connection.commit()
            print("数据库chat_robot创建成功")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"创建数据库失败: {e}")
        return False

if __name__ == "__main__":
    create_chat_robot_database()