#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify Chatflow API 最终测试 - 完全绕过代理
"""

import requests
import json
import os


def clear_proxy():
    """清除所有代理设置"""
    # 清除环境变量中的代理设置
    proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']
    for var in proxy_vars:
        if var in os.environ:
            del os.environ[var]


def simple_chat_test(query: str, api_key: str = "app-1QxUL5OqjaFWvSNUE2bHsmPT"):
    """
    简单的聊天测试 - 完全绕过代理
    
    Args:
        query: 用户查询
        api_key: API密钥
    
    Returns:
        聊天响应
    """
    # 清除代理设置
    clear_proxy()
    
    url = "https://api.dify.ai/v1/chat-messages"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "inputs": {"todo": query, "info": "测试信息"},  # 添加todo和info参数
        "query": "1",  # 使用简单的query
        "response_mode": "blocking",  # 使用非流式模式
        "conversation_id": "",
        "user": "test-user"
    }
    
    # 添加调试信息
    print(f"API密钥: {api_key[:10]}...")
    print(f"请求头: {headers}")
    
    # 创建session并明确禁用代理
    session = requests.Session()
    session.proxies = {
        'http': None,
        'https': None
    }
    
    try:
        print(f"正在发送请求到: {url}")
        print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
        
        response = session.post(url, headers=headers, json=data, timeout=30)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API调用失败: {str(e)}"}


def main():
    """主函数"""
    print("=== Dify Chatflow API 最终测试 ===")
    print()
    
    # 测试查询
    query = "你好，请简单介绍一下自己"
    
    print(f"发送查询: {query}")
    print("正在获取响应...")
    print()
    
    # 调用API
    result = simple_chat_test(query)
    
    # 打印结果
    if "error" in result:
        print(f"[错误] {result['error']}")
    else:
        print("[成功] 获取响应:")
        print("-" * 50)
        
        # 提取并打印答案
        if "answer" in result:
            print(result["answer"])
        else:
            print("完整响应:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("-" * 50)
        
        # 打印其他有用信息
        if "conversation_id" in result:
            print(f"会话ID: {result['conversation_id']}")
        if "message_id" in result:
            print(f"消息ID: {result['message_id']}")


if __name__ == "__main__":
    main()
