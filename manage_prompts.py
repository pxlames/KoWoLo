#!/usr/bin/env python3
"""
提示词管理工具
用于查看、编辑和管理提示词文件
"""

import os
import sys
from prompt_manager import prompt_manager


def list_prompts():
    """列出所有提示词文件"""
    print("📝 可用的提示词文件:")
    print("=" * 50)
    
    prompts = prompt_manager.list_prompts()
    if not prompts:
        print("❌ 没有找到提示词文件")
        return
    
    for filename in prompts:
        info = prompt_manager.get_prompt_info(filename)
        if info['exists']:
            size_kb = info['size'] / 1024
            print(f"📄 {filename} ({size_kb:.1f} KB)")
        else:
            print(f"❌ {filename} (文件不存在)")


def show_prompt(filename: str):
    """显示提示词内容"""
    try:
        content = prompt_manager.load_prompt(filename)
        print(f"📄 {filename} 内容:")
        print("=" * 50)
        print(content)
        print("=" * 50)
    except Exception as e:
        print(f"❌ 加载失败: {e}")


def test_prompt():
    """测试提示词构建"""
    print("🧪 测试提示词构建:")
    print("=" * 50)
    
    # 测试系统提示词
    try:
        system_prompt = prompt_manager.get_system_prompt()
        print("✅ 系统提示词加载成功")
        print(f"长度: {len(system_prompt)} 字符")
        print(f"预览: {system_prompt[:100]}...")
    except Exception as e:
        print(f"❌ 系统提示词加载失败: {e}")
    
    print()
    
    # 测试用户消息模板
    try:
        user_template = prompt_manager.get_user_message_template()
        print("✅ 用户消息模板加载成功")
        print(f"长度: {len(user_template)} 字符")
        print(f"预览: {user_template[:100]}...")
    except Exception as e:
        print(f"❌ 用户消息模板加载失败: {e}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("📝 提示词管理工具")
        print("=" * 30)
        print("用法:")
        print("  python manage_prompts.py list                    # 列出所有提示词")
        print("  python manage_prompts.py show <filename>         # 显示提示词内容")
        print("  python manage_prompts.py test                    # 测试提示词构建")
        print()
        print("示例:")
        print("  python manage_prompts.py list")
        print("  python manage_prompts.py show system_prompt.md")
        print("  python manage_prompts.py test")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_prompts()
    elif command == "show":
        if len(sys.argv) < 3:
            print("❌ 请指定文件名")
            return
        show_prompt(sys.argv[2])
    elif command == "test":
        test_prompt()
    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()
