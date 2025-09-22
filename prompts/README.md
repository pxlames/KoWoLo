# 提示词管理

这个目录包含了所有AI提示词模板文件，用于管理和维护与AI交互的提示词。

## 文件结构

```
prompts/
├── README.md                    # 本说明文件
├── system_prompt.md            # 系统提示词
└── user_message_template.md    # 用户消息模板
```

## 文件说明

### system_prompt.md
系统提示词，定义了AI助手的角色、任务和输出要求。

**包含内容：**
- 角色定义
- 核心任务
- 输出要求
- 分析重点
- 输出格式示例

### user_message_template.md
用户消息模板，定义了发送给AI的消息格式。

**包含内容：**
- 模板结构
- 变量说明
- 使用说明
- 状态描述格式

## 管理工具

使用 `manage_prompts.py` 工具来管理提示词：

```bash
# 列出所有提示词文件
python3 manage_prompts.py list

# 查看提示词内容
python3 manage_prompts.py show system_prompt.md

# 测试提示词构建
python3 manage_prompts.py test
```

## 修改提示词

1. **直接编辑文件**：使用任何文本编辑器修改 `.md` 文件
2. **使用管理工具**：运行 `python3 manage_prompts.py show <filename>` 查看内容
3. **测试修改**：运行 `python3 manage_prompts.py test` 验证修改

## 提示词设计原则

1. **清晰明确**：提示词应该清晰明确，避免歧义
2. **结构化**：使用Markdown格式，结构清晰
3. **可维护**：分离不同功能的提示词到不同文件
4. **可测试**：提供测试工具验证提示词效果

## 变量替换

在模板中使用 `{variable_name}` 格式定义变量，程序会自动替换：

- `{status_description}`: 状态描述
- `{cur_summary}`: 当前总结

## 最佳实践

1. **版本控制**：将提示词文件纳入版本控制
2. **备份**：修改前备份原始文件
3. **测试**：修改后及时测试效果
4. **文档**：记录重要的修改和原因

## 故障排除

如果提示词加载失败：

1. 检查文件路径是否正确
2. 检查文件编码是否为UTF-8
3. 检查文件格式是否符合要求
4. 运行测试工具查看具体错误

## 扩展

要添加新的提示词模板：

1. 在 `prompts/` 目录下创建新的 `.md` 文件
2. 在 `prompt_manager.py` 中添加对应的加载方法
3. 在 `manage_prompts.py` 中添加管理功能
4. 更新本文档
