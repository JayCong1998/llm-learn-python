# 导入命令行参数读取工具。
import argparse
# 导入异步事件循环管理器。
import asyncio

# 导入 FastAPI 应用工厂。
from fastapi import FastAPI

# 导入 Uvicorn 的应用运行入口与服务器组件。
import uvicorn
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
    # 传--reload那么args.reload就启用

    # 创建启动参数解析器以供用户选择运行方式。
    parser = argparse.ArgumentParser(description="启动 Agent LangChain API 服务")
    # 添加启用文件热重载的命令行开关。
    parser.add_argument("--reload", action="store_true", help="启用文件变化自动重载")
    # 解析用户传入的启动参数。
    args = parser.parse_args()
    # 根据参数选择适合热重载的 Uvicorn 子进程模式。
    if args.reload:
        # 使用导入字符串启动应用以支持 Uvicorn 热重载。
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    # 未启用热重载时使用当前进程运行以便 IDEA 断点调试。
    else:
        # 在当前进程内创建 ASGI 服务器实例。
        server = Server(Config(app, host="127.0.0.1", port=8000))
        # 创建并管理当前进程的异步事件循环。
        with asyncio.Runner() as runner:
            # 在当前事件循环中运行服务器以保留断点调试能力。
            runner.run(server.serve())
