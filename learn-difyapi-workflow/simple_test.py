#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Dify API调用示例
"""

import requests
import json


def call_dify_api(query: str, api_key: str = "app-sDPkhDsRPVYY96A3o9JfmZUx"):
    """
    简单的Dify API调用函数
    
    Args:
        query: 要发送的查询内容
        api_key: API密钥
    
    Returns:
        API响应结果
    """
    url = "https://api.dify.ai/v1/workflows/run"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "inputs": {"query": query},
        "response_mode": "blocking",  # 使用非流式模式，更简单
        "user": "test-user"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API调用失败: {str(e)}"}


def call_dify_api_streaming(query: str, api_key: str = "app-sDPkhDsRPVYY96A3o9JfmZUx"):
    """
    流式Dify API调用函数
    
    Args:
        query: 要发送的查询内容
        api_key: API密钥
    
    Yields:
        流式响应数据块
    """
    url = "https://api.dify.ai/v1/workflows/run"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "inputs": {"query": query},
        "response_mode": "streaming",
        "user": "test-user"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        yield data
                    except json.JSONDecodeError:
                        continue
    except requests.exceptions.RequestException as e:
        yield {"error": f"流式API调用失败: {str(e)}"}


if __name__ == "__main__":
    # 测试非流式调用
    print("=== 非流式调用测试 ===")
    result = call_dify_api("你好，请介绍一下自己")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n=== 流式调用测试 ===")
    print("开始接收流式数据...")
    for i, chunk in enumerate(call_dify_api_streaming("请写一首关于春天的诗")):
        print(f"数据块 {i+1}: {json.dumps(chunk, ensure_ascii=False)}")
        if i >= 3:  # 只显示前几个数据块
            print("... (更多数据)")
            break
