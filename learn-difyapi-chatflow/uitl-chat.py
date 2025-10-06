#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify Chatflow API 调用代码
支持流式和非流式响应
"""

import requests
import json
from typing import Dict, Any, Optional, Iterator


class DifyChatflowClient:
    """Dify Chatflow API 客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai/v1"):
        """
        初始化客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def send_message(self, 
                    query: str,
                    inputs: Dict[str, Any] = None,
                    response_mode: str = "blocking",
                    conversation_id: str = "",
                    user: str = "default-user",
                    files: list = None) -> Dict[str, Any]:
        """
        发送消息到Chatflow
        
        Args:
            query: 用户查询内容
            inputs: 输入参数
            response_mode: 响应模式，"blocking" 或 "streaming"
            conversation_id: 会话ID，空字符串表示新会话
            user: 用户ID
            files: 文件列表
            
        Returns:
            API响应结果
        """
        if inputs is None:
            inputs = {}
        if files is None:
            files = []
        
        url = f"{self.base_url}/chat-messages"
        
        data = {
            "inputs": inputs,
            "query": query,
            "response_mode": response_mode,
            "conversation_id": conversation_id,
            "user": user,
            "files": files
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
        """处理流式响应"""
        try:
            lines = response.text.strip().split('\n')
            results = []
            
            for line in lines:
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
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
    
    def send_message_streaming(self, 
                              query: str,
                              inputs: Dict[str, Any] = None,
                              conversation_id: str = "",
                              user: str = "default-user",
                              files: list = None) -> Iterator[Dict[str, Any]]:
        """
        发送消息并返回流式响应迭代器
        
        Args:
            query: 用户查询内容
            inputs: 输入参数
            conversation_id: 会话ID
            user: 用户ID
            files: 文件列表
            
        Yields:
            流式响应数据块
        """
        if inputs is None:
            inputs = {}
        if files is None:
            files = []
        
        url = f"{self.base_url}/chat-messages"
        
        data = {
            "inputs": inputs,
            "query": query,
            "response_mode": "streaming",
            "conversation_id": conversation_id,
            "user": user,
            "files": files
        }
        
        try:
            response = self.session.post(url, json=data, stream=True)
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
            yield {
                "error": f"流式API请求失败: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None)
            }




def simple_chat_streaming(query: str, api_key: str = "app-1QxUL5OqjaFWvSNUE2bHsmPT"):
    """
    简单的流式聊天函数
    
    Args:
        query: 用户查询
        api_key: API密钥
    
    Yields:
        流式响应数据块
    """
    url = "https://api.dify.ai/v1/chat-messages"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "conversation_id": "",
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


def main():
    """主函数 - 演示如何使用Chatflow API"""
    
    # 使用你提供的API密钥
    API_KEY = "app-1QxUL5OqjaFWvSNUE2bHsmPT"

    # 测试3: 流式调用
    print("3. 流式调用:")
    print("开始接收流式数据...")

    # 实时解析和打印流式API返回的内容，兼容多种事件类型
    for chunk in simple_chat_streaming("你好", API_KEY):
        if not isinstance(chunk, dict):
            continue
        # 处理 message 事件，打印 answer 字段
        if chunk.get("event") == "message" and "answer" in chunk:
            print(chunk["answer"], end="", flush=True)
        # 处理 message_end 事件，可用于分隔或统计
        elif chunk.get("event") == "message_end":
            print("\n[消息结束]", flush=True)
        # 处理 tts_message 事件，打印音频信息
        elif chunk.get("event") == "tts_message" and "audio" in chunk:
            print(f"\n[收到TTS音频，长度: {len(chunk['audio'])}]", flush=True)
        # 处理 tts_message_end 事件
        elif chunk.get("event") == "tts_message_end":
            print("\n[TTS音频结束]", flush=True)
        # 处理错误
        elif "error" in chunk:
            print(f"\n错误: {chunk['error']}")
        # 其他事件可根据需要扩展
    print()  # 最后换行
if __name__ == "__main__":
    main()