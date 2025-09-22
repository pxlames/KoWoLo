#!/usr/bin/env python3
"""
个人技术工作规划工具启动脚本
"""

import os
import sys
from app import app, config

def check_config():
    """检查配置是否完整"""
    if not config.SILICONFLOW_API_KEY:
        print("❌ 错误：未设置 SILICONFLOW_API_KEY")
        print("请在 .env 文件中设置你的硅基流动API密钥")
        print("示例：SILICONFLOW_API_KEY=your_api_key_here")
        return False
    
    if not config.SILICONFLOW_BASE_URL:
        print("❌ 错误：未设置 SILICONFLOW_BASE_URL")
        print("请在 .env 文件中设置硅基流动API地址")
        print("示例：SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1")
        return False
    
    return True

def create_env_file():
    """创建.env文件模板"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("""# 硅基流动API配置
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# Flask配置
FLASK_ENV=development
FLASK_DEBUG=True
""")
        print("✅ 已创建 .env 文件模板，请编辑并填入你的API密钥")
        return False
    return True

def main():
    """主函数"""
    print("🚀 启动个人技术工作规划工具...")
    
    # 检查.env文件
    if not create_env_file():
        return
    
    # 检查配置
    if not check_config():
        return
    
    print("✅ 配置检查通过")
    print("🌐 启动Web服务器...")
    print("📱 访问地址：http://localhost:5001")
    print("⏹️  按 Ctrl+C 停止服务")
    
    try:
        app.run(debug=config.FLASK_DEBUG, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败：{e}")

if __name__ == '__main__':
    main()
