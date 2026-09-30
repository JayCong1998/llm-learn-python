# 导入 FastAPI 路由定义工具。
from fastapi import APIRouter
# 导入统一响应模型与构造方法。
from core.response import ApiResponse, success_response

# 创建健康检查 API 路由。
router = APIRouter()





# 提供服务存活状态检查接口。
@router.get("/health", tags=["health"])
# 返回简单的健康状态结果。
async def health_check() -> ApiResponse[dict[str, str]]:
    # 使用固定状态表示服务已启动。
    return success_response({"status": "server ok"})
