# Linux 通知系统前端

## 项目结构

```
web/Linux-f/
├── src/
│   ├── components/     # 公共组件
│   ├── pages/         # 页面组件
│   ├── services/      # API 服务
│   ├── types/         # TypeScript 类型定义
│   ├── data/          # 模拟数据
│   └── utils/         # 工具函数
├── public/            # 静态资源
└── package.json       # 项目依赖
```

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm start
```

访问 http://localhost:3000 查看应用。

## 功能模块说明

### 1. 通知分类配置

通知分类在以下文件中配置：

1. 类型定义：`src/types/index.ts`
```typescript
export type NoticeType = '通知' | '讲座' | '比赛' | '实习';
```

2. 通知列表筛选：`src/pages/NoticeList.tsx`
```typescript
<Select value={typeFilter} onChange={value => setTypeFilter(value as NoticeType | 'all')}>
  <Option value="all">所有类型</Option>
  <Option value="通知">通知</Option>
  <Option value="讲座">讲座</Option>
  <Option value="比赛">比赛</Option>
  <Option value="实习">实习</Option>
</Select>
```

3. 管理员添加通知：`src/pages/Admin.tsx`
```typescript
<Select>
  <Option value="通知">通知</Option>
  <Option value="活动通知">活动通知</Option>
  <Option value="安全通知">安全通知</Option>
</Select>
```

### 2. 数据管理

#### 2.1 模拟数据

模拟数据位于 `src/data/mockNotices.ts`，用于开发和测试：

```typescript
export const mockNotices: Notice[] = [
  {
    id: 1,
    title: '系统维护通知',
    content: '系统将于本周六凌晨2点进行例行维护，预计持续2小时。',
    source: '系统管理员',
    category: '通知',
    publish_date: '2024-03-20',
    views: 156,
    favorites: 15,
    link: 'https://example.com/maintenance'
  },
  // ... 更多通知
];
```

#### 2.2 API 服务

API 服务位于 `src/services/api.ts`，包含与后端通信的方法：

```typescript
// 获取通知列表
export const getNotices = () => axios.get('/api/notices');

// 获取比赛信息
export const getCompetitions = () => axios.get('/api/competitions');

// 获取考试信息
export const getExams = () => axios.get('/api/exams');

// 获取实习信息
export const getInternships = () => axios.get('/api/internships');
```

### 3. 后端集成

#### 3.1 环境配置

在 `src/services/api.ts` 中配置后端 API 地址：

```typescript
import axios from 'axios';

// 配置默认的 API 地址
axios.defaults.baseURL = 'http://localhost:5000';
```

#### 3.2 数据格式

后端 API 返回的数据格式应为：

```typescript
interface ApiResponse<T> {
  data: T[];
  message?: string;
  status: number;
}
```

### 4. 数据提取

#### 4.1 数据库结构

通知表结构：
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

#### 4.2 数据提取脚本

使用 Python 脚本从数据库提取数据：

```python
import sqlite3
import json

def extract_notices():
    conn = sqlite3.connect('notices.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM notices')
    notices = cursor.fetchall()
    
    # 转换为前端需要的格式
    formatted_notices = [
        {
            'id': notice[0],
            'title': notice[1],
            'content': notice[2],
            'publish_date': notice[3],
            'category': notice[4],
            'source': notice[5],
            'link': notice[6],
            'views': notice[7],
            'favorites': notice[8]
        }
        for notice in notices
    ]
    
    # 保存为 JSON 文件
    with open('notices.json', 'w', encoding='utf-8') as f:
        json.dump(formatted_notices, f, ensure_ascii=False, indent=2)
    
    conn.close()

if __name__ == '__main__':
    extract_notices()
```

## 开发指南

### 1. 添加新的通知类型

1. 在 `src/types/index.ts` 中更新 `NoticeType` 类型：
```typescript
export type NoticeType = '通知' | '讲座' | '比赛' | '实习' | '新类型';
```

2. 在 `src/pages/NoticeList.tsx` 中添加新的选项：
```typescript
<Option value="新类型">新类型</Option>
```

3. 在 `src/pages/Admin.tsx` 中添加新的选项：
```typescript
<Option value="新类型">新类型</Option>
```

### 2. 修改通知来源

1. 在 `src/types/index.ts` 中更新 `NoticeSource` 类型：
```typescript
export type NoticeSource = '官网' | 'QQ群' | '管理员' | '新来源';
```

2. 在 `src/pages/NoticeList.tsx` 中添加新的选项：
```typescript
<Option value="新来源">新来源</Option>
```

## 部署说明

### 1. 构建生产版本

```bash
npm run build
```

### 2. 配置后端 API

1. 确保后端服务正在运行
2. 在 `src/services/api.ts` 中更新 API 地址为生产环境地址

### 3. 部署到服务器

1. 将 `build` 目录下的文件复制到 Web 服务器
2. 配置服务器以支持 React Router 的客户端路由

## 常见问题

1. Q: 如何修改通知分类？
   A: 修改 `src/types/index.ts` 中的 `NoticeType` 类型定义，并在相应的组件中更新选项。

2. Q: 如何添加新的数据源？
   A: 在 `src/services/api.ts` 中添加新的 API 方法，并在相应的组件中调用。

3. Q: 如何修改通知显示格式？
   A: 修改 `src/pages/NoticeList.tsx` 中的渲染逻辑。

## 技术支持

如有问题，请联系系统管理员或提交 Issue。 