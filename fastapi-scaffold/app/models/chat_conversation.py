# 导入关系字段类型。
from typing import TYPE_CHECKING

# 导入 SQLAlchemy 外键约束工具。
from sqlalchemy import ForeignKey
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

# 仅在类型检查时导入关联模型以避免循环导入。
if TYPE_CHECKING:
    # 导入消息模型类型。
    from app.models.chat_message import ChatMessage
    # 导入用户模型类型。
    from app.models.user import User


# 定义用户 LLM 对话会话数据库模型。
class ChatConversation(AuditMixin, Base):
    # 指定对话会话表名称。
    __tablename__ = "chat_conversation"

    # 定义对话会话主键。
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 定义会话所属用户外键。
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="RESTRICT"), nullable=False, index=True)
    # 定义可选会话标题。
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # 配置更新时自动校验并递增乐观锁版本。
    __mapper_args__ = {"version_id_col": AuditMixin.lock_version}
    # 定义会话与所属用户的多对一关系。
    user: Mapped["User"] = relationship(back_populates="conversations")
    # 定义会话与消息的一对多关系。
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="conversation")
