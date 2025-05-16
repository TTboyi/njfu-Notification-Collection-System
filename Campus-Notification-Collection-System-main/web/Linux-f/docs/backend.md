# 后端说明文档

## 技术栈
- 框架：Express.js
- 数据库：MySQL
- ORM：Sequelize
- 认证：JWT
- 开发语言：TypeScript
- 构建工具：ts-node

## 项目结构
```
src/
  ├── config/        # 配置文件
  ├── controllers/   # 控制器
  ├── models/        # 数据模型
  ├── routes/        # 路由
  ├── middlewares/   # 中间件
  ├── utils/         # 工具函数
  └── app.ts         # 应用入口
```

## 数据库设计

### 用户表 (users)
```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL UNIQUE,
  account VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role ENUM('user', 'admin') DEFAULT 'user',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 通知表 (notifications)
```sql
CREATE TABLE notifications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 收藏表 (favorites)
```sql
CREATE TABLE favorites (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  notification_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (notification_id) REFERENCES notifications(id) ON DELETE CASCADE,
  UNIQUE KEY unique_favorite (user_id, notification_id)
);
```

## API接口文档

### 1. 认证接口

#### 登录
```typescript
POST /api/auth/login
Request:
{
  username: string;
  password: string;
  userType: 'user' | 'admin';
}
Response:
成功：
{
  code: 200,
  data: {
    user: {
      id: number;
      username: string;
      account: string;
      role: 'user' | 'admin';
    },
    token: string;
  }
}
失败：
{
  code: 400,
  message: string;
}
```

#### 注册
```typescript
POST /api/auth/register
Request:
{
  username: string;
  password: string;
}
Response:
成功：
{
  code: 200,
  data: {
    user: {
      id: number;
      username: string;
      account: string;
      role: 'user';
    },
    token: string;
  }
}
失败：
{
  code: 400,
  message: string;
}
```

### 2. 管理员接口

#### 获取用户列表
```typescript
GET /api/admin/users
Response:
成功：
{
  code: 200,
  data: User[];
}
失败：
{
  code: 401,
  message: '未授权';
}
```

#### 删除用户
```typescript
DELETE /api/admin/users/:id
Response:
成功：
{
  code: 200,
  data: { success: true };
}
失败：
{
  code: 400 | 401,
  message: string;
}
```

#### 获取通知列表
```typescript
GET /api/admin/notifications
Response:
成功：
{
  code: 200,
  data: Notification[];
}
失败：
{
  code: 401,
  message: '未授权';
}
```

#### 添加通知
```typescript
POST /api/admin/notifications
Request:
{
  title: string;
  content: string;
}
Response:
成功：
{
  code: 200,
  data: Notification;
}
失败：
{
  code: 400 | 401,
  message: string;
}
```

#### 删除通知
```typescript
DELETE /api/admin/notifications/:id
Response:
成功：
{
  code: 200,
  data: { success: true };
}
失败：
{
  code: 400 | 401,
  message: string;
}
```

### 3. 用户接口

#### 获取收藏列表
```typescript
GET /api/user/favorites
Response:
成功：
{
  code: 200,
  data: Notification[];
}
失败：
{
  code: 401,
  message: '未授权';
}
```

#### 添加收藏
```typescript
POST /api/user/favorites/:notificationId
Response:
成功：
{
  code: 200,
  data: { success: true };
}
失败：
{
  code: 400 | 401,
  message: string;
}
```

#### 删除收藏
```typescript
DELETE /api/user/favorites/:notificationId
Response:
成功：
{
  code: 200,
  data: { success: true };
}
失败：
{
  code: 400 | 401,
  message: string;
}
```

## 环境要求
- Node.js >= 16
- MySQL >= 8.0
- npm >= 8

## 安装和运行
1. 安装依赖
```bash
npm install
```

2. 配置数据库
- 创建数据库
- 修改 `src/config/database.ts` 中的数据库配置

3. 运行数据库迁移
```bash
npm run migrate
```

4. 开发环境运行
```bash
npm run dev
```

5. 生产环境运行
```bash
npm run build
npm start
``` 