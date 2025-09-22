#!/usr/bin/env python3
"""
测试generate函数
"""

import json
import os
from config import Config
from langgraph_service import LangGraphService

def test_generate_function():
    """测试generate函数"""
    print("🔍 测试generate函数...")
    
    try:
        # 初始化
        config = Config()
        langgraph_service = LangGraphService()
        
        # 加载数据
        status_list = []
        status_file = config.STATUS_FILE
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                status_list = json.load(f)
        
        print(f"📊 状态列表长度: {len(status_list)}")
        
        # 构建提示词
        status_description = langgraph_service._build_status_description_from_list(status_list)
        system_prompt = langgraph_service.prompt_manager.get_system_prompt()
        summary = langgraph_service._load_summary()
        user_message = langgraph_service.prompt_manager.build_user_message(status_description, summary)
        full_prompt = f"{system_prompt}\n\n{user_message}"
        
        print(f"✅ 提示词构建成功: {len(full_prompt)} 字符")
        
        # 模拟流式生成
        print("🔄 开始模拟流式生成...")
        
        # 这里我们模拟一个简单的流式响应
        def mock_generate():
            try:
                print("🔍 开始生成流式数据...")
                yield f"data: {json.dumps({'type': 'content', 'content': '测试', 'done': False})}\n\n"
                yield f"data: {json.dumps({'type': 'content', 'content': '内容', 'done': False})}\n\n"
                yield f"data: {json.dumps({'type': 'done', 'content': '', 'summary': '测试内容'})}\n\n"
                print("✅ 流式数据生成完成")
            except Exception as e:
                print(f"❌ 生成流式数据时出错: {e}")
                import traceback
                traceback.print_exc()
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        
        # 测试生成器
        for chunk in mock_generate():
            print(f"📦 生成数据: {chunk.strip()}")
        
        print("🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generate_function()
