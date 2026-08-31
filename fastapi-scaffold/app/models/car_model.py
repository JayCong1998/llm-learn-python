# 导入创建与更新时间字段所需的日期时间类型。
from datetime import datetime
# 导入协调世界时区对象。
from datetime import timezone
# 导入精确金额字段类型。
from decimal import Decimal
# 导入关系字段类型。
from typing import TYPE_CHECKING

# 导入 SQLAlchemy 日期时间列类型。
from sqlalchemy import DateTime
# 导入 SQLAlchemy 外键约束工具。
from sqlalchemy import ForeignKey
# 导入 SQLAlchemy 整数列类型。
from sqlalchemy import Integer
# 导入 SQLAlchemy 数值列类型。
from sqlalchemy import Numeric
# 导入 SQLAlchemy 字符串列类型。
from sqlalchemy import String
# 导入 ORM 映射字段工具。
from sqlalchemy.orm import Mapped
# 导入 ORM 映射列工具。
from sqlalchemy.orm import mapped_column
# 导入 ORM 关系工具。
from sqlalchemy.orm import relationship

# 导入项目 ORM 基类。
from app.core.database import Base

# 仅在类型检查时导入品牌模型以避免循环导入。
if TYPE_CHECKING:
    # 导入品牌模型类型。
    from app.models.brand import Brand


# 定义汽车车型数据库模型。
class CarModel(Base):
    # 指定车型表名称。
    __tablename__ = "car_models"

    # 定义车型主键。
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 定义车型名称字段。
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 定义车型年款字段。
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    # 定义车型价格字段。
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    # 定义所属品牌外键字段。
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False, index=True)
    # 定义车型创建时间字段。
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    # 定义车型更新时间字段。
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    # 定义车型与品牌的多对一关系。
    brand: Mapped["Brand"] = relationship(back_populates="car_models")
