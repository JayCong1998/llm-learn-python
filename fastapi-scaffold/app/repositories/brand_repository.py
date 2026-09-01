# 导入 SQLAlchemy 查询构造工具。
from sqlalchemy import select
# 导入 SQLAlchemy 会话类型。
from sqlalchemy.orm import Session

# 导入品牌 ORM 模型。
from app.models.brand import Brand
# 导入车型 ORM 模型。
from app.models.car_model import CarModel


# 封装品牌实体的数据访问操作。
class BrandRepository:
    # 保存当前请求数据库会话。
    def __init__(self, database_session: Session) -> None:
        # 记录仓储使用的会话。
        self.database_session = database_session

    # 按主键查询品牌。
    def get(self, brand_id: int) -> Brand | None:
        # 返回指定主键的品牌实体。
        return self.database_session.get(Brand, brand_id)

    # 按主键升序查询全部品牌。
    def list(self) -> list[Brand]:
        # 返回已排序的品牌列表。
        return list(self.database_session.scalars(select(Brand).order_by(Brand.id)).all())

    # 查询同名品牌并可排除指定主键。
    def find_by_name(self, name: str, exclude_id: int | None = None) -> Brand | None:
        # 创建按名称查询品牌的语句。
        statement = select(Brand).where(Brand.name == name)
        # 在更新场景排除当前品牌。
        if exclude_id is not None:
            # 添加排除当前主键的条件。
            statement = statement.where(Brand.id != exclude_id)
        # 返回同名品牌或空值。
        return self.database_session.scalar(statement)

    # 将品牌标记为待持久化实体。
    def add(self, brand: Brand) -> None:
        # 加入当前会话而不提交事务。
        self.database_session.add(brand)

    # 将品牌标记为待删除实体。
    def delete(self, brand: Brand) -> None:
        # 从当前会话删除品牌。
        self.database_session.delete(brand)

    # 判断品牌是否拥有车型关联。
    def has_car_models(self, brand_id: int) -> bool:
        # 查询任意一条关联车型。
        return self.database_session.scalar(select(CarModel.id).where(CarModel.brand_id == brand_id).limit(1)) is not None
