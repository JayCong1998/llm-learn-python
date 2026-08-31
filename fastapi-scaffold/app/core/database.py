# 导入 SQLite 数据库驱动类型。
import sqlite3

# 导入 SQLAlchemy 事件注册工具。
from sqlalchemy import event
# 导入 SQLAlchemy 数据库引擎创建函数。
from sqlalchemy import create_engine
# 导入 SQLAlchemy 引擎类型。
from sqlalchemy.engine import Engine
# 导入 SQLAlchemy 声明式模型基类。
from sqlalchemy.orm import DeclarativeBase
# 导入 SQLAlchemy 会话工厂。
from sqlalchemy.orm import sessionmaker

# 导入应用配置。
from app.core.config import settings


# 定义全部 ORM 模型共享的声明式基类。
class Base(DeclarativeBase):
    # 保持声明式基类不定义额外成员。
    pass


# 在每个 SQLite 连接建立时开启外键约束。
@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    # 忽略非 SQLite 数据库连接。
    if not isinstance(dbapi_connection, sqlite3.Connection):
        # 直接结束非 SQLite 连接的事件处理。
        return
    # 创建执行 SQLite 指令的游标。
    cursor = dbapi_connection.cursor()
    # 开启 SQLite 默认关闭的外键约束。
    cursor.execute("PRAGMA foreign_keys=ON")
    # 关闭游标释放数据库资源。
    cursor.close()


# 根据数据库类型配置 SQLite 的跨线程访问参数。
engine_options = {"connect_args": {"check_same_thread": False}} if settings.database_url.startswith("sqlite") else {}
# 创建应用共享的数据库引擎。
engine = create_engine(settings.database_url, **engine_options)
# 创建不自动提交和刷新实体的会话工厂。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 按请求生成并在结束后关闭数据库会话。
def get_db():
    # 创建新的数据库会话。
    database_session = SessionLocal()
    # 确保请求结束时关闭数据库会话。
    try:
        # 向调用方提供数据库会话。
        yield database_session
    # 无论请求结果如何都关闭会话。
    finally:
        # 关闭数据库会话释放连接资源。
        database_session.close()
