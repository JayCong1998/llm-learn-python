# 导入 SQLAlchemy 条件组合工具。
from sqlalchemy import or_
# 导入 SQLAlchemy 查询构造工具。
from sqlalchemy import select
# 导入 SQLAlchemy 会话类型。
from sqlalchemy.orm import Session

# 导入用户 ORM 模型。
from app.models.user import User


# 封装用户实体的数据访问操作。
class UserRepository:
    # 保存当前请求数据库会话。
    def __init__(self, database_session: Session) -> None:
        # 记录仓储使用的会话。
        self.database_session = database_session

    # 按用户名查询用户实体。
    def find_by_username(self, username: str) -> User | None:
        # 返回匹配用户名的单个用户。
        return self.database_session.scalar(select(User).where(User.username == username))

    # 按用户名或邮箱查询用户实体。
    def find_by_username_or_email(self, username: str, email: str) -> User | None:
        # 返回匹配任一唯一字段的单个用户。
        return self.database_session.scalar(select(User).where(or_(User.username == username, User.email == email)))

    # 将用户标记为待持久化实体。
    def add(self, user: User) -> None:
        # 加入当前会话而不提交事务。
        self.database_session.add(user)
