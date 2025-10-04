# 个人技术工作规划工具

一个基于LangGraph和硅基流动API的智能技术学习状态跟踪工具，采用GitHub风格的简洁界面设计。

## 功能特性1

- 📝 **状态管理**：记录当前正在进行和计划进行的技术工作
- ✅ **进度跟踪**：支持标记任务完成状态
- 🤖 **AI总结**：基于LangGraph调用大模型生成智能技术总结
- 💾 **上下文记忆**：保持对话历史，支持增量更新
- 🎨 **GitHub风格**：简洁美观的用户界面
- 📱 **响应式设计**：支持移动端访问

## 技术栈

- **后端**：Flask + Python
- **前端**：HTML5 + CSS3 + JavaScript
- **AI服务**：LangGraph + 硅基流动API
- **数据存储**：JSON文件

## 安装和运行

### 1. 安装依赖

```bash
cd todoLists
pip install -r requirements.txt
```

### 2. 配置API密钥

复制 `.env.example` 为 `.env` 并填入你的硅基流动API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

### 3. 启动服务

```bash
python run.py
```

或者直接运行：

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问：http://localhost:5000

## 使用说明

### 更新状态
1. 在"更新状态"区域填写你正在进行和计划进行的技术工作
2. 点击"提交状态"按钮
3. 系统会自动调用AI生成技术总结

### 管理任务
- 点击任务旁边的✓按钮可以标记任务为完成状态
- 系统会根据状态变化自动更新AI总结

### 刷新总结
- 点击"刷新总结"按钮可以重新生成技术总结
- 系统会基于当前状态和对话历史生成新的总结

## 项目结构

```
todoLists/
├── app.py                 # Flask主应用
├── config.py             # 配置文件
├── langgraph_service.py  # LangGraph服务
├── run.py               # 启动脚本
├── requirements.txt     # 依赖包
├── templates/           # HTML模板
│   └── index.html
├── static/             # 静态资源
│   ├── style.css       # 样式文件
│   └── script.js       # JavaScript文件
├── data/               # 数据存储目录
│   ├── status.json     # 状态数据
│   ├── summary.json    # 总结数据
│   └── conversation_history.json  # 对话历史
└── README.md           # 说明文档
```

## 数据存储

所有数据都存储在 `data/` 目录下的JSON文件中：

- `status.json`：当前工作状态
- `summary.json`：AI生成的总结
- `conversation_history.json`：对话历史记录

## 自定义配置

可以在 `config.py` 中修改以下配置：

- API密钥和地址
- 数据存储路径
- Flask调试模式
- 模型参数

## 故障排除

### 1. API密钥错误
确保在 `.env` 文件中正确设置了硅基流动的API密钥。

### 2. 端口占用
如果5000端口被占用，可以修改 `app.py` 中的端口号。

### 3. 依赖安装失败
确保Python版本兼容，建议使用Python 3.8+。

## 开发说明

### 添加新功能
1. 在 `app.py` 中添加新的API路由
2. 在 `static/script.js` 中添加前端交互逻辑
3. 在 `templates/index.html` 中添加UI元素

### 修改AI行为
编辑 `langgraph_service.py` 中的提示词和参数。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
