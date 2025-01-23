import os
import uuid
import hashlib
import importlib
from pathlib import Path
from typing import Dict, Any
from app.core.logger import log
from app.core.config import config
from app.core.errors import AppError
from app.core.events import event_manager
from app.api.deps import response_wrapper
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.schemas.response import ResponseModel
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware

# 设置应用入口点
event_manager.set_entry_point(config.get("app.main", "app.main"))

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    应用生命周期管理
    处理应用启动和关闭时的事件
    """
    app_id = int(hashlib.sha256(str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode()))).encode()).hexdigest(), 26) % 10**16
    app_id = f"{app_id:016x}"
    config.set("app.id", app_id)
    try:
        await event_manager.run_startup(_app)
        yield
    finally:
        await event_manager.run_shutdown(_app)

# 创建FastAPI应用
app = FastAPI(
    title=config.get("app.name"),
    description=config.get("app.description"),
    version=config.get("app.version"),
    docs_url="/docs",      # Swagger UI路径
    redoc_url="/redoc",    # ReDoc路径
    openapi_url="/openapi.json",  # OpenAPI规范JSON路径
    lifespan=lifespan,
    openapi_tags=[{"name": "日志", "description": "👉[访问日志控制台](/logs)"}],
)

# 配置CORS
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    """
    应用异常处理器
    处理自定义异常，返回统一的错误响应格式
    """
    return JSONResponse(
        status_code=200,  # 统一使用200状态码，通过code字段区分错误
        content=ResponseModel(
            code=exc.error_code,
            msg=exc.error_msg,
            data=exc.error_detail
        ).model_dump()
    )


def load_routers():
    """
    自动加载所有API路由
    扫描app/api目录下所有的python文件，并导入其中的api_router
    路由前缀将基于文件所在的目录路径，例如：
    - app/api/v1/xxx.py 的路由前缀为 /v1
    - app/api/logs.py 的路由前缀为 /logs
    - app/api/v2/test/demo.py 的路由前缀为 /v2/test
    """
    routers = []
    api_dir = Path(__file__).parent / "api"
    
    # 递归处理所有Python文件
    for api_file in api_dir.rglob("*.py"):
        if api_file.stem in ["__init__", "deps"]:
            continue
            
        try:
            # 计算相对于api目录的路径
            rel_path = api_file.relative_to(api_dir)
            module_path = f"app.api.{'.'.join(rel_path.with_suffix('').parts)}"
            
            # 动态导入模块
            module = importlib.import_module(module_path)
            if hasattr(module, "api_router"):
                router = APIRouter()
                # 如果不是直接位于api目录下，添加目录前缀
                dir_prefix = "" if api_file.parent == api_dir else "/" + str(rel_path.parent).replace(os.sep, "/")
                router.include_router(module.api_router, prefix=dir_prefix)
                routers.append(router)
                
                # 获取完整的路由地址
                module_prefix = getattr(module.api_router, "prefix", "")
                log.info(f"成功加载路由模块: {module_path}，路由地址: {dir_prefix}{module_prefix}")
        except Exception as e:
            log.error(f"加载路由模块失败 {module_path}: {str(e)}")
    
    return routers


@app.get("/", response_model=ResponseModel[Dict[str, Any]], summary="程序信息")
@response_wrapper
async def root():
    """
    获取程序信息
    """
    return {
        "app_name": config.get("app.name"),
        "app_id": config.get("app.id", ""),
        "version": config.get("app.version"),
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

@app.get("/health", response_model=ResponseModel[Dict[str, Any]], summary="环境状态检查")
@response_wrapper
async def health_check():
    """
    健康检查接口
    返回系统健康状态和资源使用情况
    
    返回信息包括：
    - 系统状态
    - CPU使用率
    - 内存使用情况
    - 磁盘使用情况
    - 系统运行时间
    """
    return SystemInfo.get_system_stats()


 # 自动加载所有路由
routers = load_routers()
for router in routers:
    app.include_router(router)