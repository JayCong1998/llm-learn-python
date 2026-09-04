# 导入依赖注入注解工具。
from typing import Annotated
# 导入 FastAPI 路由类。
from fastapi import APIRouter
# 导入依赖注入工具。
from fastapi import Depends
# 导入 HTTP 状态码常量。
from fastapi import status
# 导入统一响应路由类。
from app.core.api_response import EnvelopeRoute
# 导入管理员权限依赖。
from app.core.dependencies import require_admin
# 导入数据库会话注解。
from app.core.dependencies import DatabaseSession
# 导入认证服务。
from app.services.auth_service import AuthService
# 导入令牌响应模型。
from app.schemas.auth import TokenResponse
# 导入登录请求模型。
from app.schemas.auth import UserLogin
# 导入用户读取模型。
from app.schemas.auth import UserRead
# 导入注册请求模型。
from app.schemas.auth import UserRegister

# 创建认证功能路由并启用统一成功响应。
router = APIRouter(prefix="/auth", tags=["auth"], route_class=EnvelopeRoute)

# 注册默认普通用户。
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
# 定义注册接口。
def register_user(payload: UserRegister, database_session: DatabaseSession) -> UserRead:
    # 创建认证服务。
    service = AuthService(database_session)
    # 返回注册成功用户。
    return service.register(payload)

# 校验凭据并返回 Bearer 令牌。
@router.post("/login", response_model=TokenResponse)
# 定义登录接口。
def login_user(payload: UserLogin, database_session: DatabaseSession) -> TokenResponse:
    # 创建认证服务。
    service = AuthService(database_session)
    # 返回签发的令牌。
    return service.login(payload)

# 提供管理员权限探针。
@router.post("/admin-probe", status_code=status.HTTP_204_NO_CONTENT)
# 定义管理员探针接口。
def admin_probe(current_user: Annotated[object, Depends(require_admin)]) -> None:
    # 显式引用权限校验结果。
    _ = current_user
