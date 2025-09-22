#!/usr/bin/env python3
"""
调试流式API问题
"""

import json
import os
from config import Config
from langgraph_service import LangGraphService

def debug_prompt_building():
    """调试提示词构建过程"""
    print("🔍 开始调试提示词构建...")
    
    try:
        # 初始化服务
        langgraph_service = LangGraphService()
        config = Config()
        
        print("✅ 服务初始化成功")
        
        # 加载状态列表
        status_list = []
        status_file = config.STATUS_FILE
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                status_list = json.load(f)
        
        print(f"📊 状态列表长度: {len(status_list)}")
        
        # 检查状态列表内容
        for i, status in enumerate(status_list[:3]):  # 只检查前3个
            print(f"  状态 {i}: {status}")
        
        # 构建状态描述
        print("\n🔨 构建状态描述...")
        status_description = langgraph_service._build_status_description_from_list(status_list)
        print(f"✅ 状态描述构建成功: {len(status_description)} 字符")
        print(f"   内容预览: {status_description[:100]}...")
        
        # 构建系统提示
        print("\n🔨 构建系统提示...")
        system_prompt = langgraph_service.prompt_manager.get_system_prompt()
        print(f"✅ 系统提示构建成功: {len(system_prompt)} 字符")
        print(f"   内容预览: {system_prompt[:100]}...")
        
        # 加载总结
        print("\n🔨 加载总结...")
        summary = langgraph_service._load_summary()
        print(f"✅ 总结加载成功: {type(summary)} - {len(str(summary))} 字符")
        print(f"   内容预览: {str(summary)[:100]}...")
        
        # 构建用户消息
        print("\n🔨 构建用户消息...")
        user_message = langgraph_service.prompt_manager.build_user_message(status_description, summary)
        print(f"✅ 用户消息构建成功: {len(user_message)} 字符")
        print(f"   内容预览: {user_message[:100]}...")
        
        # 构建完整提示
        print("\n🔨 构建完整提示...")
        full_prompt = f"{system_prompt}\n\n{user_message}"
        print(f"✅ 完整提示构建成功: {len(full_prompt)} 字符")
        print(f"   内容预览: {full_prompt[:200]}...")
        
        print("\n🎉 所有步骤都成功完成！")
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_prompt_building()
