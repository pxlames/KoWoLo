from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
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
            return default_value or {}
    return default_value or {}

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
    """获取当前状态"""
    status_data = load_data(config.STATUS_FILE, {
        'currentWork': '',
        'futureWork': '',
        'currentCompleted': False,
        'futureCompleted': False,
        'lastUpdated': None
    })
    
    summary_data = load_data(config.SUMMARY_FILE, {
        'summary': '',
        'lastUpdated': None
    })
    
    return jsonify({
        'currentWork': status_data.get('currentWork', ''),
        'futureWork': status_data.get('futureWork', ''),
        'currentCompleted': status_data.get('currentCompleted', False),
        'futureCompleted': status_data.get('futureCompleted', False),
        'summary': summary_data.get('summary', ''),
        'lastUpdated': status_data.get('lastUpdated')
    })

@app.route('/api/update-status', methods=['POST'])
def update_status():
    """更新状态"""
    try:
        data = request.get_json()
        current_work = data.get('currentWork', '').strip()
        future_work = data.get('futureWork', '').strip()
        
        # 加载当前状态
        status_data = load_data(config.STATUS_FILE, {
            'currentWork': '',
            'futureWork': '',
            'currentCompleted': False,
            'futureCompleted': False,
            'lastUpdated': None
        })
        
        # 更新状态
        if current_work:
            status_data['currentWork'] = current_work
            status_data['currentCompleted'] = False
        
        if future_work:
            status_data['futureWork'] = future_work
            status_data['futureCompleted'] = False
        
        status_data['lastUpdated'] = datetime.now().isoformat()
        
        # 保存状态
        save_data(config.STATUS_FILE, status_data)
        
        # 生成智能总结
        summary = langgraph_service.generate_summary(status_data)
        
        # 保存总结
        summary_data = {
            'summary': summary,
            'lastUpdated': datetime.now().isoformat()
        }
        save_data(config.SUMMARY_FILE, summary_data)
        
        return jsonify({
            'success': True,
            'currentWork': status_data['currentWork'],
            'futureWork': status_data['futureWork'],
            'currentCompleted': status_data['currentCompleted'],
            'futureCompleted': status_data['futureCompleted'],
            'summary': summary
        })
        
    except Exception as e:
        print(f"Error updating status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/toggle-status', methods=['POST'])
def toggle_status():
    """切换状态完成状态"""
    try:
        data = request.get_json()
        status_type = data.get('type')  # 'current' or 'future'
        completed = data.get('completed', False)
        
        # 加载当前状态
        status_data = load_data(config.STATUS_FILE, {
            'currentWork': '',
            'futureWork': '',
            'currentCompleted': False,
            'futureCompleted': False,
            'lastUpdated': None
        })
        
        # 更新完成状态
        if status_type == 'current':
            status_data['currentCompleted'] = completed
        elif status_type == 'future':
            status_data['futureCompleted'] = completed
        
        status_data['lastUpdated'] = datetime.now().isoformat()
        
        # 保存状态
        save_data(config.STATUS_FILE, status_data)
        
        # 生成更新的总结
        summary = langgraph_service.generate_summary(status_data)
        
        # 保存总结
        summary_data = {
            'summary': summary,
            'lastUpdated': datetime.now().isoformat()
        }
        save_data(config.SUMMARY_FILE, summary_data)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        print(f"Error toggling status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/refresh-summary', methods=['POST'])
def refresh_summary():
    """刷新总结"""
    try:
        # 加载当前状态
        status_data = load_data(config.STATUS_FILE, {
            'currentWork': '',
            'futureWork': '',
            'currentCompleted': False,
            'futureCompleted': False,
            'lastUpdated': None
        })
        
        # 生成新的总结
        summary = langgraph_service.generate_summary(status_data)
        
        # 保存总结
        summary_data = {
            'summary': summary,
            'lastUpdated': datetime.now().isoformat()
        }
        save_data(config.SUMMARY_FILE, summary_data)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        print(f"Error refreshing summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=config.FLASK_DEBUG, host='0.0.0.0', port=5001)
