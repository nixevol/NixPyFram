from fastapi import APIRouter, Query, Body
from pydantic import BaseModel, Field
from app.core.logger import logger
from app.api.deps import *

# 创建自动加载路由器
api_router = APIRouter(prefix="/demo", tags=["示例接口"])


# 请求模型
class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    

# 响应模型
class UserInfo(BaseModel):
    """用户信息"""
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="角色")

# 模拟数据库
users_db = {
    "admin": {
        "user_id": 1,
        "username": "admin",
        "password": "admin123",
        "role": "admin"
    },
    "user": {
        "user_id": 2,
        "username": "user",
        "password": "user123",
        "role": "user"
    }
}

@api_router.get("/success")
@response_wrapper
async def success_demo(
    data_type: str = Query(
        "object",
        description="返回数据类型: object, list, string, number, null"
    )
):
    """
    演示成功响应
    
    不同类型的成功响应示例：
    - object: 返回对象
    - list: 返回列表
    - string: 返回字符串
    - number: 返回数字
    - null: 返回空
    """
    logger.info(f"演示成功响应: data_type={data_type}")
    
    if data_type == "object":
        return {"id": 1, "name": "示例对象"}
    elif data_type == "list":
        return [{"id": 1, "name": "项目1"}, {"id": 2, "name": "项目2"}]
    elif data_type == "string":
        return "这是一个字符串"
    elif data_type == "number":
        return 42
    else:
        return None

@api_router.post("/login")
@response_wrapper
async def login(
    request: LoginRequest = Body(..., description="登录请求")
):
    """
    用户登录
    检查用户名和密码
    """
    logger.info(f"用户登录: {request.username}")
    
    # 验证用户名是否存在
    if request.username not in users_db:
        raise NotFoundError(f"用户不存在: {request.username}")
    
    user = users_db[request.username]
    
    # 验证密码
    if request.password != user["password"]:
        raise PermissionError("密码错误")
    
    # 返回用户信息
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "role": user["role"]
    }

@api_router.get("/admin/users")
@response_wrapper
async def get_users(
    role: Optional[str] = Query(None, description="按角色筛选"),
    current_role: str = "user"  # 模拟当前用户角色
):
    """
    获取用户列表
    只有管理员可以访问
    """
    # 检查权限
    if current_role != "admin":
        raise PermissionError("只有管理员可以访问用户列表")
    
    # 按角色筛选
    if role:
        if role not in ["admin", "user"]:
            raise ValidationError(f"无效的角色值: {role}")
            
        users = [
            user for user in users_db.values()
            if user["role"] == role
        ]
        return {"users": users}
    
    return {"users": list(users_db.values())}

@api_router.post("/users/{user_id}/update")
@response_wrapper
async def update_user(
    user_id: int,
    role: str = Body(..., description="新角色"),
    current_role: str = "user"  # 模拟当前用户角色
):
    """
    更新用户角色
    只有管理员可以修改用户角色
    """
    # 检查权限
    if current_role != "admin":
        raise PermissionError("只有管理员可以修改用户角色")
    
    # 检查用户是否存在
    user = None
    for u in users_db.values():
        if u["user_id"] == user_id:
            user = u
            break
    
    if not user:
        raise NotFoundError(f"用户不存在: {user_id}")
    
    # 检查角色值
    if role not in ["admin", "user"]:
        raise ValidationError(f"无效的角色值: {role}")
    
    # 不允许修改admin用户的角色
    if user["username"] == "admin":
        raise BusinessError(
            "不能修改admin用户的角色",
            detail={"user_id": user_id, "role": role}
        )
    
    # 更新角色
    user["role"] = role
    return user
