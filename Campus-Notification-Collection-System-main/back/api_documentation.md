# Linux文件系统管理系统 - 后端API文档

## 基础信息
- 基础URL: `http://localhost:5000/api`
- 所有响应格式均为JSON
- 错误响应格式：
```json
{
    "error": "错误信息描述"
}
```

## 接口列表

### 1. 文件系统操作

#### 1.1 获取目录内容
- **接口**: `GET /files`
- **描述**: 获取指定目录下的所有文件和子目录
- **参数**: 
  - `path` (query string): 目录路径，默认为根目录 "/"
- **响应**:
```json
{
    "files": [
        {
            "name": "example.txt",
            "type": "file",
            "size": 1024,
            "permissions": "rwxr-xr-x",
            "owner": "user",
            "group": "group",
            "lastModified": "2024-03-20T10:00:00Z"
        },
        {
            "name": "documents",
            "type": "directory",
            "permissions": "rwxr-xr-x",
            "owner": "user",
            "group": "group",
            "lastModified": "2024-03-20T10:00:00Z"
        }
    ]
}
```

#### 1.2 创建新目录
- **接口**: `POST /directory`
- **描述**: 在指定路径创建新目录
- **请求体**:
```json
{
    "path": "/path/to/new/directory",
    "permissions": "755"  // 可选
}
```
- **响应**:
```json
{
    "success": true,
    "path": "/path/to/new/directory"
}
```

#### 1.3 删除文件/目录
- **接口**: `DELETE /files`
- **描述**: 删除指定的文件或目录
- **请求体**:
```json
{
    "path": "/path/to/file/or/directory",
    "recursive": true  // 如果是目录，是否递归删除
}
```
- **响应**:
```json
{
    "success": true,
    "path": "/path/to/file/or/directory"
}
```

#### 1.4 移动/重命名文件
- **接口**: `PUT /files/move`
- **描述**: 移动或重命名文件/目录
- **请求体**:
```json
{
    "sourcePath": "/path/to/source",
    "destinationPath": "/path/to/destination"
}
```
- **响应**:
```json
{
    "success": true,
    "source": "/path/to/source",
    "destination": "/path/to/destination"
}
```

#### 1.5 修改文件权限
- **接口**: `PUT /files/permissions`
- **描述**: 修改文件或目录的权限
- **请求体**:
```json
{
    "path": "/path/to/file",
    "permissions": "755",
    "recursive": false  // 可选，是否递归修改子目录权限
}
```
- **响应**:
```json
{
    "success": true,
    "path": "/path/to/file",
    "permissions": "755"
}
```

### 2. 文件内容操作

#### 2.1 读取文件内容
- **接口**: `GET /files/content`
- **描述**: 读取文件内容
- **参数**: 
  - `path` (query string): 文件路径
- **响应**:
```json
{
    "content": "文件内容",
    "encoding": "utf-8"
}
```

#### 2.2 写入/更新文件内容
- **接口**: `PUT /files/content`
- **描述**: 写入或更新文件内容
- **请求体**:
```json
{
    "path": "/path/to/file",
    "content": "新的文件内容",
    "encoding": "utf-8"  // 可选
}
```
- **响应**:
```json
{
    "success": true,
    "path": "/path/to/file",
    "size": 1024
}
```

### 3. 搜索功能

#### 3.1 搜索文件
- **接口**: `GET /search`
- **描述**: 搜索文件和目录
- **参数**: 
  - `query` (query string): 搜索关键词
  - `path` (query string, 可选): 搜索起始路径
  - `type` (query string, 可选): 文件类型筛选 ("file" 或 "directory")
- **响应**:
```json
{
    "results": [
        {
            "path": "/path/to/match1",
            "type": "file",
            "size": 1024,
            "lastModified": "2024-03-20T10:00:00Z"
        },
        {
            "path": "/path/to/match2",
            "type": "directory",
            "lastModified": "2024-03-20T10:00:00Z"
        }
    ]
}
```

### 4. 系统信息

#### 4.1 获取系统信息
- **接口**: `GET /system/info`
- **描述**: 获取系统基本信息
- **响应**:
```json
{
    "totalSpace": 1000000000,
    "freeSpace": 500000000,
    "usedSpace": 500000000,
    "rootDirectory": "/",
    "osType": "Linux",
    "osVersion": "5.10.0"
}
```

## 错误码说明

- 200: 请求成功
- 400: 请求参数错误
- 401: 未授权
- 403: 权限不足
- 404: 文件或目录不存在
- 409: 操作冲突（如创建已存在的目录）
- 500: 服务器内部错误

## 注意事项

1. 所有路径参数都应该是绝对路径
2. 文件权限使用八进制字符串表示（如 "755"）
3. 涉及文件内容的操作默认使用UTF-8编码
4. 大文件操作可能需要特殊处理，建议添加文件大小限制
5. 某些操作可能需要管理员权限 