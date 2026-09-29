# 导入异步事件循环管理器与 FastAPI 应用工厂。
import asyncio
from fastapi import FastAPI

# 导入 Uvicorn 开发服务器。
from uvicorn import Config, Server

# 导入统一 API 路由与应用配置。
from api.router import api_router
from core.config import settings
# 导入全局异常处理器注册函数。
from core.exceptions import register_exception_handlers

# 使用项目配置创建 HTTP 应用。
app = FastAPI(title=settings.app_name, debug=settings.debug)
# 为应用注册统一异常处理器。
register_exception_handlers(app)
# 将业务 API 路由挂载到应用。
app.include_router(api_router)

# 在 IDE 直接运行时启动可调试的开发服务器。
if __name__ == "__main__":
    # 配置当前进程内的 ASGI 服务器以便 IDE 断点调试。
    server = Server(Config(app, host="127.0.0.1", port=8000, reload=False))
    # 用 Python 3.13 的 Runner 启动服务，避开 Uvicorn 对 asyncio.run 的调用。
    with asyncio.Runner() as runner:
        # 在当前调试进程的事件循环中运行服务器。
        runner.run(server.serve())
