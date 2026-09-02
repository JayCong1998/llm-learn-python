"""API 对外暴露的稳定业务异常。"""


# 定义带稳定错误码的业务异常基类。
class ApiError(Exception):
    """表示可以安全映射为 HTTP 响应的错误。"""

    # 声明默认错误码。
    code = "api_error"

    # 初始化安全错误说明。
    def __init__(self, message: str) -> None:
        # 保存可向调用方展示的说明。
        self.message = message
        # 初始化标准异常文本。
        super().__init__(message)


# 定义服务配置缺失或无效异常。
class ConfigurationError(ApiError):
    """表示服务运行配置不可用。"""

    # 声明配置错误码。
    code = "configuration_error"


# 定义模型或 MCP 上游调用异常。
class UpstreamServiceError(ApiError):
    """表示外部模型或 MCP 服务调用失败。"""

    # 声明上游错误码。
    code = "upstream_service_error"


# 定义白名单资源不存在异常。
class ResourceNotFoundError(ApiError):
    """表示请求的本地白名单资源不存在。"""

    # 声明资源未找到错误码。
    code = "resource_not_found"


# 定义资源名称不满足安全规则异常。
class InvalidResourceNameError(ApiError):
    """表示资源名称可能越过允许边界。"""

    # 声明资源名称错误码。
    code = "invalid_resource_name"
