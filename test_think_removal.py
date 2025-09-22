#!/usr/bin/env python3
"""
测试think标签去除功能
"""

import re

def remove_think_tags(content):
    """去掉内容中的think标签"""
    if not content:
        return content
    
    # 去掉 <think>...</think> 标签及其内容
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    
    # 去掉单独的 <think> 和 </think> 标签
    content = re.sub(r'</?think>', '', content)
    
    # 清理多余的空行
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    return content.strip()

def test_think_removal():
    """测试think标签去除"""
    print("🧪 测试think标签去除功能...")
    
    # 测试用例1：完整的think标签
    test1 = """
    这是一些正常内容。
    
    <think>
    这是思考过程，应该被去掉。
    这里有很多思考内容。
    </think>
    
    这是think标签后的内容。
    """
    
    result1 = remove_think_tags(test1)
    print("测试1 - 完整think标签:")
    print(f"原文: {repr(test1)}")
    print(f"结果: {repr(result1)}")
    print(f"✅ 包含think标签: {'<think>' in result1}")
    print()
    
    # 测试用例2：单独的think标签
    test2 = """
    这是开始内容。
    <think>
    这是思考内容。
    </think>
    这是结束内容。
    """
    
    result2 = remove_think_tags(test2)
    print("测试2 - 单独think标签:")
    print(f"原文: {repr(test2)}")
    print(f"结果: {repr(result2)}")
    print(f"✅ 包含think标签: {'<think>' in result2}")
    print()
    
    # 测试用例3：多个think标签
    test3 = """
    开始内容。
    <think>思考1</think>
    中间内容。
    <think>思考2</think>
    结束内容。
    """
    
    result3 = remove_think_tags(test3)
    print("测试3 - 多个think标签:")
    print(f"原文: {repr(test3)}")
    print(f"结果: {repr(result3)}")
    print(f"✅ 包含think标签: {'<think>' in result3}")
    print()
    
    # 测试用例4：没有think标签
    test4 = """
    这是正常内容，没有think标签。
    应该保持不变。
    """
    
    result4 = remove_think_tags(test4)
    print("测试4 - 无think标签:")
    print(f"原文: {repr(test4)}")
    print(f"结果: {repr(result4)}")
    print(f"✅ 内容相同: {test4.strip() == result4}")
    print()
    
    print("🎉 所有测试完成！")

if __name__ == "__main__":
    test_think_removal()
