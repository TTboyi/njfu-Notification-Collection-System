# 前端说明文档

## 技术栈
- 框架：React 18
- UI组件库：Ant Design 5.x
- 路由：React Router 6
- 状态管理：React Hooks
- 开发语言：TypeScript
- 构建工具：Vite

## 项目结构
```
src/
  ├── components/     # 公共组件
  ├── pages/         # 页面组件
  ├── types/         # TypeScript类型定义
  ├── App.tsx        # 应用入口
  └── index.tsx      # 渲染入口
```

## 主要功能模块

### 1. 登录模块 (src/pages/Login.tsx)
- 用户登录
- 管理员登录
- 游客登录
- 用户注册

### 2. 管理员模块 (src/pages/Admin.tsx)
- 用户管理（查看、删除用户）
- 通知管理（添加、删除通知）

### 3. 用户中心模块
- 收藏夹管理
- 通知查看

## 后端接口需求

### 1. 认证接口
```typescript
// 登录
POST /api/auth/login
Request:
{
  username: string;
  password: string;
  userType: 'user' | 'admin';
}
Response:
{
  user: User;
  token: string;
}

// 注册
POST /api/auth/register
Request:
{
  username: string;
  password: string;
}
Response:
{
  user: User;
  token: string;
}
```

### 2. 管理员接口
```typescript
// 获取用户列表
GET /api/admin/users
Response: User[]

// 删除用户
DELETE /api/admin/users/:id
Response: { success: boolean }

// 获取通知列表
GET /api/admin/notifications
Response: Notification[]

// 添加通知
POST /api/admin/notifications
Request:
{
  title: string;
  content: string;
}
Response: Notification

// 删除通知
DELETE /api/admin/notifications/:id
Response: { success: boolean }
```

### 3. 用户接口
```typescript
// 获取收藏列表
GET /api/user/favorites
Response: Notification[]

// 添加收藏
POST /api/user/favorites/:notificationId
Response: { success: boolean }

// 删除收藏
DELETE /api/user/favorites/:notificationId
Response: { success: boolean }
```

## 环境要求
- Node.js >= 16
- npm >= 8

## 安装和运行
1. 安装依赖
```bash
npm install
```

2. 开发环境运行
```bash
npm run dev
```

3. 生产环境构建
```bash
npm run build
``` 