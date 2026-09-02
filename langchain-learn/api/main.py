"""LangChain 教学 API 的 FastAPI 应用入口。"""

# 导入异步上下文管理器装饰器。
from contextlib import asynccontextmanager
# 导入线程锁类型。
from threading import Lock

# 导入 FastAPI 应用和请求类型。
from fastapi import FastAPI, Request
# 导入 JSON 响应类型。
from fastapi.responses import JSONResponse

# 导入业务异常类型。
from api.core.errors import (
    ApiError,
    ConfigurationError,
    InvalidResourceNameError,
    ResourceNotFoundError,
    UpstreamServiceError,
)
# 导入提示词模块路由。
from api.modules.prompts.api import router as prompts_router
# 导入消息记忆模块路由。
from api.modules.memory.api import router as memory_router
# 导入 MCP 调用模块路由。
from api.modules.mcp.api import router as mcp_router
# 导入本地技能模块路由。
from api.modules.skills.api import router as skills_router
# 导入流式输出模块路由。
from api.modules.streaming.api import router as streaming_router
# 导入结构化输出模块路由。
from api.modules.structured.api import router as structured_router
# 导入安全本地工具模块路由。
from api.modules.tools.api import router as tools_router


# 根据异常类型取得 HTTP 状态码。
def _status_for_error(error: ApiError) -> int:
    # 将配置异常映射为服务不可用。
    if isinstance(error, ConfigurationError):
        # 返回服务不可用状态码。
        return 503
    # 将上游异常映射为错误网关。
    if isinstance(error, UpstreamServiceError):
        # 返回错误网关状态码。
        return 502
    # 将资源不存在映射为未找到。
    if isinstance(error, ResourceNotFoundError):
        # 返回未找到状态码。
        return 404
    # 将非法名称映射为不可处理实体。
    if isinstance(error, InvalidResourceNameError):
        # 返回不可处理实体状态码。
        return 422
    # 为其他稳定业务异常返回客户端错误。
    return 400


# 管理当前 FastAPI 应用独占的持久资源。
@asynccontextmanager
async def _application_lifespan(application: FastAPI):
    # 确保正常或异常退出都执行资源清理。
    try:
        # 让应用开始处理请求。
        yield
    # 在任意退出路径清理持久资源。
    finally:
        # 复制关闭函数以避免清理过程修改迭代对象。
        resource_closers = list(reversed(application.state.resource_closers))
        # 提前清空列表避免关闭异常留下失效引用。
        application.state.resource_closers.clear()
        # 逆序关闭应用运行期间创建的资源。
        for close_resource in resource_closers:
            # 隔离单个资源的关闭异常。
            try:
                # 关闭 SQLite 等持久连接。
                close_resource()
            # 忽略停机阶段无法恢复的单个关闭异常。
            except Exception:
                # 继续尝试关闭其他资源。
                pass
        # 释放记忆服务引用。
        application.state.memory_service = None


# 创建可供测试隔离使用的 FastAPI 应用。
def create_app() -> FastAPI:
    # 创建带教学元数据的应用实例。
    application = FastAPI(
        title="LangChain API Demos",
        version="1.0.0",
        lifespan=_application_lifespan,
    )
    # 初始化当前应用独占的记忆服务引用。
    application.state.memory_service = None
    # 初始化并发首次创建资源的线程锁。
    application.state.memory_resource_lock = Lock()
    # 初始化生命周期资源关闭函数列表。
    application.state.resource_closers = []

    # 注册统一业务异常处理器。
    @application.exception_handler(ApiError)
    async def handle_api_error(_request: Request, error: ApiError) -> JSONResponse:
        # 返回稳定且不泄露内部信息的错误结构。
        return JSONResponse(
            status_code=_status_for_error(error),
            content={"error": {"code": error.code, "message": error.message}},
        )

    # 注册不读取模型配置的健康检查。
    @application.get("/health", tags=["system"])
    def health() -> dict[str, dict[str, str]]:
        # 返回稳定存活状态。
        return {"data": {"status": "ok"}}

    # 注册提示词模板模块。
    application.include_router(prompts_router)
    # 注册消息记忆模块。
    application.include_router(memory_router)
    # 注册 MCP 调用模块。
    application.include_router(mcp_router)
    # 注册本地技能模块。
    application.include_router(skills_router)
    # 注册流式输出模块。
    application.include_router(streaming_router)
    # 注册结构化输出模块。
    application.include_router(structured_router)
    # 注册安全本地工具模块。
    application.include_router(tools_router)

    # 返回完成基础配置的应用实例。
    return application


# 创建 Uvicorn 默认加载的应用实例。
app = create_app()
