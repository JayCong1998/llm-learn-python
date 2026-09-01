# 导入日志配置工具。
from logging.config import fileConfig

# 导入 Alembic 上下文。
from alembic import context
# 导入 SQLAlchemy 引擎创建工具。
from sqlalchemy import engine_from_config
# 导入 SQLAlchemy 连接池模块。
from sqlalchemy import pool

# 导入应用配置以读取数据库地址。
from app.core.config import settings
# 导入 ORM 元数据基类。
from app.core.database import Base
# 导入用户模型以注册用户表。
from app.models.user import User
# 导入会话模型以注册会话表。
from app.models.chat_conversation import ChatConversation
# 导入消息模型以注册消息表。
from app.models.chat_message import ChatMessage
# 导入大模型调用日志模型以注册日志表。
from app.models.llm_call_log import LlmCallLog

# 读取 Alembic 当前配置对象。
config = context.config
# 应用配置文件中的日志格式。
if config.config_file_name is not None:
    # 加载 Alembic 日志配置。
    fileConfig(config.config_file_name)
# 使用应用配置覆盖默认数据库地址。
config.set_main_option("sqlalchemy.url", settings.database_url)
# 指定自动生成迁移时比较的 ORM 元数据。
target_metadata = Base.metadata


# 在离线模式中生成 SQL 迁移脚本。
def run_migrations_offline() -> None:
    # 读取已解析的数据库地址。
    url = config.get_main_option("sqlalchemy.url")
    # 配置离线迁移上下文。
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    # 开启迁移事务。
    with context.begin_transaction():
        # 执行迁移版本升级或降级。
        context.run_migrations()


# 在在线模式中连接数据库并执行迁移。
def run_migrations_online() -> None:
    # 从配置创建可连接的数据库引擎。
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    # 建立数据库连接。
    with connectable.connect() as connection:
        # 使用连接配置迁移上下文。
        context.configure(connection=connection, target_metadata=target_metadata)
        # 开启迁移事务。
        with context.begin_transaction():
            # 执行迁移版本升级或降级。
            context.run_migrations()


# 根据当前执行模式选择迁移实现。
if context.is_offline_mode():
    # 执行离线迁移。
    run_migrations_offline()
# 在非离线模式执行在线迁移。
else:
    # 执行在线迁移。
    run_migrations_online()
