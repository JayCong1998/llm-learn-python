# 导入 SQLAlchemy 会话类型。
from sqlalchemy.orm import Session

# 导入品牌模型。
from app.models.brand import Brand
# 导入品牌仓储。
from app.repositories.brand_repository import BrandRepository
# 导入冲突异常。
from app.services.exceptions import ConflictError
# 导入未找到异常。
from app.services.exceptions import NotFoundError
# 导入品牌创建模型。
from app.schemas.brand import BrandCreate
# 导入品牌更新模型。
from app.schemas.brand import BrandUpdate


# 编排品牌相关的业务规则和事务。
class BrandService:
    # 初始化服务使用的会话与仓储。
    def __init__(self, database_session: Session) -> None:
        # 保存当前业务会话。
        self.database_session = database_session
        # 创建品牌数据访问对象。
        self.brand_repository = BrandRepository(database_session)

    # 返回品牌或抛出未找到异常。
    def get_or_raise(self, brand_id: int) -> Brand:
        # 查询品牌实体。
        brand = self.brand_repository.get(brand_id)
        # 拒绝不存在品牌。
        if brand is None:
            # 抛出领域未找到异常。
            raise NotFoundError("品牌不存在")
        # 返回找到的品牌。
        return brand

    # 返回全部品牌。
    def list(self) -> list[Brand]:
        # 返回仓储查询结果。
        return self.brand_repository.list()

    # 创建品牌。
    def create(self, payload: BrandCreate) -> Brand:
        # 拒绝重复品牌名称。
        if self.brand_repository.find_by_name(payload.name) is not None:
            # 抛出领域冲突异常。
            raise ConflictError("品牌名称已存在")
        # 创建品牌实体。
        brand = Brand(**payload.model_dump())
        # 加入待写入品牌。
        self.brand_repository.add(brand)
        # 提交品牌事务。
        self.database_session.commit()
        # 刷新品牌字段。
        self.database_session.refresh(brand)
        # 返回创建品牌。
        return brand

    # 更新品牌。
    def update(self, brand_id: int, payload: BrandUpdate) -> Brand:
        # 查询待更新品牌。
        brand = self.get_or_raise(brand_id)
        # 拒绝更新为其他品牌名称。
        if self.brand_repository.find_by_name(payload.name, exclude_id=brand_id) is not None:
            # 抛出领域冲突异常。
            raise ConflictError("品牌名称已存在")
        # 写入更新字段。
        for field_name, field_value in payload.model_dump().items():
            # 设置当前品牌字段。
            setattr(brand, field_name, field_value)
        # 提交更新事务。
        self.database_session.commit()
        # 刷新更新结果。
        self.database_session.refresh(brand)
        # 返回更新品牌。
        return brand

    # 删除品牌。
    def delete(self, brand_id: int) -> None:
        # 查询待删除品牌。
        brand = self.get_or_raise(brand_id)
        # 拒绝仍有关联车型的品牌。
        if self.brand_repository.has_car_models(brand_id):
            # 抛出领域冲突异常。
            raise ConflictError("品牌仍有关联车型，不能删除")
        # 标记品牌为删除。
        self.brand_repository.delete(brand)
        # 提交删除事务。
        self.database_session.commit()
