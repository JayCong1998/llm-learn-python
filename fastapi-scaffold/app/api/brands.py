# 导入 FastAPI 路由类。
from fastapi import APIRouter
# 导入 FastAPI 依赖注入工具。
from fastapi import Depends
# 导入 FastAPI HTTP 异常类型。
from fastapi import HTTPException
# 导入 HTTP 状态码常量。
from fastapi import status
# 导入 SQLAlchemy 查询构造工具。
from sqlalchemy import select

# 导入管理员权限依赖。
from app.core.dependencies import require_admin
# 导入当前用户认证依赖。
from app.core.dependencies import get_current_user
# 导入数据库会话注解。
from app.core.dependencies import DatabaseSession
# 导入品牌模型。
from app.models.brand import Brand
# 导入车型模型。
from app.models.car_model import CarModel
# 导入创建品牌请求模型。
from app.schemas.brand import BrandCreate
# 导入品牌读取响应模型。
from app.schemas.brand import BrandRead
# 导入更新品牌请求模型。
from app.schemas.brand import BrandUpdate

# 创建要求登录的品牌管理路由。
router = APIRouter(prefix="/brands", tags=["brands"], dependencies=[Depends(get_current_user)])


# 根据主键查询品牌并在缺失时返回未找到错误。
def get_brand_or_404(brand_id: int, database_session: DatabaseSession) -> Brand:
    # 根据主键查询品牌记录。
    brand = database_session.get(Brand, brand_id)
    # 判断品牌是否存在。
    if brand is None:
        # 返回资源未找到响应。
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌不存在")
    # 返回查询到的品牌。
    return brand


# 登录后返回全部品牌列表。
@router.get("", response_model=list[BrandRead])
# 定义品牌列表处理函数。
def list_brands(database_session: DatabaseSession) -> list[Brand]:
    # 按主键升序查询全部品牌。
    brands = database_session.scalars(select(Brand).order_by(Brand.id)).all()
    # 返回品牌列表。
    return list(brands)


# 登录后返回指定品牌详情。
@router.get("/{brand_id}", response_model=BrandRead)
# 定义品牌详情处理函数。
def get_brand(brand_id: int, database_session: DatabaseSession) -> Brand:
    # 查询并返回指定品牌。
    return get_brand_or_404(brand_id, database_session)


# 仅允许管理员创建品牌。
@router.post("", response_model=BrandRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
# 定义创建品牌处理函数。
def create_brand(payload: BrandCreate, database_session: DatabaseSession) -> Brand:
    # 查询是否存在同名品牌。
    existing_brand = database_session.scalar(select(Brand).where(Brand.name == payload.name))
    # 拒绝重复品牌名称。
    if existing_brand is not None:
        # 返回资源冲突响应。
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="品牌名称已存在")
    # 使用请求数据创建品牌实体。
    brand = Brand(**payload.model_dump())
    # 将新品牌加入当前事务。
    database_session.add(brand)
    # 提交品牌数据。
    database_session.commit()
    # 刷新实体以读取数据库生成字段。
    database_session.refresh(brand)
    # 返回创建后的品牌。
    return brand


# 仅允许管理员更新品牌。
@router.put("/{brand_id}", response_model=BrandRead, dependencies=[Depends(require_admin)])
# 定义更新品牌处理函数。
def update_brand(brand_id: int, payload: BrandUpdate, database_session: DatabaseSession) -> Brand:
    # 查询要更新的品牌。
    brand = get_brand_or_404(brand_id, database_session)
    # 查询同名的其他品牌。
    existing_brand = database_session.scalar(select(Brand).where(Brand.name == payload.name, Brand.id != brand_id))
    # 拒绝更新为已有品牌名称。
    if existing_brand is not None:
        # 返回资源冲突响应。
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="品牌名称已存在")
    # 逐项写入更新后的品牌属性。
    for field_name, field_value in payload.model_dump().items():
        # 为品牌实体设置当前字段值。
        setattr(brand, field_name, field_value)
    # 提交品牌更新。
    database_session.commit()
    # 刷新实体以读取更新后的字段。
    database_session.refresh(brand)
    # 返回更新后的品牌。
    return brand


# 仅允许管理员删除品牌。
@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
# 定义删除品牌处理函数。
def delete_brand(brand_id: int, database_session: DatabaseSession) -> None:
    # 查询要删除的品牌。
    brand = get_brand_or_404(brand_id, database_session)
    # 查询品牌是否仍有关联车型。
    related_car_model = database_session.scalar(select(CarModel).where(CarModel.brand_id == brand_id))
    # 拒绝删除仍被车型引用的品牌。
    if related_car_model is not None:
        # 返回业务冲突响应。
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="品牌仍有关联车型，不能删除")
    # 删除品牌实体。
    database_session.delete(brand)
    # 提交删除事务。
    database_session.commit()
