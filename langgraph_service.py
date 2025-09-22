import json
import os
import requests
from datetime import datetime
from typing import Dict, Any
from config import Config
from prompt_manager import prompt_manager
import logging

logger = logging.getLogger('my_app')  # 创建名为 'my_app' 的 Logger
logging.basicConfig(
    level=logging.DEBUG,  # 设置最低日志级别为 DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',  # 时间格式
    # filename='app.lo',  # 输出到文件（默认追加模式）
    # filemode='w'  # 覆盖模式写入文件（可选）
)


class LangGraphService:
    def __init__(self):
        self.config = Config()
        self.llm = self._initialize_llm()
        self.conversation_history = self._load_conversation_history()
        self.prompt_manager = prompt_manager
    
    def _initialize_llm(self):
        """初始化大语言模型"""
        return True  # 简化实现，直接返回True
    
    def _load_conversation_history(self):
        """加载对话历史"""
        history_file = os.path.join(self.config.DATA_DIR, 'conversation_history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _load_summary(self):
        """加载总结信息"""
        summary = os.path.join(self.config.DATA_DIR, 'summary.json')
        if os.path.exists(summary):
            try:
                with open(summary, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def _save_conversation_history(self):
        """保存对话历史"""
        history_file = os.path.join(self.config.DATA_DIR, 'conversation_history.json')
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
    
    def generate_summary_from_list(self, status_list: list) -> str:
        """从状态列表生成总结"""
        if not self.config.SILICONFLOW_API_KEY:
            return "AI服务暂时不可用，请检查API密钥配置。"
        
        try:
            # 构建状态描述
            status_description = self._build_status_description_from_list(status_list)
            
            # 构建系统提示
            system_prompt = prompt_manager.get_system_prompt()
            
            # 构建用户消息
            summary = self._load_summary()
            # _load_summary 已经返回了反序列化的对象，无需再次 json.loads
            # 仅在调试时打印 summary
            print(json.dumps(summary, indent=4, ensure_ascii=False))
            user_message = prompt_manager.build_user_message(status_description, summary)
            
            # 构建完整的提示
            full_prompt = f"{system_prompt}\n\n{user_message}"
            
            # 调用硅基流动API
            response = self._call_siliconflow_api(full_prompt)
            
            # 保存对话历史
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # 保持历史记录在合理范围内（最多50轮对话）
            if len(self.conversation_history) > 50:
                self.conversation_history = self.conversation_history[-50:]
            
            self._save_conversation_history()
            
            return response
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"生成总结时出现错误: {str(e)}"
    
    
    def _build_status_description_from_list(self, status_list: list) -> str:
        """从状态列表构建状态描述"""
        if not status_list:
            return "当前技术工作状态：\n- 暂无工作状态记录\n"
        
        description = "当前技术工作状态：\n\n"
        
        # 按类型分组
        ongoing = [s for s in status_list if s['type'] == 'ongoing']
        planned = [s for s in status_list if s['type'] == 'planned']
        completed = [s for s in status_list if s['type'] == 'completed']
        
        if ongoing:
            description += "## 正在进行的工作：\n"
            for status in ongoing:
                status_text = "已完成" if status.get('completed', False) else "进行中"
                title = status.get('title', '无标题') or '无标题'
                description += f"- **{title}** ({status_text})\n"
                if status.get('description'):
                    description += f"  - {status['description']}\n"
            description += "\n"
        
        if planned:
            description += "## 计划进行的工作：\n"
            for status in planned:
                status_text = "已完成" if status.get('completed', False) else "计划中"
                title = status.get('title', '无标题') or '无标题'
                description += f"- **{title}** ({status_text})\n"
                if status.get('description'):
                    description += f"  - {status['description']}\n"
            description += "\n"
        
        if completed:
            description += "## 已完成的工作：\n"
            for status in completed:
                title = status.get('title', '无标题') or '无标题'
                description += f"- **{title}** (已完成)\n"
                if status.get('description'):
                    description += f"  - {status['description']}\n"
            description += "\n"
        
        return description
    
    def _build_status_description(self, status_data: Dict[str, Any]) -> str:
        """构建状态描述（兼容旧版本）"""
        current_work = status_data.get('currentWork', '')
        future_work = status_data.get('futureWork', '')
        current_completed = status_data.get('currentCompleted', False)
        future_completed = status_data.get('futureCompleted', False)
        
        description = "当前技术工作状态：\n"
        
        if current_work:
            status_text = "已完成" if current_completed else "进行中"
            description += f"- 正在进行的工作：{current_work} ({status_text})\n"
        else:
            description += "- 正在进行的工作：暂无\n"
        
        if future_work:
            status_text = "已完成" if future_completed else "计划中"
            description += f"- 计划进行的工作：{future_work} ({status_text})\n"
        else:
            description += "- 计划进行的工作：暂无\n"
        
        return description
    
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        self._save_conversation_history()
    
    def get_conversation_history(self):
        """获取对话历史"""
        return self.conversation_history
    
    def _call_siliconflow_api(self, prompt: str) -> str:
        """调用硅基流动API（流式输出）"""
        import time
        
        url = f"{self.config.SILICONFLOW_BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 尝试不同的模型
        models_to_try = ["Qwen/QwQ-32B", "Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2-7B-Instruct"]
        
        for model in models_to_try:
            print(f"尝试使用模型: {model}")
            
            data = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": True  # 启用流式输出
            }
            
            # 重试机制
            max_retries = 2  # 每个模型重试2次
            for attempt in range(max_retries):
                try:
                    print(f"正在调用API (模型: {model}, 尝试 {attempt + 1}/{max_retries})...")
                    response = requests.post(url, headers=headers, json=data, timeout=60, stream=True)
                    response.raise_for_status()
                    
                    # 处理流式响应
                    full_content = ""
                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            if line.startswith('data: '):
                                data_str = line[6:]  # 移除 'data: ' 前缀
                                if data_str.strip() == '[DONE]':
                                    break
                                
                                try:
                                    chunk = json.loads(data_str)
                                    if 'choices' in chunk and len(chunk['choices']) > 0:
                                        delta = chunk['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            content = delta['content']
                                            full_content += content
                                            print(content, end='', flush=True)  # 实时输出
                                except json.JSONDecodeError:
                                    continue
                    
                    print(f"\nAPI调用成功，使用模型: {model}")
                    return full_content
                    
                except requests.exceptions.Timeout as e:
                    print(f"API请求超时 (模型: {model}, 尝试 {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        wait_time = 3
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        print(f"模型 {model} 超时，尝试下一个模型...")
                        break
                        
                except requests.exceptions.ConnectionError as e:
                    print(f"API连接错误 (模型: {model}, 尝试 {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        wait_time = 2
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        print(f"模型 {model} 连接失败，尝试下一个模型...")
                        break
                        
                except requests.exceptions.RequestException as e:
                    print(f"API请求失败 (模型: {model}, 尝试 {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        wait_time = 2
                        print(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        print(f"模型 {model} 请求失败，尝试下一个模型...")
                        break
                        
                except KeyError as e:
                    print(f"API响应格式错误 (模型: {model}): {e}")
                    print(f"尝试下一个模型...")
                    break
                    
                except Exception as e:
                    print(f"未知错误 (模型: {model}): {e}")
                    print(f"尝试下一个模型...")
                    break
        
        # 如果所有API调用都失败，返回本地生成的简单总结
        return "API调用失败"