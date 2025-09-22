#!/usr/bin/env python3
"""
测试流式API调用和解析
"""

import requests
import json
import time

def test_stream_api():
    """测试流式API调用"""
    print("🧪 开始测试流式API调用...")
    
    url = "http://localhost:5001/api/generate-summary-stream"
    
    try:
        print("📡 发送请求到:", url)
        response = requests.post(url, stream=True, timeout=30)
        
        if not response.ok:
            print(f"❌ 请求失败: {response.status_code} {response.reason}")
            return
        
        print("✅ 连接成功，开始接收流式数据...")
        print("-" * 60)
        
        chunk_count = 0
        char_count = 0
        start_time = time.time()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                print(f"📦 原始行: {repr(line)}")
                
                if line.startswith('data: '):
                    try:
                        data_str = line[6:]
                        print(f"📝 数据字符串: {repr(data_str)}")
                        
                        data = json.loads(data_str)
                        print(f"🔍 解析数据: {data}")
                        
                        if data.get('type') == 'content':
                            char_count += 1
                            print(f"✅ 字符 {char_count}: '{data.get('content')}'")
                        
                        elif data.get('type') == 'done':
                            print("🎉 流式输出完成!")
                            print(f"📊 总字符数: {char_count}")
                            break
                        
                        elif data.get('type') == 'error':
                            print(f"❌ 错误: {data.get('content')}")
                            break
                        
                        chunk_count += 1
                        
                        # 每10个字符暂停一下，便于观察
                        if char_count % 10 == 0:
                            time.sleep(0.1)
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON解析错误: {e}")
                        print(f"   原始数据: {repr(data_str)}")
                        continue
                    except Exception as e:
                        print(f"❌ 处理数据时出错: {e}")
                        continue
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("-" * 60)
        print(f"✅ 测试完成!")
        print(f"📊 统计信息:")
        print(f"   - 总数据块: {chunk_count}")
        print(f"   - 总字符数: {char_count}")
        print(f"   - 耗时: {duration:.2f}秒")
        print(f"   - 平均速度: {char_count/duration:.1f} 字符/秒")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_simple_stream():
    """测试简单的流式响应"""
    print("\n🔬 测试简单流式响应...")
    
    try:
        response = requests.get("http://localhost:5001/api/status")
        if response.ok:
            data = response.json()
            print(f"✅ 状态API正常: {len(data.get('statusList', []))} 个状态")
        else:
            print(f"❌ 状态API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 状态API测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始流式API测试")
    print("=" * 60)
    
    # 先测试基本API
    test_simple_stream()
    
    # 再测试流式API
    test_stream_api()
    
    print("\n🎉 所有测试完成!")
