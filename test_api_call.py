#!/usr/bin/env python3
"""
测试API调用
"""

import requests
import json
import os
from config import Config

def test_api_call():
    """测试API调用"""
    print("🔍 测试API调用...")
    
    try:
        config = Config()
        
        # 构建简单的测试数据
        data = {
            "model": "Qwen/QwQ-32B",
            "messages": [
                {
                    "role": "user",
                    "content": "你好，请简单回复一下。"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 100,
            "stream": True
        }
        
        url = f"{config.SILICONFLOW_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        }
        
        print(f"🌐 调用API:")
        print(f"  - URL: {url}")
        print(f"  - API Key: {config.SILICONFLOW_API_KEY[:10]}...")
        print(f"  - 数据: {json.dumps(data, ensure_ascii=False)}")
        
        response = requests.post(url, headers=headers, json=data, timeout=30, stream=True)
        
        print(f"📡 API响应状态: {response.status_code}")
        print(f"📡 响应头: {dict(response.headers)}")
        
        if not response.ok:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return
        
        print("✅ API调用成功，开始接收流式数据...")
        
        # 读取流式数据
        line_count = 0
        for line in response.iter_lines():
            if line:
                line_count += 1
                line_str = line.decode('utf-8')
                print(f"📦 行 {line_count}: {line_str}")
                
                if line_str.startswith('data: '):
                    try:
                        data_str = line_str[6:]
                        if data_str.strip() == '[DONE]':
                            print("✅ 流式数据接收完成")
                            break
                        
                        chunk = json.loads(data_str)
                        print(f"🔍 解析数据: {chunk}")
                        
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta:
                                content = delta['content']
                                print(f"✅ 内容: '{content}'")
                        
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON解析错误: {e}")
                        continue
                
                if line_count >= 10:  # 只读取前10行
                    break
        
        print(f"✅ 成功读取 {line_count} 行数据")
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_call()
