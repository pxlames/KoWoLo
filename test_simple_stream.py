#!/usr/bin/env python3
"""
测试简单的流式响应
"""

from flask import Flask, Response
import json
import time

app = Flask(__name__)

@app.route('/test-stream')
def test_stream():
    def generate():
        try:
            print("🔍 开始生成流式数据...")
            yield f"data: {json.dumps({'type': 'test', 'content': 'Hello'})}\n\n"
            time.sleep(0.1)
            yield f"data: {json.dumps({'type': 'test', 'content': 'World'})}\n\n"
            time.sleep(0.1)
            yield f"data: {json.dumps({'type': 'done', 'content': 'Complete'})}\n\n"
            print("✅ 流式数据生成完成")
        except Exception as e:
            print(f"❌ 生成流式数据时出错: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    })

if __name__ == '__main__':
    print("🚀 启动测试服务器...")
    app.run(debug=True, port=5002)
