# Dify API 调用代码

这个目录包含了调用 Dify API 的完整代码示例。

## 文件说明

- `dify_api_client.py` - 完整的 Dify API 客户端类，支持流式和非流式调用
- `simple_test.py` - 简化的 API 调用示例，适合快速测试
- `test.py` - 原始的 API 信息记录
- `requirements.txt` - 依赖包列表

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 使用简化版本

```python
from simple_test import call_dify_api, call_dify_api_streaming

# 非流式调用
result = call_dify_api("你好，请介绍一下自己")
print(result)

# 流式调用
for chunk in call_dify_api_streaming("请写一首诗"):
    print(chunk)
```

### 3. 使用完整客户端

```python
from dify_api_client import DifyAPIClient

# 创建客户端
client = DifyAPIClient(api_key="your-api-key")

# 非流式调用
result = client.run_workflow(
    inputs={"query": "你好"},
    response_mode="blocking"
)

# 流式调用
for chunk in client.run_workflow_streaming(
    inputs={"query": "你好"}
):
    print(chunk)
```

## API 密钥

当前使用的 API 密钥：`app-sDPkhDsRPVYY96A3o9JfmZUx`

## 功能特性

- ✅ 支持非流式调用（blocking mode）
- ✅ 支持流式调用（streaming mode）
- ✅ 完整的错误处理
- ✅ 类型提示支持
- ✅ 易于使用的接口

## 运行测试

```bash
# 运行简化测试
python simple_test.py

# 运行完整客户端测试
python dify_api_client.py
```
