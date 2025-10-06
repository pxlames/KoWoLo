#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移工具
从JSON文件迁移数据到MySQL数据库
"""

import os
import sys
import json
import argparse
from datetime import datetime
from .database_manager import TechPlanningDB, get_database_url

def create_database_config():
    """创建数据库配置文件"""
    config_file = '.env'
    
    if os.path.exists(config_file):
        print(f"配置文件 {config_file} 已存在")
        return
    
    config_content = """# 数据库配置
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=tech_planning
DB_CHARSET=utf8mb4

# 应用配置
FLASK_DEBUG=True
FLASK_PORT=5001
"""
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"已创建配置文件 {config_file}")
    print("请修改其中的数据库连接信息!")

def check_mysql_connection(host, port, user, password, database):
    """检查MySQL连接"""
    try:
        from pymysql import connect
        
        connection = connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        connection.close()
        return True
    except Exception as e:
        print(f"MySQL连接失败: {e}")
        return False

def create_mysql_database(host, port, user, password, database):
    """创建MySQL数据库"""
    try:
        from pymysql import connect
        
        # 连接到MySQL服务器（不指定数据库）
        connection = connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 {database} 创建成功!")
        
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"创建数据库失败: {e}")
        return False

def migrate_data(json_data_dir, mysql_config):
    """迁移数据"""
    print("开始数据迁移...")
    
    # 检查JSON数据目录
    if not os.path.exists(json_data_dir):
        print(f"JSON数据目录 {json_data_dir} 不存在!")
        return False
    
    # 检查必要的JSON文件
    required_files = ['status.json', 'summary.json', 'conversation_history.json']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(json_data_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        print(f"缺少以下JSON文件: {', '.join(missing_files)}")
        return False
    
    try:
        # 创建数据库连接URL
        database_url = get_database_url('mysql', **mysql_config)
        
        # 初始化数据库
        db = TechPlanningDB(database_url)
        
        # 迁移数据
        db.migrate_from_json(json_data_dir)
        
        # 验证迁移结果
        print("\n验证迁移结果...")
        
        statuses = db.get_all_statuses()
        print(f"状态记录: {len(statuses)} 条")
        
        summary = db.get_summary()
        print(f"总结记录: {'有' if summary.get('summary') else '无'}")
        
        conversations = db.get_conversation_history()
        print(f"对话记录: {len(conversations)} 条")
        
        db.close()
        print("数据迁移完成!")
        return True
        
    except Exception as e:
        print(f"数据迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def export_data(json_data_dir, mysql_config):
    """从数据库导出数据到JSON文件"""
    print("开始从数据库导出数据...")
    
    try:
        # 创建数据库连接URL
        database_url = get_database_url('mysql', **mysql_config)
        
        # 初始化数据库
        db = TechPlanningDB(database_url)
        
        # 导出数据
        db.export_to_json(json_data_dir)
        
        db.close()
        print("数据导出完成!")
        return True
        
    except Exception as e:
        print(f"数据导出失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据迁移工具')
    parser.add_argument('--action', choices=['migrate', 'export', 'config'], 
                       default='migrate', help='操作类型')
    parser.add_argument('--data-dir', default='data', 
                       help='JSON数据目录路径')
    parser.add_argument('--host', default='localhost', 
                       help='MySQL主机地址')
    parser.add_argument('--port', type=int, default=3306, 
                       help='MySQL端口')
    parser.add_argument('--user', default='root', 
                       help='MySQL用户名')
    parser.add_argument('--password', default='', 
                       help='MySQL密码')
    parser.add_argument('--database', default='tech_planning', 
                       help='MySQL数据库名')
    
    args = parser.parse_args()
    
    if args.action == 'config':
        create_database_config()
        return
    
    # MySQL配置
    mysql_config = {
        'host': args.host,
        'port': args.port,
        'user': args.user,
        'password': args.password,
        'database': args.database,
        'charset': 'utf8mb4'
    }
    
    if args.action == 'migrate':
        print("=== 数据迁移到MySQL ===")
        
        # 检查MySQL连接
        if not check_mysql_connection(**mysql_config):
            print("尝试创建数据库...")
            if not create_mysql_database(**mysql_config):
                print("无法创建数据库，请检查MySQL连接信息!")
                return
        
        # 迁移数据
        if migrate_data(args.data_dir, mysql_config):
            print("迁移成功! 现在可以更新应用配置使用MySQL数据库。")
        else:
            print("迁移失败!")
    
    elif args.action == 'export':
        print("=== 从MySQL导出数据 ===")
        
        if export_data(args.data_dir, mysql_config):
            print("导出成功!")
        else:
            print("导出失败!")

if __name__ == "__main__":
    main()
