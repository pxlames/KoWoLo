#!/usr/bin/env python3
"""
测试应用功能
"""

import json
import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from langgraph_service import LangGraphService

def test_config():
    """测试配置加载"""
    print("🔧 测试配置加载...")
    config = Config()
    print(f"   数据目录: {config.DATA_DIR}")
    print(f"   API地址: {config.SILICONFLOW_BASE_URL}")
    print(f"   API密钥: {'已设置' if config.SILICONFLOW_API_KEY else '未设置'}")
    return True

def test_data_structure():
    """测试数据结构"""
    print("📁 测试数据结构...")
    config = Config()
    
    # 确保数据目录存在
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # 测试状态数据结构
    test_status = {
        'currentWork': '学习Python Flask框架',
        'futureWork': '学习机器学习算法',
        'currentCompleted': False,
        'futureCompleted': False,
        'lastUpdated': datetime.now().isoformat()
    }
    
    status_file = config.STATUS_FILE
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(test_status, f, ensure_ascii=False, indent=2)
    
    print(f"   状态文件: {status_file}")
    
    # 测试总结数据结构
    test_summary = {
        'summary': '这是一个测试总结',
        'lastUpdated': datetime.now().isoformat()
    }
    
    summary_file = config.SUMMARY_FILE
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(test_summary, f, ensure_ascii=False, indent=2)
    
    print(f"   总结文件: {summary_file}")
    return True

def test_langgraph_service():
    """测试LangGraph服务"""
    print("🤖 测试LangGraph服务...")
    
    try:
        service = LangGraphService()
        print("   LangGraph服务初始化成功")
        
        # 测试状态描述构建
        test_status = {
            'currentWork': '学习Python Flask框架',
            'futureWork': '学习机器学习算法',
            'currentCompleted': False,
            'futureCompleted': False
        }
        
        description = service._build_status_description(test_status)
        print("   状态描述构建成功")
        print(f"   描述内容: {description[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   LangGraph服务测试失败: {e}")
        return False

def test_flask_app():
    """测试Flask应用"""
    print("🌐 测试Flask应用...")
    
    try:
        from app import app
        print("   Flask应用初始化成功")
        
        # 测试路由
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("   主页路由正常")
            else:
                print(f"   主页路由异常: {response.status_code}")
                return False
            
            response = client.get('/api/status')
            if response.status_code == 200:
                print("   状态API正常")
            else:
                print(f"   状态API异常: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   Flask应用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试个人技术工作规划工具...")
    print("=" * 50)
    
    tests = [
        ("配置加载", test_config),
        ("数据结构", test_data_structure),
        ("LangGraph服务", test_langgraph_service),
        ("Flask应用", test_flask_app),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！应用可以正常运行。")
        print("\n🚀 启动应用:")
        print("   python3 run.py")
        print("\n🌐 访问地址:")
        print("   http://localhost:5000")
    else:
        print("⚠️  部分测试失败，请检查配置和依赖。")
        print("\n💡 常见问题:")
        print("   1. 确保已安装所有依赖: pip3 install -r requirements.txt")
        print("   2. 检查API密钥配置")
        print("   3. 确保Python版本兼容")

if __name__ == '__main__':
    main()
