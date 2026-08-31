# 导入创建时间字段所需的日期时间类型。
from datetime import datetime
# 导入协调世界时区对象。
from datetime import timezone

# 导入 SQLAlchemy 日期时间列类型。
from sqlalchemy import DateTime
# 导入 SQLAlchemy 整数列类型。
from sqlalchemy import Integer
# 导入 SQLAlchemy 字符串列类型。
from sqlalchemy import String
# 导入 ORM 映射字段工具。
from sqlalchemy.orm import Mapped
# 导入 ORM 映射列工具。
from sqlalchemy.orm import mapped_column

# 导入项目 ORM 基类。
from app.core.database import Base


# 定义系统用户数据库模型。
class User(Base):
    # 指定用户表名称。
    __tablename__ = "users"

    # 定义用户主键。
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 定义唯一用户名字段。
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    # 定义唯一邮箱字段。
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    # 定义密码哈希字段。
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # 定义用户角色字段。
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    # 定义用户创建时间字段。
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
