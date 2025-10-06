#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理工具
提供数据库操作的统一接口
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from .database_models import DatabaseManager, Status, Summary, ConversationHistory, get_database_url

class TechPlanningDB:
    """技术规划数据库操作类"""
    
    def __init__(self, database_url: str = None):
        """
        初始化数据库连接
        
        Args:
            database_url: 数据库连接URL，如果为None则从环境变量读取
        """
        if database_url is None:
            database_url = self._get_database_url_from_env()
        
        self.db_manager = DatabaseManager(database_url)
        self._init_database()
    
    def _get_database_url_from_env(self) -> str:
        """从环境变量获取数据库连接URL"""
        db_type = os.getenv('DB_TYPE', 'sqlite')
        
        if db_type == 'mysql':
            return get_database_url('mysql',
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', '3306')),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'tech_planning'),
                charset=os.getenv('DB_CHARSET', 'utf8mb4')
            )
        else:
            return get_database_url('sqlite',
                database=os.getenv('DB_NAME', 'tech_planning.db')
            )
    
    def _init_database(self):
        """初始化数据库"""
        try:
            self.db_manager.create_tables()
            print("数据库初始化成功!")
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """获取数据库会话的上下文管理器"""
        session = self.db_manager.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # ==================== 状态管理 ====================
    
    def get_all_statuses(self) -> List[Dict[str, Any]]:
        """获取所有状态"""
        with self.get_session() as session:
            statuses = session.query(Status).order_by(Status.created_at.desc()).all()
            return [status.to_dict() for status in statuses]
    
    def get_status_by_id(self, status_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取状态"""
        with self.get_session() as session:
            status = session.query(Status).filter(Status.id == status_id).first()
            return status.to_dict() if status else None
    
    def add_status(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加新状态"""
        with self.get_session() as session:
            # 生成新的ID
            max_id = session.query(Status.id).order_by(Status.id.desc()).first()
            new_id = (max_id[0] + 1) if max_id else 1
            
            status_data['id'] = str(new_id)
            status = Status.from_dict(status_data)
            session.add(status)
            session.flush()  # 获取生成的ID
            
            return status.to_dict()
    
    def update_status(self, status_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新状态"""
        with self.get_session() as session:
            status = session.query(Status).filter(Status.id == status_id).first()
            if not status:
                return None
            
            # 更新字段
            for key, value in update_data.items():
                if hasattr(status, key):
                    setattr(status, key, value)
            
            status.updated_at = datetime.utcnow()
            return status.to_dict()
    
    def delete_status(self, status_id: int) -> bool:
        """删除状态"""
        with self.get_session() as session:
            status = session.query(Status).filter(Status.id == status_id).first()
            if not status:
                return False
            
            session.delete(status)
            return True
    
    def toggle_status_completion(self, status_id: int, completed: bool) -> Optional[Dict[str, Any]]:
        """切换状态完成状态"""
        return self.update_status(status_id, {'completed': completed})
    
    def mark_all_statuses_processed(self) -> int:
        """标记所有状态为已处理"""
        with self.get_session() as session:
            count = session.query(Status).filter(Status.ai_processed == False).update({
                'ai_processed': True,
                'updated_at': datetime.utcnow()
            })
            return count
    
    # ==================== 总结管理 ====================
    
    def get_summary(self) -> Dict[str, Any]:
        """获取总结"""
        with self.get_session() as session:
            summary = session.query(Summary).order_by(Summary.last_updated.desc()).first()
            if summary:
                return summary.to_dict()
            else:
                return {'summary': '', 'lastUpdated': None}
    
    def save_summary(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """保存总结"""
        with self.get_session() as session:
            # 检查是否已存在总结
            existing_summary = session.query(Summary).first()
            
            if existing_summary:
                # 更新现有总结
                existing_summary.summary = summary_data.get('summary', '')
                existing_summary.last_updated = datetime.utcnow()
                return existing_summary.to_dict()
            else:
                # 创建新总结
                summary = Summary(
                    summary=summary_data.get('summary', ''),
                    last_updated=datetime.utcnow()
                )
                session.add(summary)
                return summary.to_dict()
    
    def append_summary(self, new_content: str) -> Dict[str, Any]:
        """追加总结内容"""
        current_summary = self.get_summary()
        existing_content = current_summary.get('summary', '')
        
        if existing_content.strip():
            separator = f"\n\n---\n**{datetime.now().strftime('%Y-%m-%d %H:%M')}**\n\n"
            new_summary = existing_content + separator + new_content
        else:
            new_summary = new_content
        
        return self.save_summary({'summary': new_summary})
    
    # ==================== 对话历史管理 ====================
    
    def get_conversation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取对话历史"""
        with self.get_session() as session:
            conversations = session.query(ConversationHistory).order_by(
                ConversationHistory.timestamp.desc()
            ).limit(limit).all()
            return [conv.to_dict() for conv in conversations]
    
    def add_conversation(self, role: str, content: str) -> Dict[str, Any]:
        """添加对话记录"""
        with self.get_session() as session:
            conversation = ConversationHistory(
                role=role,
                content=content,
                timestamp=datetime.utcnow()
            )
            session.add(conversation)
            return conversation.to_dict()
    
    def clear_conversation_history(self) -> int:
        """清空对话历史"""
        with self.get_session() as session:
            count = session.query(ConversationHistory).count()
            session.query(ConversationHistory).delete()
            return count
    
    # ==================== 数据迁移 ====================
    
    def migrate_from_json(self, json_data_dir: str = 'data'):
        """从JSON文件迁移数据到数据库"""
        print("开始从JSON文件迁移数据...")
        
        # 迁移状态数据
        status_file = os.path.join(json_data_dir, 'status.json')
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                statuses = json.load(f)
            
            with self.get_session() as session:
                # 清空现有状态
                session.query(Status).delete()
                
                # 插入新状态
                for status_data in statuses:
                    status = Status.from_dict(status_data)
                    session.add(status)
            
            print(f"迁移了 {len(statuses)} 条状态记录")
        
        # 迁移总结数据
        summary_file = os.path.join(json_data_dir, 'summary.json')
        if os.path.exists(summary_file):
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            self.save_summary(summary_data)
            print("迁移了总结数据")
        
        # 迁移对话历史
        conversation_file = os.path.join(json_data_dir, 'conversation_history.json')
        if os.path.exists(conversation_file):
            with open(conversation_file, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            
            with self.get_session() as session:
                # 清空现有对话历史
                session.query(ConversationHistory).delete()
                
                # 插入新对话历史
                for conv_data in conversations:
                    conversation = ConversationHistory.from_dict(conv_data)
                    session.add(conversation)
            
            print(f"迁移了 {len(conversations)} 条对话记录")
        
        print("数据迁移完成!")
    
    def export_to_json(self, json_data_dir: str = 'data'):
        """从数据库导出数据到JSON文件"""
        print("开始从数据库导出数据...")
        
        # 确保目录存在
        os.makedirs(json_data_dir, exist_ok=True)
        
        # 导出状态数据
        statuses = self.get_all_statuses()
        with open(os.path.join(json_data_dir, 'status.json'), 'w', encoding='utf-8') as f:
            json.dump(statuses, f, ensure_ascii=False, indent=2)
        
        # 导出总结数据
        summary = self.get_summary()
        with open(os.path.join(json_data_dir, 'summary.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 导出对话历史
        conversations = self.get_conversation_history()
        with open(os.path.join(json_data_dir, 'conversation_history.json'), 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
        
        print("数据导出完成!")
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()

# 全局数据库实例
_db_instance = None

def get_db() -> TechPlanningDB:
    """获取数据库实例（单例模式）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = TechPlanningDB()
    return _db_instance

def init_database(database_url: str = None):
    """初始化数据库"""
    global _db_instance
    _db_instance = TechPlanningDB(database_url)
    return _db_instance

if __name__ == "__main__":
    # 测试数据库操作
    try:
        # 初始化数据库
        db = TechPlanningDB()
        
        # 测试状态操作
        print("测试状态操作...")
        
        # 添加测试状态
        test_status = {
            'title': '测试状态',
            'description': '这是一个测试状态',
            'type': 'ongoing',
            'completed': False,
            'aiProcessed': False
        }
        
        new_status = db.add_status(test_status)
        print(f"添加状态: {new_status}")
        
        # 获取所有状态
        statuses = db.get_all_statuses()
        print(f"获取到 {len(statuses)} 条状态")
        
        # 更新状态
        if statuses:
            updated_status = db.toggle_status_completion(statuses[0]['id'], True)
            print(f"更新状态: {updated_status}")
        
        # 测试总结操作
        print("\n测试总结操作...")
        summary_data = {
            'summary': '这是一个测试总结',
            'lastUpdated': datetime.utcnow().isoformat()
        }
        db.save_summary(summary_data)
        
        summary = db.get_summary()
        print(f"获取总结: {summary}")
        
        # 测试对话历史
        print("\n测试对话历史...")
        db.add_conversation('user', '测试用户消息')
        db.add_conversation('assistant', '测试助手回复')
        
        conversations = db.get_conversation_history()
        print(f"获取到 {len(conversations)} 条对话记录")
        
        # 清理测试数据
        print("\n清理测试数据...")
        if statuses:
            db.delete_status(int(statuses[0]['id']))
        db.clear_conversation_history()
        
        db.close()
        print("数据库测试完成!")
        
    except Exception as e:
        print(f"数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
