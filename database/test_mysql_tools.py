#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL工具测试脚本
"""

import os
import sys
from datetime import datetime

def test_database_models():
    """测试数据库模型"""
    print("=== 测试数据库模型 ===")
    try:
        from .database_models import Status, Summary, ConversationHistory, DatabaseManager, get_database_url
        
        # 使用SQLite进行测试
        db_url = get_database_url('sqlite', database='test.db')
        db_manager = DatabaseManager(db_url)
        
        # 创建表
        db_manager.create_tables()
        print("✅ 数据库表创建成功")
        
        # 测试会话
        with db_manager.get_session() as session:
            # 测试Status模型
            status = Status(
                title="测试状态",
                description="这是一个测试状态",
                type="ongoing",
                completed=False,
                ai_processed=False
            )
            session.add(status)
            session.commit()
            
            # 测试查询
            statuses = session.query(Status).all()
            print(f"✅ Status模型测试成功，查询到 {len(statuses)} 条记录")
            
            # 测试转换
            status_dict = statuses[0].to_dict()
            print(f"✅ 字典转换成功: {status_dict['title']}")
            
            # 清理测试数据
            session.query(Status).delete()
            session.commit()
        
        # 清理测试数据库
        os.remove('test.db')
        print("✅ 数据库模型测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库模型测试失败: {e}")
        return False

def test_database_manager():
    """测试数据库管理器"""
    print("\n=== 测试数据库管理器 ===")
    try:
        from .database_manager import TechPlanningDB, get_database_url
        
        # 使用SQLite进行测试
        db_url = get_database_url('sqlite', database='test_manager.db')
        db = TechPlanningDB(db_url)
        
        # 测试状态操作
        test_status = {
            'title': '测试状态',
            'description': '测试描述',
            'type': 'ongoing',
            'completed': False,
            'aiProcessed': False
        }
        
        # 添加状态
        new_status = db.add_status(test_status)
        print(f"✅ 添加状态成功: ID {new_status['id']}")
        
        # 获取状态
        statuses = db.get_all_statuses()
        print(f"✅ 获取状态成功: {len(statuses)} 条")
        
        # 更新状态
        updated_status = db.toggle_status_completion(int(new_status['id']), True)
        print(f"✅ 更新状态成功: {updated_status['completed']}")
        
        # 测试总结操作
        summary_data = {
            'summary': '这是一个测试总结',
            'lastUpdated': datetime.utcnow().isoformat()
        }
        db.save_summary(summary_data)
        
        summary = db.get_summary()
        print(f"✅ 总结操作成功: {'有内容' if summary.get('summary') else '无内容'}")
        
        # 测试对话历史
        db.add_conversation('user', '测试用户消息')
        db.add_conversation('assistant', '测试助手回复')
        
        conversations = db.get_conversation_history()
        print(f"✅ 对话历史成功: {len(conversations)} 条")
        
        db.close()
        
        # 清理测试数据库
        os.remove('test_manager.db')
        print("✅ 数据库管理器测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_db_config():
    """测试数据库配置"""
    print("\n=== 测试数据库配置 ===")
    try:
        from .db_config import get_database_config, get_db, print_config_info
        
        # 测试配置
        config = get_database_config()
        print("✅ 配置加载成功")
        
        # 打印配置信息
        print_config_info()
        
        # 测试数据库连接
        db = get_db()
        print("✅ 数据库连接成功")
        
        # 测试基本操作
        statuses = db.get_all_statuses()
        print(f"✅ 基本操作成功: {len(statuses)} 条状态")
        
        db.close()
        print("✅ 数据库配置测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库配置测试失败: {e}")
        return False

def test_migration_tool():
    """测试迁移工具"""
    print("\n=== 测试迁移工具 ===")
    try:
        from .migrate_to_mysql import create_database_config
        
        # 测试配置创建
        create_database_config()
        print("✅ 配置创建成功")
        
        # 检查配置文件
        if os.path.exists('.env'):
            print("✅ .env文件已创建")
        else:
            print("⚠️ .env文件未创建")
        
        print("✅ 迁移工具测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 迁移工具测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试MySQL工具...")
    
    tests = [
        test_database_models,
        test_database_manager,
        test_db_config,
        test_migration_tool
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！MySQL工具准备就绪！")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
