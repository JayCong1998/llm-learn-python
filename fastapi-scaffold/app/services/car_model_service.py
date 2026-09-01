# 导入 SQLAlchemy 会话类型。
from sqlalchemy.orm import Session

# 导入品牌模型。
from app.models.brand import Brand
# 导入车型模型。
from app.models.car_model import CarModel
# 导入品牌仓储。
from app.repositories.brand_repository import BrandRepository
# 导入车型仓储。
from app.repositories.car_model_repository import CarModelRepository
# 导入未找到异常。
from app.services.exceptions import NotFoundError
# 导入车型创建模型。
from app.schemas.car_model import CarModelCreate
# 导入车型更新模型。
from app.schemas.car_model import CarModelUpdate


# 编排车型相关的业务规则和事务。
class CarModelService:
    # 初始化服务使用的会话与仓储。
    def __init__(self, database_session: Session) -> None:
        # 保存当前业务会话。
        self.database_session = database_session
        # 创建品牌数据访问对象。
        self.brand_repository = BrandRepository(database_session)
        # 创建车型数据访问对象。
        self.car_model_repository = CarModelRepository(database_session)

    # 返回车型或抛出未找到异常。
    def get_or_raise(self, car_model_id: int) -> CarModel:
        # 查询车型实体。
        car_model = self.car_model_repository.get(car_model_id)
        # 拒绝不存在车型。
        if car_model is None:
            # 抛出领域未找到异常。
            raise NotFoundError("车型不存在")
        # 返回找到的车型。
        return car_model

    # 校验并返回品牌。
    def require_brand(self, brand_id: int) -> Brand:
        # 查询品牌实体。
        brand = self.brand_repository.get(brand_id)
        # 拒绝不存在品牌。
        if brand is None:
            # 抛出领域未找到异常。
            raise NotFoundError("品牌不存在")
        # 返回找到的品牌。
        return brand

    # 按条件返回车型列表。
    def list(self, brand_id: int | None, limit: int, offset: int) -> list[CarModel]:
        # 返回仓储的筛选分页结果。
        return self.car_model_repository.list(brand_id, limit, offset)

    # 创建车型。
    def create(self, payload: CarModelCreate) -> CarModel:
        # 校验关联品牌存在。
        self.require_brand(payload.brand_id)
        # 创建车型实体。
        car_model = CarModel(**payload.model_dump())
        # 加入待写入车型。
        self.car_model_repository.add(car_model)
        # 提交车型事务。
        self.database_session.commit()
        # 刷新车型字段。
        self.database_session.refresh(car_model)
        # 返回创建车型。
        return car_model

    # 更新车型。
    def update(self, car_model_id: int, payload: CarModelUpdate) -> CarModel:
        # 查询待更新车型。
        car_model = self.get_or_raise(car_model_id)
        # 校验更新品牌存在。
        self.require_brand(payload.brand_id)
        # 写入更新字段。
        for field_name, field_value in payload.model_dump().items():
            # 设置当前车型字段。
            setattr(car_model, field_name, field_value)
        # 提交更新事务。
        self.database_session.commit()
        # 刷新更新结果。
        self.database_session.refresh(car_model)
        # 返回更新车型。
        return car_model

    # 删除车型。
    def delete(self, car_model_id: int) -> None:
        # 查询待删除车型。
        car_model = self.get_or_raise(car_model_id)
        # 标记车型为删除。
        self.car_model_repository.delete(car_model)
        # 提交删除事务。
        self.database_session.commit()
