# 导入 FastAPI 路由类。
from fastapi import APIRouter
# 导入依赖注入工具。
from fastapi import Depends
# 导入 HTTP 异常类型。
from fastapi import HTTPException
# 导入 HTTP 状态码常量。
from fastapi import status
# 导入管理员依赖。
from app.core.dependencies import require_admin
# 导入当前用户依赖。
from app.core.dependencies import get_current_user
# 导入数据库会话注解。
from app.core.dependencies import DatabaseSession
# 导入品牌服务。
from app.services.brand_service import BrandService
# 导入冲突异常。
from app.services.exceptions import ConflictError
# 导入未找到异常。
from app.services.exceptions import NotFoundError
# 导入品牌创建模型。
from app.schemas.brand import BrandCreate
# 导入品牌读取模型。
from app.schemas.brand import BrandRead
# 导入品牌更新模型。
from app.schemas.brand import BrandUpdate

# 创建要求登录的品牌路由。
router = APIRouter(prefix="/brands", tags=["brands"], dependencies=[Depends(get_current_user)])

# 创建服务实例。
def get_service(database_session: DatabaseSession) -> BrandService:
    # 返回绑定当前会话的服务。
    return BrandService(database_session)

# 转换服务异常为 HTTP 异常。
def translate_error(error: Exception) -> HTTPException:
    # 处理未找到业务异常。
    if isinstance(error, NotFoundError):
        # 返回未找到响应。
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    # 返回冲突响应。
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))

# 返回品牌列表。
@router.get("", response_model=list[BrandRead])
def list_brands(database_session: DatabaseSession) -> list[BrandRead]:
    # 调用品牌列表服务。
    return get_service(database_session).list()

# 返回品牌详情。
@router.get("/{brand_id}", response_model=BrandRead)
def get_brand(brand_id: int, database_session: DatabaseSession) -> BrandRead:
    # 尝试查询品牌。
    try:
        # 返回品牌详情。
        return get_service(database_session).get_or_raise(brand_id)
    # 转换未找到异常。
    except NotFoundError as error:
        # 抛出 HTTP 异常。
        raise translate_error(error) from error

# 创建品牌。
@router.post("", response_model=BrandRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_brand(payload: BrandCreate, database_session: DatabaseSession) -> BrandRead:
    # 尝试创建品牌。
    try:
        # 返回创建品牌。
        return get_service(database_session).create(payload)
    # 转换冲突异常。
    except ConflictError as error:
        # 抛出 HTTP 异常。
        raise translate_error(error) from error

# 更新品牌。
@router.put("/{brand_id}", response_model=BrandRead, dependencies=[Depends(require_admin)])
def update_brand(brand_id: int, payload: BrandUpdate, database_session: DatabaseSession) -> BrandRead:
    # 尝试更新品牌。
    try:
        # 返回更新品牌。
        return get_service(database_session).update(brand_id, payload)
    # 转换业务异常。
    except (NotFoundError, ConflictError) as error:
        # 抛出 HTTP 异常。
        raise translate_error(error) from error

# 删除品牌。
@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_brand(brand_id: int, database_session: DatabaseSession) -> None:
    # 尝试删除品牌。
    try:
        # 执行删除操作。
        get_service(database_session).delete(brand_id)
    # 转换业务异常。
    except (NotFoundError, ConflictError) as error:
        # 抛出 HTTP 异常。
        raise translate_error(error) from error
