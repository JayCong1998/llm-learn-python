# 导入依赖注入注解工具。
from typing import Annotated

# 导入 FastAPI 路由类。
from fastapi import APIRouter
# 导入 FastAPI 依赖注入工具。
from fastapi import Depends
# 导入 FastAPI HTTP 异常类型。
from fastapi import HTTPException
# 导入 HTTP 状态码常量。
from fastapi import status
# 导入 SQLAlchemy 查询构造工具。
from sqlalchemy import or_
# 导入 SQLAlchemy 查询构造工具。
from sqlalchemy import select

# 导入管理员权限依赖。
from app.core.dependencies import require_admin
# 导入数据库会话注解。
from app.core.dependencies import DatabaseSession
# 导入访问令牌创建函数。
from app.core.security import create_access_token
# 导入密码哈希函数。
from app.core.security import hash_password
# 导入密码校验函数。
from app.core.security import verify_password
# 导入用户数据库模型。
from app.models.user import User
# 导入令牌响应模型。
from app.schemas.auth import TokenResponse
# 导入用户登录请求模型。
from app.schemas.auth import UserLogin
# 导入用户读取响应模型。
from app.schemas.auth import UserRead
# 导入用户注册请求模型。
from app.schemas.auth import UserRegister

# 创建认证功能路由。
router = APIRouter(prefix="/auth", tags=["auth"])


# 注册新用户并默认赋予普通用户角色。
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
# 定义用户注册处理函数。
def register_user(payload: UserRegister, database_session: DatabaseSession) -> User:
    # 检查用户名或邮箱是否已被使用。
    existing_user = database_session.scalar(select(User).where(or_(User.username == payload.username, User.email == payload.email)))
    # 拒绝重复的用户名或邮箱。
    if existing_user is not None:
        # 返回资源冲突响应。
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名或邮箱已存在")
    # 创建密码已哈希且角色为普通用户的实体。
    user = User(username=payload.username, email=payload.email, password_hash=hash_password(payload.password), role="user")
    # 将新用户加入当前事务。
    database_session.add(user)
    # 提交用户数据。
    database_session.commit()
    # 刷新实体以读取数据库生成的字段。
    database_session.refresh(user)
    # 返回安全的用户信息。
    return user


# 校验用户名密码并返回 Bearer JWT。
@router.post("/login", response_model=TokenResponse)
# 定义用户登录处理函数。
def login_user(payload: UserLogin, database_session: DatabaseSession) -> TokenResponse:
    # 根据用户名查询用户实体。
    user = database_session.scalar(select(User).where(User.username == payload.username))
    # 拒绝不存在用户或密码校验失败的登录。
    if user is None or not verify_password(payload.password, user.password_hash):
        # 返回不泄露用户名存在性的认证失败响应。
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误", headers={"WWW-Authenticate": "Bearer"})
    # 创建携带用户主体与角色的访问令牌。
    access_token = create_access_token({"sub": user.username, "role": user.role})
    # 返回标准 Bearer 令牌响应。
    return TokenResponse(access_token=access_token, token_type="bearer")


# 提供用于验证管理员权限依赖的最小写入端点。
@router.post("/admin-probe", status_code=status.HTTP_204_NO_CONTENT)
# 定义管理员探针处理函数。
def admin_probe(current_user: Annotated[User, Depends(require_admin)]) -> None:
    # 显式引用依赖结果以表明权限已完成校验。
    _ = current_user
