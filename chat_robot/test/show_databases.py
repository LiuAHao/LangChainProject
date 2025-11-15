#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
显示MySQL中可用的数据库
"""

import pymysql

def show_databases():
    """显示所有数据库"""
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
            # 执行SHOW DATABASES查询
            cursor.execute("SHOW DATABASES")
            result = cursor.fetchall()
            
            print("可用的数据库:")
            for row in result:
                print(f"  - {row[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"查询数据库列表失败: {e}")
        return False

if __name__ == "__main__":
    show_databases()