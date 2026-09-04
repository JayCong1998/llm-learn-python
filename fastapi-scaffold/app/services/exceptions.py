# 定义业务领域异常的共同基类。
class DomainError(Exception):
    # 定义默认客户端错误状态码。
    status_code = 400
    # 定义默认应用错误码。
    error_code = 400
    # 定义可选的响应头。
    headers: dict[str, str] | None = None


# 定义业务资源冲突异常。
class ConflictError(DomainError):
    # 定义资源冲突状态码。
    status_code = 409
    # 定义资源冲突错误码。
    error_code = 409


# 定义业务资源未找到异常。
class NotFoundError(DomainError):
    # 定义资源不存在状态码。
    status_code = 404
    # 定义资源不存在错误码。
    error_code = 404


# 定义业务认证失败异常。
class AuthenticationError(DomainError):
    # 定义认证失败状态码。
    status_code = 401
    # 定义认证失败错误码。
    error_code = 401
    # 定义 Bearer 认证协商响应头。
    headers = {"WWW-Authenticate": "Bearer"}


# 定义业务授权失败异常。
class AuthorizationError(DomainError):
    # 定义禁止访问状态码。
    status_code = 403
    # 定义禁止访问错误码。
    error_code = 403
