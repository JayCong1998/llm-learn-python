# 导入 FastAPI 路由类。
from fastapi import APIRouter
# 导入统一响应路由类。
from app.core.api_response import EnvelopeRoute
# 导入应用配置。
from app.core.config import settings

# 创建系统接口路由并启用统一成功响应。
router = APIRouter(tags=["system"], route_class=EnvelopeRoute)


# 提供应用健康检查接口。
@router.get("/health")
# 定义健康检查处理函数。
def health_check() -> dict[str, str]:
    # 返回约定的健康状态数据。
    return {"status": "ok", "service": settings.app_name}
