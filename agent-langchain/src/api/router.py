# 导入 FastAPI 路由组合工具。
from fastapi import APIRouter

# 导入独立的聊天与健康检查路由。
from api.chat import router as chat_router
from api.health import router as health_router
from api.async_demo import router as async_demo_router
from api.agent_chat import router as agent_chat_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(async_demo_router)
api_router.include_router(agent_chat_router)
