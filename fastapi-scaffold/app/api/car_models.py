# 导入注解工具。
from typing import Annotated
# 导入路由类。
from fastapi import APIRouter
# 导入依赖注入工具。
from fastapi import Depends
# 导入 HTTP 异常。
from fastapi import HTTPException
# 导入查询参数工具。
from fastapi import Query
# 导入状态码常量。
from fastapi import status
# 导入管理员依赖。
from app.core.dependencies import require_admin
# 导入当前用户依赖。
from app.core.dependencies import get_current_user
# 导入数据库会话注解。
from app.core.dependencies import DatabaseSession
# 导入车型服务。
from app.services.car_model_service import CarModelService
# 导入未找到异常。
from app.services.exceptions import NotFoundError
# 导入车型创建模型。
from app.schemas.car_model import CarModelCreate
# 导入车型读取模型。
from app.schemas.car_model import CarModelRead
# 导入车型更新模型。
from app.schemas.car_model import CarModelUpdate

# 创建要求登录的车型路由。
router = APIRouter(prefix="/car-models", tags=["car-models"], dependencies=[Depends(get_current_user)])

# 创建车型服务实例。
def get_service(database_session: DatabaseSession) -> CarModelService:
    # 返回绑定当前会话的服务。
    return CarModelService(database_session)

# 返回车型列表。
@router.get("", response_model=list[CarModelRead])
def list_car_models(database_session: DatabaseSession, brand_id: Annotated[int | None, Query(gt=0)] = None, limit: Annotated[int, Query(ge=1, le=100)] = 20, offset: Annotated[int, Query(ge=0)] = 0) -> list[CarModelRead]:
    # 调用筛选分页服务。
    return get_service(database_session).list(brand_id, limit, offset)

# 返回车型详情。
@router.get("/{car_model_id}", response_model=CarModelRead)
def get_car_model(car_model_id: int, database_session: DatabaseSession) -> CarModelRead:
    # 尝试查询车型。
    try:
        # 返回车型详情。
        return get_service(database_session).get_or_raise(car_model_id)
    # 转换未找到异常。
    except NotFoundError as error:
        # 返回 HTTP 未找到异常。
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

# 创建车型。
@router.post("", response_model=CarModelRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_car_model(payload: CarModelCreate, database_session: DatabaseSession) -> CarModelRead:
    # 尝试创建车型。
    try:
        # 返回创建车型。
        return get_service(database_session).create(payload)
    # 转换未找到异常。
    except NotFoundError as error:
        # 返回 HTTP 未找到异常。
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

# 更新车型。
@router.put("/{car_model_id}", response_model=CarModelRead, dependencies=[Depends(require_admin)])
def update_car_model(car_model_id: int, payload: CarModelUpdate, database_session: DatabaseSession) -> CarModelRead:
    # 尝试更新车型。
    try:
        # 返回更新车型。
        return get_service(database_session).update(car_model_id, payload)
    # 转换未找到异常。
    except NotFoundError as error:
        # 返回 HTTP 未找到异常。
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

# 删除车型。
@router.delete("/{car_model_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_car_model(car_model_id: int, database_session: DatabaseSession) -> None:
    # 尝试删除车型。
    try:
        # 执行删除车型。
        get_service(database_session).delete(car_model_id)
    # 转换未找到异常。
    except NotFoundError as error:
        # 返回 HTTP 未找到异常。
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
