# 导入关系字段类型。
from typing import TYPE_CHECKING

# 导入 SQLAlchemy 整数列类型。
from sqlalchemy import Integer
# 导入 SQLAlchemy 字符串列类型。
from sqlalchemy import String
# 导入 ORM 映射字段工具。
from sqlalchemy.orm import Mapped
# 导入 ORM 映射列工具。
from sqlalchemy.orm import mapped_column
# 导入 ORM 关系工具。
from sqlalchemy.orm import relationship

# 导入公共持久化字段混入类。
from app.models.audit import AuditMixin
# 导入项目 ORM 基类。
from app.core.database import Base

# 仅在类型检查时导入会话模型以避免循环导入。
if TYPE_CHECKING:
    # 导入会话模型类型。
    from app.models.chat_conversation import ChatConversation


# 定义系统用户数据库模型。
class User(AuditMixin, Base):
    # 指定用户表名称。
    __tablename__ = "user"

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
    # 配置更新时自动校验并递增乐观锁版本。
    __mapper_args__ = {"version_id_col": AuditMixin.lock_version}
    # 定义用户与会话的一对多关系。
    conversations: Mapped[list["ChatConversation"]] = relationship(back_populates="user")
