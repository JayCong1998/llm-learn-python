# 导入 SQLAlchemy 查询构造工具。
from sqlalchemy import select
# 导入 SQLAlchemy 会话类型。
from sqlalchemy.orm import Session

# 导入车型 ORM 模型。
from app.models.car_model import CarModel


# 封装车型实体的数据访问操作。
class CarModelRepository:
    # 保存当前请求数据库会话。
    def __init__(self, database_session: Session) -> None:
        # 记录仓储使用的会话。
        self.database_session = database_session

    # 按主键查询车型。
    def get(self, car_model_id: int) -> CarModel | None:
        # 返回指定主键的车型实体。
        return self.database_session.get(CarModel, car_model_id)

    # 按条件过滤并分页查询车型。
    def list(self, brand_id: int | None, limit: int, offset: int) -> list[CarModel]:
        # 创建按主键排序的车型查询。
        statement = select(CarModel).order_by(CarModel.id)
        # 按需附加品牌条件。
        if brand_id is not None:
            # 限制为指定品牌的车型。
            statement = statement.where(CarModel.brand_id == brand_id)
        # 限制查询返回范围。
        statement = statement.limit(limit).offset(offset)
        # 返回当前页车型列表。
        return list(self.database_session.scalars(statement).all())

    # 将车型标记为待持久化实体。
    def add(self, car_model: CarModel) -> None:
        # 加入当前会话而不提交事务。
        self.database_session.add(car_model)

    # 将车型标记为待删除实体。
    def delete(self, car_model: CarModel) -> None:
        # 从当前会话删除车型。
        self.database_session.delete(car_model)
