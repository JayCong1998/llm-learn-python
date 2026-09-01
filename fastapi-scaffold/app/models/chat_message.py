# 导入关系字段类型。
from typing import TYPE_CHECKING

# 导入 SQLAlchemy 检查约束工具。
from sqlalchemy import CheckConstraint
# 导入 SQLAlchemy 外键约束工具。
from sqlalchemy import ForeignKey
# 导入 SQLAlchemy 整数列类型。
from sqlalchemy import Integer
# 导入 SQLAlchemy 字符串列类型。
from sqlalchemy import String
# 导入 SQLAlchemy 文本列类型。
from sqlalchemy import Text
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
    # 导入会话模型类型。
    from app.models.chat_conversation import ChatConversation
    # 导入大模型调用日志模型类型。
    from app.models.llm_call_log import LlmCallLog


# 定义 LLM 对话消息数据库模型。
class ChatMessage(AuditMixin, Base):
    # 指定对话消息表名称。
    __tablename__ = "chat_message"
    # 定义限制消息角色取值范围的数据库约束。
    __table_args__ = (CheckConstraint("role IN ('system', 'user', 'assistant')", name="ck_chat_message_role"),)

    # 定义对话消息主键。
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 定义消息所属会话外键。
    conversation_id: Mapped[int] = mapped_column(ForeignKey("chat_conversation.id", ondelete="RESTRICT"), nullable=False, index=True)
    # 定义消息角色字段。
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    # 定义消息正文内容字段。
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 配置更新时自动校验并递增乐观锁版本。
    __mapper_args__ = {"version_id_col": AuditMixin.lock_version}
    # 定义消息与所属会话的多对一关系。
    conversation: Mapped["ChatConversation"] = relationship(back_populates="messages")
    # 定义消息与模型调用日志的一对一关系。
    llm_call_log: Mapped["LlmCallLog | None"] = relationship(back_populates="message", uselist=False)
