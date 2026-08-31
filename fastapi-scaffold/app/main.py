# 导入 FastAPI 应用类。
from fastapi import FastAPI
# 导入认证路由。
from app.api.auth import router as auth_router
# 导入品牌管理路由。
from app.api.brands import router as brands_router
# 导入车型管理路由。
from app.api.car_models import router as car_models_router
# 导入健康检查路由。
from app.api.health import router as health_router
# 导入应用配置。
from app.core.config import settings

# 使用应用配置创建 FastAPI 实例。
app = FastAPI(title=settings.app_name)
# 注册认证路由。
app.include_router(auth_router)
# 注册品牌管理路由。
app.include_router(brands_router)
# 注册车型管理路由。
app.include_router(car_models_router)
# 注册健康检查路由。
app.include_router(health_router)
