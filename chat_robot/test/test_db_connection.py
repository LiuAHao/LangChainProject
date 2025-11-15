#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据库连接的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入需要的组件
import pymysql
from langchain_community.utilities import SQLDatabase

def test_pymysql_connection():
    """测试PyMySQL连接"""
    print("开始测试PyMySQL连接...")
    
    try:
        # 使用pymysql直接连接测试
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            port=3306,
            charset='utf8mb4'
        )
        print("PyMySQL连接成功")
        
        # 获取数据库版本
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            result = cursor.fetchone()
            if result:
                print(f"MySQL版本信息: {result[0]}")
            else:
                print("无法获取MySQL版本信息")
        
        connection.close()
        print("PyMySQL连接测试完成!")
        return True
        
    except Exception as e:
        print(f"PyMySQL连接测试失败: {e}")
        return False

def test_langchain_connection():
    """测试LangChain SQLDatabase连接"""
    print("开始测试LangChain SQLDatabase连接...")
    
    try:
        # 使用LangChain的SQLDatabase连接到指定数据库
        database_url = "mysql+pymysql://root:123456@localhost:3306/chat_robot"
        db = SQLDatabase.from_uri(database_url)
        print("LangChain SQLDatabase连接成功")
        
        # 执行简单的查询测试
        result = db.run("SELECT VERSION() as version")
        print(f"MySQL版本信息: {result}")
        
        print("LangChain SQLDatabase连接测试完成!")
        return True
        
    except Exception as e:
        print(f"LangChain SQLDatabase连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("数据库连接测试")
    print("=" * 50)
    
    # 测试PyMySQL连接
    pymysq_success = test_pymysql_connection()
    print()
    
    # 测试LangChain连接
    langchain_success = test_langchain_connection()
    print()
    
    print("=" * 50)
    if pymysq_success and langchain_success:
        print("所有测试通过!")
        return True
    else:
        print("部分测试失败!")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)