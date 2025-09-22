#!/usr/bin/env python3
"""
直接测试API调用
"""

import requests
import json

def test_direct_api():
    """直接测试API调用"""
    print("🧪 直接测试API调用...")
    
    # 测试状态API
    try:
        response = requests.get("http://localhost:5001/api/status")
        if response.ok:
            data = response.json()
            print(f"✅ 状态API正常: {len(data.get('statusList', []))} 个状态")
        else:
            print(f"❌ 状态API失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 状态API测试失败: {e}")
        return
    
    # 测试流式API
    try:
        print("\n🌐 测试流式API...")
        response = requests.post("http://localhost:5001/api/generate-summary-stream", stream=True, timeout=10)
        
        print(f"📡 响应状态: {response.status_code}")
        print(f"📡 响应头: {dict(response.headers)}")
        
        if not response.ok:
            print(f"❌ 流式API失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return
        
        print("✅ 流式API连接成功，开始接收数据...")
        
        # 只读取前几行来测试
        line_count = 0
        for line in response.iter_lines():
            if line:
                line_count += 1
                print(f"📦 行 {line_count}: {line.decode('utf-8')}")
                
                if line_count >= 5:  # 只读取前5行
                    break
        
        print(f"✅ 成功读取 {line_count} 行数据")
        
    except Exception as e:
        print(f"❌ 流式API测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_api()
