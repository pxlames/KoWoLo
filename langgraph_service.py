import json
import os
import requests
from datetime import datetime
from typing import Dict, Any
from config import Config

class LangGraphService:
    def __init__(self):
        self.config = Config()
        self.llm = self._initialize_llm()
        self.conversation_history = self._load_conversation_history()
    
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
    
    def _save_conversation_history(self):
        """保存对话历史"""
        history_file = os.path.join(self.config.DATA_DIR, 'conversation_history.json')
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
    
    def generate_summary(self, status_data: Dict[str, Any]) -> str:
        """生成技术总结"""
        if not self.config.SILICONFLOW_API_KEY:
            return "AI服务暂时不可用，请检查API密钥配置。"
        
        try:
            # 构建当前状态描述
            current_status = self._build_status_description(status_data)
            
            # 构建系统提示
            system_prompt = self._build_system_prompt()
            
            # 构建用户消息
            user_message = self._build_user_message(current_status)
            
            # 构建完整的提示
            full_prompt = f"{system_prompt}\n\n{user_message}"
            
            # 添加历史对话上下文（最近3轮）
            recent_history = self.conversation_history[-6:]  # 最近3轮对话
            if recent_history:
                context = "\n\n历史对话上下文：\n"
                for msg in recent_history:
                    if msg['role'] == 'user':
                        context += f"用户: {msg['content']}\n"
                    elif msg['role'] == 'assistant':
                        context += f"助手: {msg['content']}\n"
                full_prompt += context
            
            # 调用硅基流动API
            response = self._call_siliconflow_api(full_prompt)
            
            # 保存对话历史
            self.conversation_history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
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
    
    def _build_status_description(self, status_data: Dict[str, Any]) -> str:
        """构建状态描述"""
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
    
    def _build_system_prompt(self) -> str:
        """构建系统提示"""
        return """你是一个专业的技术顾问，专门帮助程序员分析他们的技术学习状态和工作进展。

你的任务是：
1. 分析用户当前的技术工作状态
2. 提供专业的技术学习建议
3. 总结技术成长轨迹
4. 给出下一步学习方向的建议

请用专业但友好的语调，结合用户的具体情况，提供有价值的建议。回答要简洁明了，重点突出。

格式要求：
- 使用中文回答
- 结构清晰，使用适当的标题和分段
- 包含具体的技术建议
- 鼓励用户继续学习"""
    
    def _build_user_message(self, status_description: str) -> str:
        """构建用户消息"""
        return f"""请分析我的技术工作状态并提供建议：

{status_description}

请基于以上信息，为我生成一个技术学习状态总结，包括：
1. 当前技术状态的评估
2. 学习进展的分析
3. 下一步学习建议
4. 技术成长路径的建议

请保持简洁明了，重点突出。"""
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        self._save_conversation_history()
    
    def get_conversation_history(self):
        """获取对话历史"""
        return self.conversation_history
    
    def _call_siliconflow_api(self, prompt: str) -> str:
        """调用硅基流动API"""
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
                "max_tokens": 1000
            }
            
            # 重试机制
            max_retries = 2  # 每个模型重试2次
            for attempt in range(max_retries):
                try:
                    print(f"正在调用API (模型: {model}, 尝试 {attempt + 1}/{max_retries})...")
                    response = requests.post(url, headers=headers, json=data, timeout=60)
                    response.raise_for_status()
                    
                    result = response.json()
                    print(f"API调用成功，使用模型: {model}")
                    return result['choices'][0]['message']['content']
                    
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
        print("API调用失败，生成本地备用总结...")
        return self._generate_fallback_summary(prompt)
    
    def _generate_fallback_summary(self, prompt: str) -> str:
        """生成备用总结（当API不可用时）"""
        # 从prompt中提取状态信息
        if "正在进行的工作：" in prompt:
            current_work = prompt.split("正在进行的工作：")[1].split("(")[0].strip() if "正在进行的工作：" in prompt else ""
        else:
            current_work = ""
            
        if "计划进行的工作：" in prompt:
            future_work = prompt.split("计划进行的工作：")[1].split("(")[0].strip() if "计划进行的工作：" in prompt else ""
        else:
            future_work = ""
        
        # 生成简单的本地总结
        summary = "## 技术学习状态总结\n\n"
        
        if current_work:
            summary += f"### 当前进展\n- 正在进行：{current_work}\n- 状态：学习中，建议保持专注\n\n"
        
        if future_work:
            summary += f"### 学习计划\n- 计划学习：{future_work}\n- 建议：制定详细的学习计划和时间安排\n\n"
        
        summary += "### 学习建议\n"
        if current_work and future_work:
            summary += "- 建议在完成当前学习任务后再开始新的学习计划\n"
            summary += "- 保持学习的连续性和系统性\n"
        elif current_work:
            summary += "- 专注于当前学习任务，确保充分掌握\n"
            summary += "- 可以开始规划下一步学习方向\n"
        elif future_work:
            summary += "- 准备开始新的学习计划\n"
            summary += "- 建议先了解基础知识再深入实践\n"
        else:
            summary += "- 建议制定明确的技术学习目标\n"
            summary += "- 可以从基础技术开始，逐步深入\n"
        
        summary += "\n*注：此总结为本地生成，AI服务暂时不可用*\n"
        
        return summary
