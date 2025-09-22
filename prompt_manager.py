"""
提示词管理模块
负责加载和管理各种提示词模板
"""

import os
from typing import Dict, Any
from datetime import datetime


class PromptManager:
    """提示词管理器"""
    
    def __init__(self, prompts_dir: str = None):
        """
        初始化提示词管理器
        
        Args:
            prompts_dir: 提示词文件目录，默认为当前目录下的prompts文件夹
        """
        if prompts_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompts_dir = os.path.join(current_dir, 'prompts')
        
        self.prompts_dir = prompts_dir
        self._cache = {}  # 缓存已加载的提示词
    
    def load_prompt(self, filename: str) -> str:
        """
        加载提示词文件
        
        Args:
            filename: 提示词文件名（不包含路径）
            
        Returns:
            提示词内容字符串
        """
        if filename in self._cache:
            return self._cache[filename]
        
        file_path = os.path.join(self.prompts_dir, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                self._cache[filename] = content
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"提示词文件不存在: {file_path}")
        except Exception as e:
            raise Exception(f"加载提示词文件失败: {e}")
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return self.load_prompt('system_prompt.md')
    
    def get_user_message_template(self) -> str:
        """获取用户消息模板"""
        return self.load_prompt('user_message_template.md')
    
    def build_user_message(self, status_description: str, cur_summary: Any) -> str:
        """
        构建用户消息
        
        Args:
            status_description: 状态描述
            cur_summary: 当前总结
            
        Returns:
            构建好的用户消息
        """
        template = self.get_user_message_template()
        
        # 处理cur_summary，确保是字符串
        if isinstance(cur_summary, dict):
            summary_text = cur_summary.get('summary', '')
        elif isinstance(cur_summary, str):
            summary_text = cur_summary
        else:
            summary_text = str(cur_summary) if cur_summary else ''
        
        return template.format(
            status_description=status_description,
            cur_summary=summary_text,
            date=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
    
    def reload_prompt(self, filename: str) -> str:
        """
        重新加载提示词文件（忽略缓存）
        
        Args:
            filename: 提示词文件名
            
        Returns:
            提示词内容字符串
        """
        if filename in self._cache:
            del self._cache[filename]
        return self.load_prompt(filename)
    
    def list_prompts(self) -> list:
        """
        列出所有可用的提示词文件
        
        Returns:
            提示词文件名列表
        """
        try:
            files = os.listdir(self.prompts_dir)
            return [f for f in files if f.endswith('.md')]
        except FileNotFoundError:
            return []
    
    def get_prompt_info(self, filename: str) -> Dict[str, Any]:
        """
        获取提示词文件信息
        
        Args:
            filename: 提示词文件名
            
        Returns:
            包含文件信息的字典
        """
        file_path = os.path.join(self.prompts_dir, filename)
        
        try:
            stat = os.stat(file_path)
            return {
                'filename': filename,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'exists': True
            }
        except FileNotFoundError:
            return {
                'filename': filename,
                'size': 0,
                'modified': 0,
                'exists': False
            }


# 创建全局实例
prompt_manager = PromptManager()
