# 校园信息收集系统（njfu） 
# linux系统与shell编程课设

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── models.py      # 数据模型
│   ├── routes.py      # API 路由
│   └── utils.py       # 工具函数
├── config/
│   └── config.yaml    # 配置文件
├── data/
│   └── notices.db     # SQLite 数据库
├── scripts/
│   ├── merge_databases.py    # 数据库合并脚本
│   └── extract_data.py       # 数据提取脚本
└── requirements.txt   # Python 依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

1. 确保 SQLite 数据库文件位于 `data/notices.db`
2. 如果需要合并多个数据库，使用 `scripts/merge_databases.py`

### 3. 配置 QQ 机器人

1. 复制 `config/config.yaml.example` 为 `config/config.yaml`
2. 修改配置文件中的 QQ 号和群号
3. 确保 go-cqhttp 已正确配置并运行

### 4. 启动服务

```bash
python app.py
```

服务将在 http://localhost:5000 启动。

## API 文档

### 1. 通知相关接口

#### 获取所有通知
```
GET /api/notices
```

响应：
```json
{
  "data": [
    {
      "id": 1,
      "title": "系统维护通知",
      "content": "系统将于本周六凌晨2点进行例行维护",
      "publish_date": "2024-03-20",
      "category": "通知",
      "source": "系统管理员",
      "link": "https://example.com/maintenance",
      "views": 156,
      "favorites": 15
    }
  ],
  "message": "success",
  "status": 200
}
```

#### 获取比赛信息
```
GET /api/competitions
```

#### 获取考试信息
```
GET /api/exams
```

#### 获取实习信息
```
GET /api/internships
```

### 2. 用户相关接口

#### 用户登录
```
POST /api/login
```

请求体：
```json
{
  "username": "admin",
  "password": "password"
}
```

响应：
```json
{
  "data": {
    "id": 1,
    "username": "admin",
    "account": "admin@example.com"
  },
  "message": "登录成功",
  "status": 200
}
```

## 数据库管理

### 1. 数据库结构

#### 通知表 (notices)
```sql
CREATE TABLE notices (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  publish_date TEXT NOT NULL,
  category TEXT NOT NULL,
  source TEXT NOT NULL,
  link TEXT NOT NULL,
  views INTEGER DEFAULT 0,
  favorites INTEGER DEFAULT 0
);
```

#### 用户表 (users)
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL,
  account TEXT NOT NULL,
  password TEXT NOT NULL,
  favorites TEXT
);
```

### 2. 数据提取

使用 `scripts/extract_data.py` 从数据库提取数据：

```bash
python scripts/extract_data.py
```

这将生成 `data/notices.json` 文件。

### 3. 数据库合并

使用 `scripts/merge_databases.py` 合并多个数据库：

```bash
python scripts/merge_databases.py --source db1.db --target db2.db
```

## QQ 机器人配置

### 1. 配置文件

`config/config.yaml` 示例：
```yaml
bot:
  qq: 123456789
  groups:
    - 987654321
    - 123456789
```

### 2. 消息处理

机器人会自动处理以下类型的消息：
- 群通知
- 私聊消息
- 系统通知

## 开发指南

### 1. 添加新的通知类型

1. 在数据库中添加新的通知记录
2. 确保 `category` 字段与前端定义的类型匹配

### 2. 添加新的 API 端点

1. 在 `app/routes.py` 中添加新的路由
2. 实现相应的处理函数
3. 更新 API 文档

### 3. 修改数据库结构

1. 备份现有数据库
2. 执行 SQL 修改语句
3. 更新数据模型定义

## 部署说明

### 1. 环境要求

- Python 3.8+
- SQLite 3
- go-cqhttp

### 2. 部署步骤

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
export FLASK_APP=app.py
export FLASK_ENV=production
```

3. 启动服务：
```bash
python app.py
```

### 3. 使用 Supervisor 管理进程

创建 `/etc/supervisor/conf.d/linux-notice.conf`：
```ini
[program:linux-notice]
command=python /path/to/app.py
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/linux-notice.err.log
stdout_logfile=/var/log/linux-notice.out.log
```

## 常见问题

1. Q: 数据库连接失败？
   A: 检查数据库文件权限和路径

2. Q: QQ 机器人无法启动？
   A: 检查 go-cqhttp 配置和 QQ 号设置

3. Q: API 返回 500 错误？
   A: 检查日志文件了解详细错误信息

## 技术支持

如有问题，请联系系统管理员或提交 Issue。 
