#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify API 客户端
支持流式和非流式响应
"""

import requests
import json
import time
from typing import Dict, Any, Optional, Iterator


class DifyAPIClient:
    """Dify API 客户端类"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        """
        初始化Dify API客户端
        
        Args:
            api_key: Dify API密钥
            base_url: API基础URL，默认为 https://api.dify.ai/v1
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def run_workflow(self, 
                    inputs: Dict[str, Any] = None, 
                    response_mode: str = "blocking",
                    user: str = "default-user",
                    workflow_id: str = None) -> Dict[str, Any]:
        """
        运行工作流
        
        Args:
            inputs: 输入参数
            response_mode: 响应模式，"blocking" 或 "streaming"
            user: 用户ID
            workflow_id: 工作流ID，如果为None则使用默认工作流
            
        Returns:
            API响应结果
        """
        if inputs is None:
            inputs = {}
        
        # 构建请求URL
        if workflow_id:
            url = f"{self.base_url}/workflows/{workflow_id}/run"
        else:
            url = f"{self.base_url}/workflows/run"
        
        # 构建请求数据
        data = {
            "inputs": inputs,
            "response_mode": response_mode,
            "user": user
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            if response_mode == "streaming":
                return self._handle_streaming_response(response)
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API请求失败: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None)
            }
    
    def _handle_streaming_response(self, response) -> Dict[str, Any]:
        """
        处理流式响应
        
        Args:
            response: requests响应对象
            
        Returns:
            处理后的响应数据
        """
        try:
            # 解析流式响应
            lines = response.text.strip().split('\n')
            results = []
            
            for line in lines:
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # 移除 'data: ' 前缀
                        results.append(data)
                    except json.JSONDecodeError:
                        continue
            
            return {
                "streaming_results": results,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": f"流式响应处理失败: {str(e)}",
                "status": "error"
            }
    
    def run_workflow_streaming(self, 
                              inputs: Dict[str, Any] = None,
                              user: str = "default-user",
                              workflow_id: str = None) -> Iterator[Dict[str, Any]]:
        """
        运行工作流并返回流式响应迭代器
        
        Args:
            inputs: 输入参数
            user: 用户ID
            workflow_id: 工作流ID
            
        Yields:
            流式响应数据块
        """
        if inputs is None:
            inputs = {}
        
        # 构建请求URL
        if workflow_id:
            url = f"{self.base_url}/workflows/{workflow_id}/run"
        else:
            url = f"{self.base_url}/workflows/run"
        
        # 构建请求数据
        data = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": user
        }
        
        try:
            response = self.session.post(url, json=data, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # 移除 'data: ' 前缀
                            yield data
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            yield {
                "error": f"流式API请求失败: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None)
            }


def main():
    """主函数 - 演示如何使用Dify API客户端"""
    
    # 使用你提供的API密钥
    API_KEY = "app-sDPkhDsRPVYY96A3o9JfmZUx"
    
    # 创建客户端实例
    client = DifyAPIClient(api_key=API_KEY)
    
    print("=== Dify API 客户端测试 ===\n")
    
    # 测试1: 非流式调用
    print("1. 测试非流式调用:")
    result = client.run_workflow(
        inputs={"query": "你好，请介绍一下自己"},
        response_mode="blocking",
        user="test-user-123"
    )
    print(f"非流式响应: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
    
    # 测试2: 流式调用
    print("2. 测试流式调用:")
    result = client.run_workflow(
        inputs={"query": "请详细解释一下人工智能的发展历程"},
        response_mode="streaming",
        user="test-user-456"
    )
    print(f"流式响应: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
    
    # 测试3: 流式迭代器
    print("3. 测试流式迭代器:")
    print("开始接收流式数据...")
    for i, chunk in enumerate(client.run_workflow_streaming(
        inputs={"query": "请写一首关于春天的诗"},
        user="test-user-789"
    )):
        print(f"数据块 {i+1}: {json.dumps(chunk, ensure_ascii=False)}")
        if i >= 5:  # 限制输出数量
            print("... (更多数据)")
            break


if __name__ == "__main__":
    main()
