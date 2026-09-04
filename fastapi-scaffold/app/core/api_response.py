# 导入 JSON 编解码工具。
import json

# 导入 HTTP 状态码常量。
from fastapi import status
# 导入 FastAPI 请求校验异常类型。
from fastapi.exceptions import RequestValidationError
# 导入 FastAPI 路由实现基类。
from fastapi.routing import APIRoute
# 导入 Starlette HTTP 异常类型。
from starlette.exceptions import HTTPException as StarletteHTTPException
# 导入 HTTP 请求对象。
from starlette.requests import Request
# 导入 HTTP 响应对象。
from starlette.responses import JSONResponse
# 导入 HTTP 响应基类。
from starlette.responses import Response
# 导入流式 HTTP 响应类型。
from starlette.responses import StreamingResponse

# 导入领域异常基类。
from app.services.exceptions import DomainError


# 构造统一成功响应数据。
def success_payload(data: object) -> dict[str, object]:
    # 返回约定的成功响应结构。
    return {"code": 0, "message": "success", "data": data}


# 构造统一错误响应对象。
def error_response(status_code: int, code: int, message: str, headers: dict[str, str] | None = None) -> JSONResponse:
    # 返回保留 HTTP 状态和必要响应头的错误响应。
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": None}, headers=headers)


# 过滤会由新响应重新计算的旧响应头。
def response_headers(response: Response) -> dict[str, str]:
    # 保留认证等业务响应头并排除过期的内容长度与类型。
    return {name: value for name, value in response.headers.items() if name.lower() not in {"content-length", "content-type"}}


# 定义统一包装非流式 JSON 成功响应的路由类。
class EnvelopeRoute(APIRoute):
    # 获取被统一响应包装的路由处理函数。
    def get_route_handler(self):
        # 获取 FastAPI 原始路由处理函数。
        original_handler = super().get_route_handler()

        # 定义包装原始处理结果的异步函数。
        async def wrapped(request: Request) -> Response:
            # 执行原始路由处理。
            response = await original_handler(request)
            # 保留无内容响应和流式响应的原始协议。
            if response.status_code == status.HTTP_204_NO_CONTENT or isinstance(response, StreamingResponse):
                # 直接返回不应包装的响应。
                return response
            # 保留非 JSON 响应避免改变文件和页面等响应协议。
            if response.media_type != "application/json":
                # 直接返回非 JSON 响应。
                return response
            # 解析 FastAPI 已序列化的业务响应体。
            data = json.loads(response.body)
            # 返回带统一成功信封的新 JSON 响应。
            return JSONResponse(status_code=response.status_code, content=success_payload(data), headers=response_headers(response))

        # 返回统一包装后的路由处理函数。
        return wrapped


# 处理业务领域异常。
async def domain_error_handler(_: Request, error: DomainError) -> JSONResponse:
    # 返回领域异常定义的状态码和错误码。
    return error_response(error.status_code, error.error_code, str(error), error.headers)


# 处理认证、权限和框架 HTTP 异常。
async def http_exception_handler(_: Request, error: StarletteHTTPException) -> JSONResponse:
    # 将可能非字符串的异常详情转换为稳定消息。
    message = error.detail if isinstance(error.detail, str) else "请求失败"
    # 返回统一框架异常响应。
    return error_response(error.status_code, error.status_code, message, dict(error.headers) if error.headers else None)


# 处理请求模型和参数校验异常。
async def validation_exception_handler(_: Request, __: RequestValidationError) -> JSONResponse:
    # 返回不暴露内部校验细节的统一响应。
    return error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, status.HTTP_422_UNPROCESSABLE_CONTENT, "请求参数校验失败")


# 处理未被业务代码预期的异常。
async def unexpected_exception_handler(_: Request, __: Exception) -> JSONResponse:
    # 返回不泄露内部实现细节的统一服务端错误。
    return error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR, "服务器内部错误")
