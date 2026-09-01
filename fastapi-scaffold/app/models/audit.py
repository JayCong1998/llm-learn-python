# 导入创建与更新时间字段所需的日期时间类型。
from datetime import datetime
# 导入协调世界时区对象。
from datetime import timezone

# 导入 SQLAlchemy 布尔列类型。
from sqlalchemy import Boolean
# 导入 SQLAlchemy 日期时间列类型。
from sqlalchemy import DateTime
# 导入 SQLAlchemy 整数列类型。
from sqlalchemy import Integer
# 导入 ORM 映射字段工具。
from sqlalchemy.orm import Mapped
# 导入 ORM 映射列工具。
from sqlalchemy.orm import mapped_column


# 定义全部持久化实体共享的审计、乐观锁与逻辑删除字段。
class AuditMixin:
    # 定义实体创建时间字段。
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    # 定义实体更新时间字段。
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    # 定义供 SQLAlchemy 乐观锁使用的版本字段。
    lock_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # 定义标识实体是否已被逻辑删除的字段。
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
