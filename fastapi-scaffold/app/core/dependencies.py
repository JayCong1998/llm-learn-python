# 导入注入数据库依赖的注解工具。
from typing import Annotated

# 导入 FastAPI 依赖注入工具。
from fastapi import Depends
# 导入 HTTP Bearer 认证解析工具。
from fastapi.security import OAuth2PasswordBearer
# 导入 PyJWT 异常类型。
from jwt import InvalidTokenError
# 导入 SQLAlchemy 查询构造工具。
from sqlalchemy import select
# 导入 SQLAlchemy 会话类型。
from sqlalchemy.orm import Session

# 导入数据库请求依赖。
from app.core.database import get_db
# 导入 JWT 解码函数。
from app.core.security import decode_access_token
# 导入用户数据库模型。
from app.models.user import User
# 导入认证失败异常。
from app.services.exceptions import AuthenticationError
# 导入授权失败异常。
from app.services.exceptions import AuthorizationError

# 定义从 Bearer 请求头提取令牌的认证方案。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# 定义数据库会话的复用注解。
DatabaseSession = Annotated[Session, Depends(get_db)]


# 获取并校验当前请求所属用户。
def get_current_user(database_session: DatabaseSession, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    # 尝试解码并校验 JWT。
    try:
        # 读取令牌中的用户名主体。
        username = decode_access_token(token).get("sub")
    # 将任意 JWT 校验失败转换为认证失败。
    except InvalidTokenError as error:
        # 抛出不泄露内部信息的认证异常。
        raise AuthenticationError("无效或过期的访问令牌") from error
    # 拒绝缺失用户主体的令牌。
    if not username:
        # 抛出认证异常。
        raise AuthenticationError("无效或过期的访问令牌")
    # 根据令牌主体查询当前用户。
    current_user = database_session.scalar(select(User).where(User.username == username))
    # 拒绝已不存在的令牌用户。
    if current_user is None:
        # 抛出认证异常。
        raise AuthenticationError("无效或过期的访问令牌")
    # 返回已经验证的当前用户。
    return current_user


# 验证当前用户拥有管理员角色。
def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    # 拒绝非管理员角色的用户。
    if current_user.role != "admin":
        # 抛出禁止访问异常。
        raise AuthorizationError("需要管理员权限")
    # 返回已验证管理员用户。
    return current_user
