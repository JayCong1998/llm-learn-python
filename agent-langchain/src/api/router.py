# 导入 FastAPI 路由组合工具。
from fastapi import APIRouter

# 导入独立的聊天与健康检查路由。
from api.chat import router as chat_router
from api.health import router as health_router

# 创建统一 API 路由容器。
api_router = APIRouter()
# 注册健康检查 API 模块。
api_router.include_router(health_router)
# 注册聊天 API 模块。
api_router.include_router(chat_router)
