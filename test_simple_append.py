#!/usr/bin/env python3
"""
简单测试追加逻辑
"""

import json
import os
from datetime import datetime

def test_append_logic():
    """测试追加逻辑"""
    print("🧪 测试追加逻辑...")
    
    # 模拟现有总结内容
    existing_summary = {
        'summary': '这是第一次的总结内容。',
        'lastUpdated': '2025-09-22T23:00:00'
    }
    #
    # 模拟新生成的内容
    new_content = '这是第二次的总结内容。'
    
    # 测试追加逻辑
    existing_content = existing_summary.get('summary', '')
    
    if existing_content.strip():
        separator = f"\n\n---\n**{datetime.now().strftime('%Y-%m-%d %H:%M')}**\n\n"
        new_summary = existing_content + separator + new_content
    else:
        new_summary = new_content
    
    print(f"📝 现有内容: {existing_content}")
    print(f"📝 新内容: {new_content}")
    print(f"📝 追加后内容: {new_summary}")
    
    # 检查是否包含分隔符
    has_separator = '---' in new_summary
    print(f"✅ 包含分隔符: {has_separator}")
    
    # 检查是否包含时间戳
    has_timestamp = '**' in new_summary
    print(f"✅ 包含时间戳: {has_timestamp}")
    
    if has_separator and has_timestamp:
        print("✅ 成功：追加逻辑正确！")
    else:
        print("❌ 错误：追加逻辑有问题！")
    
    print("\n🎉 追加逻辑测试完成！")

if __name__ == "__main__":
    test_append_logic()
