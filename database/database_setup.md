# MySQL数据库集成说明

## 🎉 MySQL集成完成！

你的个人技术工作规划工具现在支持MySQL数据库存储！

## 📁 新增文件

### 数据库模型和工具
- `database_models.py` - 数据库模型定义
- `database_manager.py` - 数据库操作管理器
- `db_config.py` - 数据库配置管理
- `migrate_to_mysql.py` - 数据迁移工具

### 配置文件
- `.env.example` - 环境配置模板

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置数据库

#### 方法1: 使用环境变量
```bash
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=tech_planning
export DB_CHARSET=utf8mb4
```

#### 方法2: 创建.env文件
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env
```

### 3. 创建MySQL数据库
```sql
CREATE DATABASE tech_planning CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 迁移现有数据
```bash
# 从JSON文件迁移到MySQL
python migrate_to_mysql.py --action migrate --data-dir data

# 或者使用自定义配置
python migrate_to_mysql.py --action migrate \
  --host localhost \
  --user root \
  --password your_password \
  --database tech_planning
```

### 5. 测试数据库连接
```bash
python db_config.py
```

## 🔧 使用方法

### 在代码中使用数据库
```python
from db_config import get_db

# 获取数据库实例
db = get_db()

# 获取所有状态
statuses = db.get_all_statuses()

# 添加新状态
new_status = db.add_status({
    'title': '新任务',
    'description': '任务描述',
    'type': 'ongoing',
    'completed': False,
    'aiProcessed': False
})

# 更新状态
db.update_status(status_id, {'completed': True})

# 获取总结
summary = db.get_summary()

# 保存总结
db.save_summary({'summary': '新的总结内容'})
```

## 📊 数据库结构

### 状态表 (statuses)
- `id` - 主键，自增
- `title` - 状态标题
- `description` - 状态描述
- `type` - 状态类型 (ongoing, planned, completed)
- `completed` - 是否完成
- `ai_processed` - 是否已被AI处理
- `created_at` - 创建时间
- `updated_at` - 更新时间

### 总结表 (summaries)
- `id` - 主键，自增
- `summary` - 总结内容
- `last_updated` - 最后更新时间

### 对话历史表 (conversation_history)
- `id` - 主键，自增
- `role` - 角色 (user, assistant)
- `content` - 对话内容
- `timestamp` - 时间戳

## 🛠️ 管理工具

### 数据迁移
```bash
# 从JSON迁移到MySQL
python migrate_to_mysql.py --action migrate

# 从MySQL导出到JSON
python migrate_to_mysql.py --action export
```

### 数据库操作
```bash
# 测试数据库连接
python db_config.py

# 测试数据库模型
python database_models.py

# 测试数据库管理器
python database_manager.py
```

## 🔄 数据迁移流程

### 1. 备份现有数据
```bash
# 备份JSON文件
cp -r data data_backup
```

### 2. 迁移数据
```bash
# 迁移到MySQL
python migrate_to_mysql.py --action migrate
```

### 3. 验证迁移结果
```bash
# 检查数据库连接
python db_config.py

# 启动应用测试
python app.py
```

### 4. 回滚（如果需要）
```bash
# 从MySQL导出回JSON
python migrate_to_mysql.py --action export

# 恢复JSON文件
cp -r data_backup data
```

## ⚙️ 配置选项

### 环境变量
- `DB_TYPE` - 数据库类型 (mysql/sqlite)
- `DB_HOST` - MySQL主机地址
- `DB_PORT` - MySQL端口
- `DB_USER` - MySQL用户名
- `DB_PASSWORD` - MySQL密码
- `DB_NAME` - 数据库名
- `DB_CHARSET` - 字符集

### 数据库URL格式
```
mysql+pymysql://user:password@host:port/database?charset=utf8mb4
sqlite:///database.db
```

## 🎯 优势

### 1. 数据持久化
- 更可靠的数据存储
- 支持事务处理
- 数据一致性保证

### 2. 性能优化
- 索引支持
- 查询优化
- 连接池管理

### 3. 扩展性
- 支持复杂查询
- 数据关系管理
- 备份和恢复

### 4. 兼容性
- 支持MySQL和SQLite
- 自动切换数据库类型
- 向后兼容JSON存储

## 🔧 故障排除

### 常见问题

1. **MySQL连接失败**
   - 检查MySQL服务是否启动
   - 验证连接参数
   - 确认数据库存在

2. **权限问题**
   - 确保用户有数据库权限
   - 检查防火墙设置

3. **字符编码问题**
   - 使用utf8mb4字符集
   - 检查数据库和表编码

### 调试方法
```bash
# 测试数据库连接
python -c "from db_config import get_db; db = get_db(); print('连接成功')"

# 查看配置信息
python -c "from db_config import print_config_info; print_config_info()"
```

## 🎉 总结

现在你的应用支持：
- ✅ MySQL数据库存储
- ✅ 自动数据迁移
- ✅ 配置管理
- ✅ 向后兼容
- ✅ 性能优化

开始使用MySQL数据库来存储你的技术规划数据吧！🚀
