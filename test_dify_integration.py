#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Dify API集成
"""

import requests
import json

def test_dify_api():
    """测试Dify API调用"""
    
    # 测试数据
    personal_description = "我是一个专注于AI开发的程序员"
    new_statuses = "完成项目文档编写, 优化代码性能, 准备技术分享"
    
    # API端点
    url = "http://localhost:5001/api/generate-summary-stream"
    
    # 请求数据
    data = {
        "personal_description": personal_description,
        "new_statuses": new_statuses
    }
    
    print("=== 测试Dify API集成 ===")
    print(f"个人描述: {personal_description}")
    print(f"新状态: {new_statuses}")
    print("\n开始调用API...")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        }
        response = requests.post(url, json=data, headers=headers, stream=True, timeout=60)
        response.raise_for_status()
        
        print("API响应:")
        print("-" * 50)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        chunk_data = json.loads(line_str[6:])
                        
                        if chunk_data.get('type') == 'content':
                            print(chunk_data['content'], end='', flush=True)
                        elif chunk_data.get('type') == 'done':
                            print(f"\n\n[完成] 总结: {chunk_data.get('summary', '')}")
                        elif chunk_data.get('type') == 'error':
                            print(f"\n[错误] {chunk_data['content']}")
                            
                    except json.JSONDecodeError:
                        continue
        
        print("\n" + "-" * 50)
        print("测试完成!")
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_dify_api()
