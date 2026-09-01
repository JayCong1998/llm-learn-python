# 导入关系字段类型。
from typing import TYPE_CHECKING

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

# 仅在类型检查时导入消息模型以避免循环导入。
if TYPE_CHECKING:
    # 导入消息模型类型。
    from app.models.chat_message import ChatMessage


# 定义每条助手消息对应的大模型调用日志数据库模型。
class LlmCallLog(AuditMixin, Base):
    # 指定大模型调用日志表名称。
    __tablename__ = "llm_call_log"

    # 定义调用日志主键。
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 定义关联助手消息且保持一对一关系的外键。
    message_id: Mapped[int] = mapped_column(ForeignKey("chat_message.id", ondelete="RESTRICT"), nullable=False, unique=True)
    # 定义调用服务商名称字段。
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    # 定义调用模型名称字段。
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    # 定义本次调用状态字段。
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    # 定义输入令牌数量字段。
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 定义输出令牌数量字段。
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 定义模型调用耗时毫秒数字段。
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 定义可选调用错误描述字段。
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 配置更新时自动校验并递增乐观锁版本。
    __mapper_args__ = {"version_id_col": AuditMixin.lock_version}
    # 定义调用日志与生成消息的一对一关系。
    message: Mapped["ChatMessage"] = relationship(back_populates="llm_call_log")
