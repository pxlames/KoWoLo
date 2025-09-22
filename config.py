import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 硅基流动API配置
    SILICONFLOW_API_KEY = os.getenv('SILICONFLOW_API_KEY', '')
    SILICONFLOW_BASE_URL = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
    
    # Flask配置
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 数据存储
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    STATUS_FILE = os.path.join(DATA_DIR, 'status.json')
    SUMMARY_FILE = os.path.join(DATA_DIR, 'summary.json')