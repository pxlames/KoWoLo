# 数据库模块

这个文件夹包含了MySQL数据库集成的所有相关文件。

## 📁 文件结构

```
database/
├── __init__.py              # 模块初始化文件
├── database_models.py       # 数据库模型定义
├── database_manager.py      # 数据库操作管理器
├── db_config.py            # 数据库配置管理
├── migrate_to_mysql.py     # 数据迁移工具
├── test_mysql_tools.py     # 测试脚本
├── database_setup.md       # 详细使用说明
└── README.md              # 本文件
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r ../requirements.txt
```

### 2. 测试工具
```bash
cd database
python test_mysql_tools.py
```

### 3. 数据迁移
```bash
# 从JSON文件迁移到MySQL
python migrate_to_mysql.py --action migrate --data-dir ../data

# 从MySQL导出到JSON
python migrate_to_mysql.py --action export --data-dir ../data
```

## 📖 详细说明

请查看 `database_setup.md` 文件获取详细的使用说明和配置信息。

## 🔧 在应用中使用

```python
# 在应用代码中导入
from database import get_db

# 获取数据库实例
db = get_db()

# 使用数据库操作
statuses = db.get_all_statuses()
summary = db.get_summary()
```

## 📊 数据库表结构

- **statuses** - 状态表
- **summaries** - 总结表  
- **conversation_history** - 对话历史表

详细结构请参考 `database_models.py` 文件。
