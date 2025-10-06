from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import os
import requests
from datetime import datetime
from config import Config
from langgraph_service import LangGraphService
# Dify API 相关函数
def call_dify_api_streaming(personal_description: str, new_statuses: str, api_key: str = "app-1QxUL5OqjaFWvSNUE2bHsmPT"):
    """
    调用Dify API流式接口
    
    Args:
        personal_description: 个人描述
        new_statuses: 新状态列表（用逗号分隔的字符串）
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
        "inputs": {"todo": new_statuses, "info": personal_description},
        "query": "1",
        "response_mode": "streaming",
        "conversation_id": "",
        "user": "flask-app"
    }
    
    # 创建session并禁用代理
    session = requests.Session()
    session.proxies = {
        'http': None,
        'https': None
    }
    
    try:
        response = session.post(url, headers=headers, json=data, stream=True)
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

app = Flask(__name__)
CORS(app)
config = Config()

# 确保数据目录存在
os.makedirs(config.DATA_DIR, exist_ok=True)

# 初始化LangGraph服务
langgraph_service = LangGraphService()

# Dify API配置
DIFY_API_KEY = "app-1QxUL5OqjaFWvSNUE2bHsmPT"

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
    # 在路由函数中获取请求数据
    try:
        # 尝试获取JSON数据
        if request.is_json:
            data = request.get_json()
        else:
            # 如果不是JSON，尝试获取表单数据
            data = request.form.to_dict()
        
        personal_description = data.get('personal_description', '')
        new_statuses = data.get('new_statuses', '')
        
    except Exception as e:
        return jsonify({'error': f'请求数据解析失败: {str(e)}'}), 400
    
    # 如果没有提供个人描述，使用默认值
    if not personal_description:
        personal_description = "用户"
    
    # 如果没有提供新状态，从现有状态列表中获取
    if not new_statuses:
        status_list = load_data(config.STATUS_FILE, [])
        # 将状态标题用逗号连接
        new_statuses = ', '.join([status.get('title', '') for status in status_list if status.get('title')])
    
    def generate():
        try:
            
            # 调用Dify API（流式）
            full_content = ""
            
            for chunk in call_dify_api_streaming(
                personal_description=personal_description,
                new_statuses=new_statuses,
                api_key=DIFY_API_KEY
            ):
                if not isinstance(chunk, dict):
                    continue
                
                # 处理 message 事件，获取 answer 字段
                if chunk.get("event") == "message" and "answer" in chunk:
                    content = chunk["answer"]
                    full_content += content
                    
                    # 逐字符发送流式内容
                    for char in content:
                        yield f"data: {json.dumps({'type': 'content', 'content': char, 'done': False})}\n\n"
                
                # 处理 message_end 事件
                elif chunk.get("event") == "message_end":
                    break
                
                # 处理错误
                elif "error" in chunk:
                    yield f"data: {json.dumps({'type': 'error', 'content': chunk['error']})}\n\n"
                    return
            
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
            status_list = load_data(config.STATUS_FILE, [])
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
