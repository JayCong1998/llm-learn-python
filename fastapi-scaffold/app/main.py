# 导入 FastAPI 应用类。
from fastapi import FastAPI
# 导入请求校验异常类型。
from fastapi.exceptions import RequestValidationError
# 导入统一响应路由类。
from app.core.api_response import EnvelopeRoute
# 导入领域异常处理函数。
from app.core.api_response import domain_error_handler
# 导入框架 HTTP 异常处理函数。
from app.core.api_response import http_exception_handler
# 导入未预期异常处理函数。
from app.core.api_response import unexpected_exception_handler
# 导入请求校验异常处理函数。
from app.core.api_response import validation_exception_handler
# 导入认证路由。
from app.api.auth import router as auth_router
# 导入聊天路由。
from app.api.chat import router as chat_router
# 导入健康检查路由。
from app.api.health import router as health_router
# 导入应用配置。
from app.core.config import settings
# 导入领域异常基类。
from app.services.exceptions import DomainError
# 导入 Starlette HTTP 异常类型。
from starlette.exceptions import HTTPException as StarletteHTTPException

# 使用应用配置创建 FastAPI 实例。
app = FastAPI(title=settings.app_name)
# 为后续注册的路由启用统一成功响应包装。
app.router.route_class = EnvelopeRoute
# 注册领域异常处理函数。
app.add_exception_handler(DomainError, domain_error_handler)
# 注册框架 HTTP 异常处理函数。
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
# 注册请求校验异常处理函数。
app.add_exception_handler(RequestValidationError, validation_exception_handler)
# 注册未预期异常处理函数。
app.add_exception_handler(Exception, unexpected_exception_handler)
# 注册认证路由。
app.include_router(auth_router)
# 注册聊天路由。
app.include_router(chat_router)
# 注册健康检查路由。
app.include_router(health_router)
