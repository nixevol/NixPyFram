# Gateway 服务

基于FastAPI的后端服务框架，用于快速搭建RESTful API服务。

## 特性

- 🚀 基于FastAPI的高性能异步框架
- 📝 完善的日志管理系统
- 🔍 实时日志查看功能
- 🔧 灵活的配置管理
- 🔄 自动路由加载机制

## 项目结构

```path
project/
├─app                     # 应用主目录
│  ├─api                 # API相关
│  │  ├─deps.py         # 依赖注入
│  │  └─v1             # API版本2
│  ├─core              # 核心功能
│  │  ├─config.py     # 配置管理
│  │  ├─logger.py     # 日志管理
│  │  └─errors.py     # 错误处理
│  ├─crud             # 数据库操作层
│  ├─models           # 数据模型
│  ├─schemas          # Pydantic模型
│  ├─services         # 业务逻辑层
│  ├─static           # 静态文件
│  │  └─logs         # 日志查看页面
│  ├─utils            # 工具函数
│  ├─init.py          # 初始化文件
│  └─main.py          # 程序入口
├─logs              # 日志文件
├─config.json       # 配置文件
├─requirements.txt   # 项目依赖
├─run.py            # 启动文件
└─README.md         # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置项目

修改 `config.json` 文件：

```json
{
    "app": {
        "name": "你的应用名称",
        "version": "0.1.0",
        "description": "应用描述",
        "host": "0.0.0.0",
        "port": 8001,
        "reload": true
    }
}
```

### 3. 启动项目

```bash
python run.py
```

## 开发指南

### 路由开发规范

框架支持自动路由加载机制，遵循以下规则：

1. 直接位于 `app/api` 目录下的路由文件：
   ```python
   # app/api/logs.py
   from fastapi import APIRouter
   
   api_router = APIRouter(prefix="/logs", tags=["日志接口"])
   
   @api_router.get("/")
   async def get_logs():
       return {"message": "logs"}
   ```

2. 版本化API路由（位于子目录）：
```python
   # app/api/v1/users.py
   from fastapi import APIRouter
   
   api_router = APIRouter(prefix="/users", tags=["用户接口"])
   
   @api_router.get("/")
   async def get_users():
       return {"message": "users"}
```

路由路径规则：
- `app/api/xxx.py` -> 路由前缀为文件中定义的 prefix
- `app/api/v1/xxx.py` -> 路由前缀为 `/v1` + 文件中定义的 prefix
- `app/api/v2/test/xxx.py` -> 路由前缀为 `/v2/test` + 文件中定义的 prefix

### 代码风格

- 使用 Python 类型注解
- 遵循 PEP 8 编码规范
- 类名使用 PascalCase 命名
- 函数和变量使用 snake_case 命名

### 日志规范

- 使用统一的日志格式
- 合理使用日志级别（DEBUG, INFO, WARNING, ERROR）
- 关键操作必须记录日志
- 异常必须记录详细信息

### 错误处理

- 使用统一的错误响应格式
- 所有异常必须被捕获并处理
- 提供有意义的错误信息

## 内置功能

### 1. 统一响应格式

所有API响应都使用统一的格式：

```json
{
    "code": 200,
    "message": "success",
    "data": {}
}
```

### 2. 日志系统

#### 日志接口

1. 获取日志页面
```web
GET /logs
```

2. 获取日志文件列表
```web
GET /logs/files
```

3. 获取日志内容
```web
GET /logs/content/{filename}
```
参数：
- `filename`: 日志文件名
- `page`: 页码（默认1）
- `page_size`: 每页条数（默认100）

4. WebSocket实时日志
```web
WS /logs/ws
```

### 3. 系统信息

1. 获取应用信息
```web
GET /
```

2. 健康检查
```web
GET /health
```

## API文档

启动服务后访问：
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- OpenAPI: `http://localhost:8001/openapi.json`
