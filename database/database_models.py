#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL数据库模型定义
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

class Status(Base):
    """状态表"""
    __tablename__ = 'statuses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, comment='状态标题')
    description = Column(Text, comment='状态描述')
    type = Column(String(50), nullable=False, default='ongoing', comment='状态类型: ongoing, planned, completed')
    completed = Column(Boolean, default=False, comment='是否完成')
    ai_processed = Column(Boolean, default=False, comment='是否已被AI处理')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description or '',
            'type': self.type,
            'completed': self.completed,
            'aiProcessed': self.ai_processed,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        instance = cls()
        instance.id = int(data.get('id', 0)) if data.get('id') else None
        instance.title = data.get('title', '')
        instance.description = data.get('description', '')
        instance.type = data.get('type', 'ongoing')
        instance.completed = data.get('completed', False)
        instance.ai_processed = data.get('aiProcessed', False)
        
        # 处理时间字段
        if data.get('createdAt'):
            instance.created_at = datetime.fromisoformat(data['createdAt'].replace('Z', '+00:00'))
        if data.get('updatedAt'):
            instance.updated_at = datetime.fromisoformat(data['updatedAt'].replace('Z', '+00:00'))
        
        return instance

class Summary(Base):
    """总结表"""
    __tablename__ = 'summaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    summary = Column(Text, comment='AI生成的总结内容')
    last_updated = Column(DateTime, default=datetime.utcnow, comment='最后更新时间')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'summary': self.summary or '',
            'lastUpdated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        instance = cls()
        instance.summary = data.get('summary', '')
        if data.get('lastUpdated'):
            instance.last_updated = datetime.fromisoformat(data['lastUpdated'].replace('Z', '+00:00'))
        return instance

class ConversationHistory(Base):
    """对话历史表"""
    __tablename__ = 'conversation_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(50), nullable=False, comment='角色: user, assistant')
    content = Column(Text, nullable=False, comment='对话内容')
    timestamp = Column(DateTime, default=datetime.utcnow, comment='时间戳')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        instance = cls()
        instance.role = data.get('role', '')
        instance.content = data.get('content', '')
        if data.get('timestamp'):
            instance.timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        return instance

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url):
        """
        初始化数据库管理器
        
        Args:
            database_url: 数据库连接URL
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = Base
    
    def create_tables(self):
        """创建所有表"""
        self.Base.metadata.create_all(bind=self.engine)
        print("数据库表创建成功!")
    
    def drop_tables(self):
        """删除所有表"""
        self.Base.metadata.drop_all(bind=self.engine)
        print("数据库表删除成功!")
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def close(self):
        """关闭数据库连接"""
        self.engine.dispose()

# 数据库配置
DATABASE_CONFIGS = {
    'mysql': {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'your_password',
        'database': 'tech_planning',
        'charset': 'utf8mb4'
    },
    'sqlite': {
        'database': 'tech_planning.db'
    }
}

def get_database_url(config_type='mysql', **kwargs):
    """
    获取数据库连接URL
    
    Args:
        config_type: 数据库类型 ('mysql' 或 'sqlite')
        **kwargs: 数据库配置参数
    
    Returns:
        str: 数据库连接URL
    """
    if config_type == 'mysql':
        config = DATABASE_CONFIGS['mysql'].copy()
        config.update(kwargs)
        return f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"
    elif config_type == 'sqlite':
        config = DATABASE_CONFIGS['sqlite'].copy()
        config.update(kwargs)
        return f"sqlite:///{config['database']}"
    else:
        raise ValueError(f"不支持的数据库类型: {config_type}")

if __name__ == "__main__":
    # 测试数据库连接
    try:
        # 使用SQLite进行测试
        db_url = get_database_url('sqlite')
        db_manager = DatabaseManager(db_url)
        
        # 创建表
        db_manager.create_tables()
        
        # 测试会话
        with db_manager.get_session() as session:
            print("数据库连接测试成功!")
            
            # 测试插入数据
            test_status = Status(
                title="测试状态",
                description="这是一个测试状态",
                type="ongoing",
                completed=False,
                ai_processed=False
            )
            session.add(test_status)
            session.commit()
            
            # 测试查询数据
            statuses = session.query(Status).all()
            print(f"查询到 {len(statuses)} 条状态记录")
            
            # 清理测试数据
            session.query(Status).delete()
            session.commit()
            print("测试数据清理完成!")
        
        db_manager.close()
        print("数据库测试完成!")
        
    except Exception as e:
        print(f"数据库测试失败: {e}")
