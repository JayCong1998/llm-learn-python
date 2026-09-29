# 导入日志记录、请求校验与 FastAPI 异常处理所需类型。
import logging

# 导入 FastAPI 请求与响应处理类型。
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# 导入统一错误定义与失败响应构造方法。
from core.response import ErrorDefinition, failure_response

# 初始化当前模块的异常日志记录器。
logger = logging.getLogger(__name__)


# 将 HTTP 状态映射为项目统一错误码。
def _error_code(status_code: int) -> ErrorDefinition:
    # 将常见 HTTP 错误映射到稳定的业务错误码。
    error_codes = {
        400: ErrorDefinition.BAD_REQUEST,
        401: ErrorDefinition.UNAUTHORIZED,
        403: ErrorDefinition.FORBIDDEN,
        404: ErrorDefinition.NOT_FOUND,
        429: ErrorDefinition.TOO_MANY_REQUESTS,
        503: ErrorDefinition.MODEL_UNAVAILABLE,
    }
    # 未单独定义的 HTTP 错误使用通用服务器错误码。
    return error_codes.get(status_code, ErrorDefinition.INTERNAL_ERROR)


# 注册应用级的统一异常处理器。
def register_exception_handlers(app: FastAPI) -> None:
    # 处理 FastAPI 与 Starlette 的 HTTP 异常。
    @app.exception_handler(StarletteHTTPException)
    # 将 HTTP 异常转换成统一 JSON 响应。
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # 使用枚举默认消息并附带 HTTP 异常详情。
        error = _error_code(exc.status_code)
        # 仅在 HTTP 异常提供文本详情时覆盖枚举默认消息。
        message = str(exc.detail) if isinstance(exc.detail, str) else error.message
        # 返回原始 HTTP 状态码与统一响应结构。
        return JSONResponse(
            status_code=exc.status_code,
            content=failure_response(error, message).model_dump(),
            headers=exc.headers,
        )

    # 处理请求体、路径参数和查询参数校验失败。
    @app.exception_handler(RequestValidationError)
    # 将校验错误转换成统一 JSON 响应。
    async def handle_validation_exception(request: Request, exc: RequestValidationError) -> JSONResponse:
        # 提取校验错误明细供调用方定位参数问题。
        errors = exc.errors()
        # 返回 422 状态码与参数错误明细。
        return JSONResponse(
            status_code=422,
            content=failure_response(
                ErrorDefinition.VALIDATION_ERROR,
                data=errors,
            ).model_dump(),
        )

    # 处理所有未被业务代码捕获的异常。
    @app.exception_handler(Exception)
    # 记录异常堆栈并返回通用错误信息。
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        # 在服务端日志中记录完整异常堆栈。
        logger.exception("处理请求时发生未捕获异常", exc_info=exc)
        # 返回通用 500 响应以免泄露内部实现细节。
        return JSONResponse(
            status_code=500,
            content=failure_response(ErrorDefinition.INTERNAL_ERROR).model_dump(),
        )
