# 导入管理员依赖注解工具。
from typing import Annotated

# 导入 FastAPI 路由类。
from fastapi import APIRouter
# 导入 FastAPI 依赖注入工具。
from fastapi import Depends
# 导入 FastAPI HTTP 异常类型。
from fastapi import HTTPException
# 导入 FastAPI 查询参数定义工具。
from fastapi import Query
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
# 导入创建车型请求模型。
from app.schemas.car_model import CarModelCreate
# 导入车型读取响应模型。
from app.schemas.car_model import CarModelRead
# 导入更新车型请求模型。
from app.schemas.car_model import CarModelUpdate

# 创建要求登录的车型管理路由。
router = APIRouter(prefix="/car-models", tags=["car-models"], dependencies=[Depends(get_current_user)])


# 根据主键查询车型并在缺失时返回未找到错误。
def get_car_model_or_404(car_model_id: int, database_session: DatabaseSession) -> CarModel:
    # 根据主键查询车型记录。
    car_model = database_session.get(CarModel, car_model_id)
    # 判断车型是否存在。
    if car_model is None:
        # 返回资源未找到响应。
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="车型不存在")
    # 返回查询到的车型。
    return car_model


# 根据主键校验品牌存在。
def require_brand(brand_id: int, database_session: DatabaseSession) -> None:
    # 根据主键查询品牌记录。
    brand = database_session.get(Brand, brand_id)
    # 拒绝不存在的品牌。
    if brand is None:
        # 返回资源未找到响应。
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌不存在")


# 登录后返回支持过滤和分页的车型列表。
@router.get("", response_model=list[CarModelRead])
# 定义车型列表处理函数。
def list_car_models(database_session: DatabaseSession, brand_id: Annotated[int | None, Query(gt=0)] = None, limit: Annotated[int, Query(ge=1, le=100)] = 20, offset: Annotated[int, Query(ge=0)] = 0) -> list[CarModel]:
    # 创建按主键升序的车型查询。
    statement = select(CarModel).order_by(CarModel.id)
    # 按需限制到指定品牌。
    if brand_id is not None:
        # 添加品牌过滤条件。
        statement = statement.where(CarModel.brand_id == brand_id)
    # 添加分页范围。
    statement = statement.limit(limit).offset(offset)
    # 执行查询并返回车型列表。
    return list(database_session.scalars(statement).all())


# 登录后返回指定车型详情。
@router.get("/{car_model_id}", response_model=CarModelRead)
# 定义车型详情处理函数。
def get_car_model(car_model_id: int, database_session: DatabaseSession) -> CarModel:
    # 查询并返回指定车型。
    return get_car_model_or_404(car_model_id, database_session)


# 仅允许管理员创建车型。
@router.post("", response_model=CarModelRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
# 定义创建车型处理函数。
def create_car_model(payload: CarModelCreate, database_session: DatabaseSession) -> CarModel:
    # 校验请求关联的品牌存在。
    require_brand(payload.brand_id, database_session)
    # 使用请求数据创建车型实体。
    car_model = CarModel(**payload.model_dump())
    # 将新车型加入当前事务。
    database_session.add(car_model)
    # 提交车型数据。
    database_session.commit()
    # 刷新实体以读取数据库生成字段。
    database_session.refresh(car_model)
    # 返回创建后的车型。
    return car_model


# 仅允许管理员更新车型。
@router.put("/{car_model_id}", response_model=CarModelRead, dependencies=[Depends(require_admin)])
# 定义更新车型处理函数。
def update_car_model(car_model_id: int, payload: CarModelUpdate, database_session: DatabaseSession) -> CarModel:
    # 查询待更新车型。
    car_model = get_car_model_or_404(car_model_id, database_session)
    # 校验请求关联的品牌存在。
    require_brand(payload.brand_id, database_session)
    # 逐项写入更新后的车型属性。
    for field_name, field_value in payload.model_dump().items():
        # 为车型实体设置当前字段值。
        setattr(car_model, field_name, field_value)
    # 提交车型更新。
    database_session.commit()
    # 刷新实体以读取更新后的字段。
    database_session.refresh(car_model)
    # 返回更新后的车型。
    return car_model


# 仅允许管理员删除车型。
@router.delete("/{car_model_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
# 定义删除车型处理函数。
def delete_car_model(car_model_id: int, database_session: DatabaseSession) -> None:
    # 查询待删除车型。
    car_model = get_car_model_or_404(car_model_id, database_session)
    # 删除车型实体。
    database_session.delete(car_model)
    # 提交删除事务。
    database_session.commit()
