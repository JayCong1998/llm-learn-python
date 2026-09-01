# 导入 SQLAlchemy 会话类型。
from sqlalchemy.orm import Session

# 导入密码散列与令牌函数。
from app.core.security import create_access_token
# 导入密码散列函数。
from app.core.security import hash_password
# 导入密码校验函数。
from app.core.security import verify_password
# 导入用户模型。
from app.models.user import User
# 导入用户仓储。
from app.repositories.user_repository import UserRepository
# 导入认证失败异常。
from app.services.exceptions import AuthenticationError
# 导入冲突异常。
from app.services.exceptions import ConflictError
# 导入令牌响应模型。
from app.schemas.auth import TokenResponse
# 导入登录请求模型。
from app.schemas.auth import UserLogin
# 导入注册请求模型。
from app.schemas.auth import UserRegister


# 编排认证相关的业务规则和事务。
class AuthService:
    # 初始化服务使用的会话与仓储。
    def __init__(self, database_session: Session) -> None:
        # 保存当前业务会话。
        self.database_session = database_session
        # 创建用户数据访问对象。
        self.user_repository = UserRepository(database_session)

    # 注册默认普通用户。
    def register(self, payload: UserRegister) -> User:
        # 查询重复的用户名或邮箱。
        if self.user_repository.find_by_username_or_email(payload.username, payload.email) is not None:
            # 返回业务冲突。
            raise ConflictError("用户名或邮箱已存在")
        # 创建带安全密码哈希的用户。
        user = User(username=payload.username, email=payload.email, password_hash=hash_password(payload.password), role="user")
        # 持久化新用户。
        self.user_repository.add(user)
        # 提交用户事务。
        self.database_session.commit()
        # 刷新数据库生成字段。
        self.database_session.refresh(user)
        # 返回注册用户。
        return user

    # 校验登录并签发令牌。
    def login(self, payload: UserLogin) -> TokenResponse:
        # 查询指定用户名用户。
        user = self.user_repository.find_by_username(payload.username)
        # 拒绝不存在用户或错误密码。
        if user is None or not verify_password(payload.password, user.password_hash):
            # 返回认证失败。
            raise AuthenticationError("用户名或密码错误")
        # 生成 Bearer 令牌响应。
        return TokenResponse(access_token=create_access_token({"sub": user.username, "role": user.role}), token_type="bearer")
