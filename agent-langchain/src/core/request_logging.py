# 导入标准日志接口以写入统一请求日志。
import logging
# 导入线程接口以标记处理请求的执行线程。
from threading import current_thread, get_ident
# 导入高精度计时器以计算请求耗时。
from time import perf_counter
# 导入 UUID 生成器以为请求生成唯一标识。
from uuid import uuid4
# 导入 FastAPI 请求对象以读取请求信息。
from fastapi import FastAPI, Request

# 使用应用专用日志记录器避免 Uvicorn 访问日志格式冲突。
logger = logging.getLogger("request_logging")

# 为应用注册全局 HTTP 请求日志中间件。
def register_request_logging(app: FastAPI) -> None:
    # 包装所有 HTTP 请求并记录状态码与处理耗时。
    @app.middleware("http")
    # 执行请求并在响应返回或异常抛出后写入日志。
    async def log_request(request: Request, call_next):
        # 复用调用方传入的请求标识，缺失时创建 UUID。
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        # 将请求标识保存到请求状态供路由处理逻辑读取。
        request.state.request_id = request_id
        # 获取当前线程名称以便关联并发处理日志。
        thread_name = current_thread().name
        # 获取当前线程数字标识以便定位执行上下文。
        thread_id = get_ident()
        # 记录请求开始时间以测量整体处理耗时。
        started_at = perf_counter()
        # 获取连接方地址；测试客户端可能没有客户端信息。
        client_host = request.client.host if request.client else "unknown"
        # 记录请求方法、完整 URL、查询参数和线程信息。
        logger.info(
            '请求开始 request_id=%s thread=%s thread_id=%s method=%s url="%s" '
            'query_params=%s client=%s',
            request_id,
            thread_name,
            thread_id,
            request.method,
            request.url,
            request.query_params,
            client_host,
        )
        # 默认以服务器错误状态记录中途未生成响应的请求。
        status_code = 500
        # 请求正常返回时记录实际响应状态码。
        try:
            # 将请求交给后续中间件与路由处理。
            response = await call_next(request)
            # 保存最终响应的 HTTP 状态码。
            status_code = response.status_code
            # 将响应交还给客户端。
            return response
        # 无论请求成功或失败都记录一条请求摘要。
        finally:
            # 计算从请求进入中间件到处理结束的毫秒数。
            elapsed_ms = (perf_counter() - started_at) * 1000
            # 记录请求标识、线程、路径、状态码和完整处理耗时。
            logger.info(
                '请求完成 request_id=%s thread=%s thread_id=%s method=%s path="%s" '
                'client=%s status=%s duration_ms=%.2f',
                request_id,
                thread_name,
                thread_id,
                request.method,
                request.url.path,
                client_host,
                status_code,
                elapsed_ms,
            )
