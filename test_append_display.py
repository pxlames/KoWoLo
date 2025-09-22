#!/usr/bin/env python3
"""
测试追加显示功能
"""

import requests
import json
import time

def test_append_display():
    """测试追加显示功能"""
    print("🧪 测试追加显示功能...")
    
    try:
        # 第一次调用
        print("📡 第一次调用流式API...")
        response1 = requests.post("http://localhost:5001/api/generate-summary-stream", stream=True, timeout=30)
        
        if not response1.ok:
            print(f"❌ 第一次API调用失败: {response1.status_code}")
            return
        
        print("✅ 第一次调用成功")
        
        # 等待一下
        time.sleep(2)
        
        # 第二次调用
        print("📡 第二次调用流式API...")
        response2 = requests.post("http://localhost:5001/api/generate-summary-stream", stream=True, timeout=30)
        
        if not response2.ok:
            print(f"❌ 第二次API调用失败: {response2.status_code}")
            return
        
        print("✅ 第二次调用成功")
        
        # 检查总结文件内容
        try:
            with open('data/summary.json', 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
                summary_content = summary_data.get('summary', '')
                
                print(f"📝 总结内容长度: {len(summary_content)} 字符")
                print(f"📝 总结内容预览: {summary_content[:200]}...")
                
                # 检查是否包含think标签
                has_think_tags = '<think>' in summary_content or '</think>' in summary_content
                print(f"✅ 包含think标签: {has_think_tags}")
                
                if has_think_tags:
                    print("❌ 错误：总结中仍然包含think标签！")
                else:
                    print("✅ 成功：think标签已被正确去除！")
                    
        except Exception as e:
            print(f"❌ 读取总结文件失败: {e}")
        
        print("\n🎉 追加显示功能测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_append_display()
