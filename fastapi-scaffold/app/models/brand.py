# 导入创建与更新时间字段所需的日期时间类型。
from datetime import datetime
# 导入协调世界时区对象。
from datetime import timezone
# 导入关系字段类型。
from typing import TYPE_CHECKING

# 导入 SQLAlchemy 日期时间列类型。
from sqlalchemy import DateTime
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

# 导入项目 ORM 基类。
from app.core.database import Base

# 仅在类型检查时导入车型模型以避免循环导入。
if TYPE_CHECKING:
    # 导入车型模型类型。
    from app.models.car_model import CarModel


# 定义汽车品牌数据库模型。
class Brand(Base):
    # 指定品牌表名称。
    __tablename__ = "brands"

    # 定义品牌主键。
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 定义唯一品牌名称字段。
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    # 定义品牌所属国家字段。
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    # 定义可选品牌描述字段。
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 定义品牌创建时间字段。
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    # 定义品牌更新时间字段。
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    # 定义品牌与车型的一对多关系。
    car_models: Mapped[list["CarModel"]] = relationship(back_populates="brand")
