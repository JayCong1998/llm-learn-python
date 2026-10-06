# 导入枚举、泛型与重载声明工具。
from enum import Enum
from typing import Any, Generic, TypeVar, overload
# 导入 Pydantic 响应模型基类。
from pydantic import BaseModel

# 定义响应数据的泛型类型。
T = TypeVar("T")


# 定义同时保存数值码和默认消息的错误类型。
class ErrorDefinition(Enum):
    # 保存错误码与默认消息。
    def __new__(cls, code: int, message: str) -> "ErrorDefinition":
        # 创建枚举成员并记录其数值码。
        member = object.__new__(cls)
        # 设置枚举成员的基础值。
        member._value_ = code
        # 保存可直接用于响应的错误码。
        member.code = code
        # 保存该错误码对应的默认消息。
        member.message = message
        # 返回完整的错误码定义成员。
        return member

    # 表示请求成功。
    SUCCESS = (0, "success")
    # 表示请求参数校验失败。
    VALIDATION_ERROR = (10001, "请求参数校验失败")
    # 表示请求内容或格式不正确。
    BAD_REQUEST = (100400, "请求内容不正确")
    # 表示请求的资源或路由不存在。
    NOT_FOUND = (10004, "请求的资源不存在")
    # 表示请求未通过身份认证。
    UNAUTHORIZED = (100401, "请先完成身份认证")
    # 表示请求没有执行权限。
    FORBIDDEN = (100403, "没有执行该操作的权限")
    # 表示请求触发限流。
    TOO_MANY_REQUESTS = (100429, "请求过于频繁")
    # 表示模型服务暂不可用。
    MODEL_UNAVAILABLE = (100503, "模型服务暂不可用")
    # 表示服务器发生未预期错误。
    INTERNAL_ERROR = (10500, "服务器内部错误")


# 定义所有 API 共用的响应结构。
class ApiResponse(BaseModel, Generic[T]):
    # 标记本次请求是否成功。
    success: bool
    # 保存业务错误码或成功码。
    code: int
    # 保存便于阅读的处理结果说明。
    message: str
    # 保存接口实际返回的数据或错误详情。
    data: T | None = None


# 声明携带业务数据的成功响应用法。
@overload
def success_response(data: T, message: str = "success") -> ApiResponse[T]: ...


# 声明不携带业务数据的成功响应用法。
@overload
def success_response(data: None = None, message: str = "success") -> ApiResponse[None]: ...


# 构造统一成功响应对象。
def success_response(data: Any = None, message: str = "success") -> ApiResponse[Any]:
    # 使用成功状态封装业务数据。
    return ApiResponse(success=True, code=ErrorDefinition.SUCCESS.code, message=message, data=data)


# 声明使用默认错误消息的失败响应用法。
@overload
def failure_response(error: ErrorDefinition, data: Any = None) -> ApiResponse[Any]: ...


# 声明使用自定义错误消息的失败响应用法。
@overload
def failure_response(error: ErrorDefinition, message: str, data: Any = None) -> ApiResponse[Any]: ...


# 构造统一失败响应对象。
def failure_response(
    error: ErrorDefinition,
    message: str | Any = "request failed",
    data: Any = None,
) -> ApiResponse[Any]:
    # 兼容将第二个位置参数直接作为错误详情的调用方式。
    if not isinstance(message, str):
        data = message
        message = "request failed"
    # 使用自定义消息或错误定义中的默认消息。
    response_message = message if isinstance(message, str) and message != "request failed" else error.message
    # 使用错误状态封装错误码、说明和详情。
    return ApiResponse(success=False, code=error.code, message=response_message, data=data)
