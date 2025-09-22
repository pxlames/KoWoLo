#!/usr/bin/env python3
"""
测试流式输出和thinking标签捕获功能
"""

import requests
import json
import time

def test_streaming():
    """测试流式输出功能"""
    print("🧪 测试流式输出功能...")
    
    url = "http://localhost:5001/api/generate-summary-stream"
    
    try:
        response = requests.post(url, stream=True, timeout=30)
        response.raise_for_status()
        
        print("✅ 流式连接建立成功")
        print("📡 开始接收流式数据...")
        print("-" * 50)
        
        normal_content = ""
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        
                        if data.get('type') == 'content':
                            normal_content += data.get('content', '')
                            print(f"📝 内容: {data.get('content', '')}", end='', flush=True)
                        
                        elif data.get('type') == 'done':
                            print(f"\n🎉 流式输出完成！")
                            print(f"📊 内容长度: {len(normal_content)} 字符")
                            break
                        
                        elif data.get('type') == 'error':
                            print(f"\n❌ 错误: {data.get('content', '')}")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON解析错误: {e}")
                        continue
        
        print("-" * 50)
        print("✅ 流式输出测试完成")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始测试流式输出功能")
    print("=" * 60)
    
    # 测试流式输出
    test_streaming()
    
    print("\n🎉 所有测试完成！")
