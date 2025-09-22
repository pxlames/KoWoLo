#!/usr/bin/env python3
"""
测试修复后的功能
"""

import requests
import json
import time

def test_fixed_functionality():
    """测试修复后的功能"""
    print("🧪 测试修复后的功能...")
    
    try:
        # 测试流式API
        print("📡 调用流式API...")
        response = requests.post("http://localhost:5001/api/generate-summary-stream", stream=True, timeout=30)
        
        if not response.ok:
            print(f"❌ API调用失败: {response.status_code}")
            return
        
        print("✅ 流式API连接成功")
        print("📝 开始接收流式内容...")
        print("-" * 60)
        
        char_count = 0
        start_time = time.time()
        content_buffer = ""
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                if line_str.startswith('data: '):
                    try:
                        data_str = line_str[6:]
                        data = json.loads(data_str)
                        
                        if data.get('type') == 'content':
                            char = data.get('content', '')
                            content_buffer += char
                            char_count += 1
                            
                            # 每50个字符显示一次进度
                            if char_count % 50 == 0:
                                print(f"📊 已接收 {char_count} 个字符...")
                        
                        elif data.get('type') == 'done':
                            end_time = time.time()
                            duration = end_time - start_time
                            
                            print("-" * 60)
                            print("🎉 流式输出完成！")
                            print(f"📊 统计信息:")
                            print(f"   - 总字符数: {char_count}")
                            print(f"   - 耗时: {duration:.2f}秒")
                            print(f"   - 平均速度: {char_count/duration:.1f} 字符/秒")
                            print(f"   - 内容长度: {len(content_buffer)} 字符")
                            
                            # 显示内容预览
                            print(f"\n📝 内容预览 (前200字符):")
                            print(f"   {content_buffer[:200]}...")
                            
                            # 检查是否包含think标签
                            has_think_tags = '<think>' in content_buffer or '</think>' in content_buffer
                            print(f"✅ 包含think标签: {has_think_tags}")
                            
                            break
                        
                        elif data.get('type') == 'error':
                            print(f"❌ 错误: {data.get('content')}")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON解析错误: {e}")
                        continue
        
        print("\n✅ 修复后的功能测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_functionality()
