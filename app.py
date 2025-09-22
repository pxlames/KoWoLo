from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import os
import requests
from datetime import datetime
from config import Config
from langgraph_service import LangGraphService

app = Flask(__name__)
CORS(app)
config = Config()

# 确保数据目录存在
os.makedirs(config.DATA_DIR, exist_ok=True)

# 初始化LangGraph服务
langgraph_service = LangGraphService()

def load_data(file_path, default_value=None):
    """加载JSON数据"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return default_value or []
    return default_value or []

def save_data(file_path, data):
    """保存JSON数据"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """获取所有状态"""
    status_list = load_data(config.STATUS_FILE, [])
    summary_data = load_data(config.SUMMARY_FILE, {
        'summary': '',
        'lastUpdated': None
    })
    
    return jsonify({
        'statusList': status_list,
        'summary': summary_data.get('summary', ''),
        'lastUpdated': summary_data.get('lastUpdated')
    })

@app.route('/api/add-status', methods=['POST'])
def add_status():
    """添加新状态"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        status_type = data.get('type', 'ongoing')  # ongoing, planned, completed
        
        if not title:
            return jsonify({'success': False, 'error': '标题不能为空'}), 400
        
        # 加载当前状态列表
        status_list = load_data(config.STATUS_FILE, [])
        
        # 创建新状态
        new_status = {
            'id': str(len(status_list) + 1),
            'title': title,
            'description': description,
            'type': status_type,
            'completed': False,
            'aiProcessed': False,  # 是否已调用过AI
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        # 添加到列表
        status_list.append(new_status)
        
        # 保存状态
        save_data(config.STATUS_FILE, status_list)
        
        return jsonify({
            'success': True,
            'status': new_status
        })
        
    except Exception as e:
        print(f"Error adding status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/toggle-status', methods=['POST'])
def toggle_status():
    """切换状态完成状态"""
    try:
        data = request.get_json()
        status_id = data.get('id')
        completed = data.get('completed', False)
        
        # 加载当前状态列表
        status_list = load_data(config.STATUS_FILE, [])
        
        # 找到并更新状态
        for status in status_list:
            if status['id'] == status_id:
                status['completed'] = completed
                status['updatedAt'] = datetime.now().isoformat()
                break
        
        # 保存状态
        save_data(config.STATUS_FILE, status_list)
        
        return jsonify({
            'success': True,
            'statusList': status_list
        })
        
    except Exception as e:
        print(f"Error toggling status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-summary-stream', methods=['POST'])
def generate_summary_stream():
    """生成AI总结（真正的流式输出）"""
    def generate():
        try:
            # 加载当前状态列表
            status_list = load_data(config.STATUS_FILE, [])
            
            # 构建状态描述
            status_description = langgraph_service._build_status_description_from_list(status_list)
            
            # 构建系统提示
            system_prompt = langgraph_service.prompt_manager.get_system_prompt()
            
            # 构建用户消息
            summary = langgraph_service._load_summary()
            user_message = langgraph_service.prompt_manager.build_user_message(status_description, summary)
            
            # 构建完整的提示
            full_prompt = f"{system_prompt}\n\n{user_message}"
            
            # 调用硅基流动API（流式）
            url = f"{config.SILICONFLOW_BASE_URL}/chat/completions"
            headers = {
                "Authorization": f"Bearer {config.SILICONFLOW_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-ai/DeepSeek-V3",
                "messages": [
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": True
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60, stream=True)
            response.raise_for_status()
            
            full_content = ""
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                
                                # 检查content字段
                                content = delta.get('content')
                                if content is not None:
                                    full_content += content
                                    
                                    # 逐字符发送流式内容
                                    for char in content:
                                        yield f"data: {json.dumps({'type': 'content', 'content': char, 'done': False})}\n\n"
                                
                                # 检查reasoning_content字段（某些模型使用这个字段）
                                reasoning_content = delta.get('reasoning_content')
                                if reasoning_content is not None:
                                    full_content += reasoning_content
                                    
                                    # 逐字符发送流式内容
                                    for char in reasoning_content:
                                        yield f"data: {json.dumps({'type': 'content', 'content': char, 'done': False})}\n\n"
                                        
                        except json.JSONDecodeError:
                            continue
            
            # 追加到现有总结中
            existing_summary = load_data(config.SUMMARY_FILE, {})
            existing_content = existing_summary.get('summary', '')
            
            # 如果有现有内容，添加分隔符
            if existing_content.strip():
                separator = f"\n\n---\n**{datetime.now().strftime('%Y-%m-%d %H:%M')}**\n\n"
                new_summary = existing_content + separator + full_content
            else:
                new_summary = full_content
            
            summary_data = {
                'summary': new_summary,
                'lastUpdated': datetime.now().isoformat()
            }
            save_data(config.SUMMARY_FILE, summary_data)
            
            # 标记所有状态为已处理
            for status in status_list:
                status['aiProcessed'] = True
                status['updatedAt'] = datetime.now().isoformat()
            save_data(config.STATUS_FILE, status_list)
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done', 'content': '', 'summary': full_content})}\n\n"
            
        except Exception as e:
            print(f"Error in stream generation: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control'
    })

if __name__ == '__main__':
    app.run(debug=config.FLASK_DEBUG, host='0.0.0.0', port=5001)
