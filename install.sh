#!/bin/bash

echo "🚀 安装个人技术工作规划工具..."

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 安装依赖
echo "📦 安装依赖包..."
pip3 install -r requirements.txt

# 创建.env文件
if [ ! -f .env ]; then
    echo "📝 创建配置文件..."
    cat > .env << EOF
# 硅基流动API配置
SILICONFLOW_API_KEY=sk-mfvgxdishgetqlikzayseblbqwbgbfhnmzxybxlnedrfafwy
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1

# Flask配置
FLASK_ENV=development
FLASK_DEBUG=True
EOF
    echo "✅ 已创建 .env 文件，请编辑并填入你的API密钥"
else
    echo "✅ .env 文件已存在"
fi

# 创建数据目录
mkdir -p data
echo "✅ 数据目录已创建"

echo ""
echo "🎉 安装完成！"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，填入你的硅基流动API密钥"
echo "2. 运行: python3 run.py"
echo "3. 访问: http://localhost:5000"
echo ""
