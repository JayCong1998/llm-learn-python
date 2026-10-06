# 导入标准日志接口以配置应用日志输出。
import logging

# 配置应用专用日志记录器及其标准控制台格式。
def configure_app_logging() -> None:
    # 获取应用日志的父记录器供业务模块共享。
    app_logger = logging.getLogger("agent")
    # 设置应用日志级别以显示关键运行信息。
    app_logger.setLevel(logging.INFO)
    # 阻止应用日志传递给 Uvicorn 的访问日志格式化器。
    app_logger.propagate = False
    # 仅在尚无处理器时创建控制台处理器。
    if not app_logger.handlers:
        # 创建标准控制台日志处理器。
        handler = logging.StreamHandler()
        # 设置常规日志格式，避免使用 Uvicorn 专用访问日志格式。
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        # 将控制台处理器附加到应用日志记录器。
        app_logger.addHandler(handler)
