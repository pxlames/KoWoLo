#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置管理工具
"""

import os
from typing import Dict, Any
from .database_manager import get_database_url, TechPlanningDB

class DatabaseConfig:
    """数据库配置管理类"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载数据库配置"""
        config = {
            'type': os.getenv('DB_TYPE', 'sqlite'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'tech_planning'),
            'charset': os.getenv('DB_CHARSET', 'utf8mb4')
        }
        return config
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return get_database_url(self.config['type'], **self.config)
    
    def get_db_instance(self) -> TechPlanningDB:
        """获取数据库实例"""
        database_url = self.get_database_url()
        return TechPlanningDB(database_url)
    
    def is_mysql(self) -> bool:
        """判断是否使用MySQL"""
        return self.config['type'] == 'mysql'
    
    def is_sqlite(self) -> bool:
        """判断是否使用SQLite"""
        return self.config['type'] == 'sqlite'
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息（隐藏密码）"""
        info = self.config.copy()
        if info['password']:
            info['password'] = '*' * len(info['password'])
        return info

# 全局配置实例
_db_config = None

def get_database_config() -> DatabaseConfig:
    """获取数据库配置实例（单例模式）"""
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig()
    return _db_config

def get_db() -> TechPlanningDB:
    """获取数据库实例"""
    config = get_database_config()
    return config.get_db_instance()

def is_using_mysql() -> bool:
    """判断是否使用MySQL"""
    config = get_database_config()
    return config.is_mysql()

def is_using_sqlite() -> bool:
    """判断是否使用SQLite"""
    config = get_database_config()
    return config.is_sqlite()

def print_config_info():
    """打印配置信息"""
    config = get_database_config()
    info = config.get_config_info()
    
    print("=== 数据库配置信息 ===")
    for key, value in info.items():
        print(f"{key}: {value}")
    print("========================")

if __name__ == "__main__":
    # 测试配置
    print_config_info()
    
    # 测试数据库连接
    try:
        db = get_db()
        print("数据库连接成功!")
        
        # 测试基本操作
        statuses = db.get_all_statuses()
        print(f"状态记录数: {len(statuses)}")
        
        summary = db.get_summary()
        print(f"总结记录: {'有' if summary.get('summary') else '无'}")
        
        conversations = db.get_conversation_history()
        print(f"对话记录数: {len(conversations)}")
        
        db.close()
        print("数据库测试完成!")
        
    except Exception as e:
        print(f"数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
