# 导入 SQLAlchemy 引擎创建函数。
from sqlalchemy import create_engine
# 导入 SQLAlchemy 表结构检查工具。
from sqlalchemy import inspect
# 导入 SQLAlchemy 会话工厂。
from sqlalchemy.orm import sessionmaker
# 导入路径操作类型。
from pathlib import Path

# 导入数据库模型基类。
from app.core.database import Base
# 导入会话消息模型以注册消息表。
from app.models.chat_message import ChatMessage
# 导入会话模型以注册会话表。
from app.models.chat_conversation import ChatConversation
# 导入大模型调用日志模型以注册日志表。
from app.models.llm_call_log import LlmCallLog
# 导入用户模型以注册用户表。
from app.models.user import User


# 验证模型创建四张单数命名的数据表及公共审计字段。
def test_llm_chat_models_create_required_tables_and_common_columns(tmp_path):
    # 创建测试专用 SQLite 引擎。
    engine = create_engine(f"sqlite:///{tmp_path / 'llm-chat.db'}")
    # 创建全部模型对应的数据表。
    Base.metadata.create_all(bind=engine)
    # 创建数据库结构检查器。
    inspector = inspect(engine)
    # 读取已创建的数据表名称集合。
    table_names = set(inspector.get_table_names())

    # 断言四张 LLM 对话持久化表均已创建。
    assert {"user", "chat_conversation", "chat_message", "llm_call_log"} <= table_names
    # 遍历需要具备公共字段的表名。
    for table_name in ("user", "chat_conversation", "chat_message", "llm_call_log"):
        # 读取当前表的列名集合。
        column_names = {column["name"] for column in inspector.get_columns(table_name)}
        # 断言当前表包含全部通用审计、乐观锁与逻辑删除字段。
        assert {"created_at", "updated_at", "lock_version", "deleted"} <= column_names


# 验证大模型调用日志只关联生成回复的单条助手消息。
def test_llm_call_log_belongs_to_one_assistant_message(tmp_path):
    # 创建测试专用 SQLite 引擎。
    engine = create_engine(f"sqlite:///{tmp_path / 'llm-call-log.db'}")
    # 创建全部模型对应的数据表。
    Base.metadata.create_all(bind=engine)
    # 创建绑定测试引擎的会话工厂。
    session_factory = sessionmaker(bind=engine)
    # 创建数据库会话。
    session = session_factory()
    # 创建测试用户。
    user = User(username="llm-user", email="llm@example.com", password_hash="hash", role="user")
    # 保存测试用户。
    session.add(user)
    # 写入用户以生成主键。
    session.commit()
    # 创建属于测试用户的对话会话。
    conversation = ChatConversation(user_id=user.id, title="天气咨询")
    # 保存对话会话。
    session.add(conversation)
    # 写入会话以生成主键。
    session.commit()
    # 创建用户提问消息。
    user_message = ChatMessage(conversation_id=conversation.id, role="user", content="北京天气如何？")
    # 创建模型生成的助手回复消息。
    assistant_message = ChatMessage(conversation_id=conversation.id, role="assistant", content="北京晴朗。")
    # 保存两条消息。
    session.add_all([user_message, assistant_message])
    # 写入消息以生成主键。
    session.commit()
    # 创建关联助手消息的调用日志。
    call_log = LlmCallLog(message_id=assistant_message.id, provider="openai", model="gpt-5", status="succeeded", input_tokens=10, output_tokens=5, latency_ms=100)
    # 保存调用日志。
    session.add(call_log)
    # 写入调用日志。
    session.commit()
    # 刷新助手消息以加载一对一调用日志。
    session.refresh(assistant_message)

    # 断言调用日志关联本次生成的助手消息。
    assert call_log.message_id == assistant_message.id
    # 断言助手消息可反向获取唯一调用日志。
    assert assistant_message.llm_call_log is not None
    # 断言用户消息不关联调用日志。
    assert user_message.llm_call_log is None
    # 断言会话至少可以包含用户和助手两条消息。
    assert len(conversation.messages) == 2
    # 关闭数据库会话。
    session.close()


# 验证消息角色仅允许系统、用户与助手三种值。
def test_chat_message_rejects_unsupported_role(tmp_path):
    # 创建测试专用 SQLite 引擎。
    engine = create_engine(f"sqlite:///{tmp_path / 'chat-message-role.db'}")
    # 创建全部模型对应的数据表。
    Base.metadata.create_all(bind=engine)
    # 创建数据库结构检查器。
    inspector = inspect(engine)
    # 读取消息表的检查约束。
    check_constraints = inspector.get_check_constraints("chat_message")

    # 断言消息角色检查约束已被创建。
    assert any("system" in str(constraint.get("sqltext")) and "assistant" in str(constraint.get("sqltext")) for constraint in check_constraints)


# 验证所有持久化实体会自动维护乐观锁版本和更新时间。
def test_llm_chat_entities_use_optimistic_locking_and_update_timestamps(tmp_path):
    # 创建测试专用 SQLite 引擎。
    engine = create_engine(f"sqlite:///{tmp_path / 'optimistic-lock.db'}")
    # 创建全部模型对应的数据表。
    Base.metadata.create_all(bind=engine)
    # 创建绑定测试引擎的会话工厂。
    session_factory = sessionmaker(bind=engine)
    # 创建数据库会话。
    session = session_factory()
    # 创建测试用户。
    user = User(username="version-user", email="version@example.com", password_hash="hash", role="user")
    # 保存测试用户。
    session.add(user)
    # 写入用户。
    session.commit()
    # 保存初始更新时间。
    initial_updated_at = user.updated_at
    # 修改用户角色以触发更新。
    user.role = "admin"
    # 写入修改以触发乐观锁版本递增。
    session.commit()

    # 断言更新时间不早于初始值。
    assert user.updated_at >= initial_updated_at
    # 断言乐观锁版本随更新递增。
    assert user.lock_version == 2
    # 断言创建时间已被自动写入。
    assert user.created_at is not None
    # 关闭数据库会话。
    session.close()


# 验证迁移会重命名用户表并创建 LLM 对话持久化表。
def test_llm_chat_migration_renames_user_table_and_creates_required_tables():
    # 定位 LLM 对话持久化迁移文件。
    migration_path = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "20260901_0002_add_llm_chat_tables.py"
    # 读取迁移文件源码。
    migration_source = migration_path.read_text(encoding="utf-8")

    # 断言迁移会保留数据地重命名既有用户表。
    assert 'op.rename_table("users", "user")' in migration_source
    # 断言迁移会创建对话会话表。
    assert "op.create_table" in migration_source and '"chat_conversation"' in migration_source
    # 断言迁移会创建对话消息表。
    assert "op.create_table" in migration_source and '"chat_message"' in migration_source
    # 断言迁移会创建大模型调用日志表。
    assert "op.create_table" in migration_source and '"llm_call_log"' in migration_source
