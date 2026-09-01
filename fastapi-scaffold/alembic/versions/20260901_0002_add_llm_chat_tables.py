"""重命名用户表并创建 LLM 对话持久化表。"""

# 导入 Alembic 迁移操作工具。
from alembic import op
# 导入 SQLAlchemy 类型定义。
import sqlalchemy as sa

# 定义本迁移的唯一版本标识。
revision = "20260901_0002"
# 定义本迁移依赖初始数据库结构。
down_revision = "20260831_0001"
# 定义分支标签为空。
branch_labels = None
# 定义依赖版本为空。
depends_on = None


# 将既有用户表升级为 LLM 对话持久化结构。
def upgrade() -> None:
    # 保留原有用户数据地将复数用户表重命名为单数表。
    op.rename_table("users", "user")
    # 在用户表中补充新的公共持久化字段。
    with op.batch_alter_table("user") as batch_operation:
        # 添加允许暂时为空的更新时间字段以兼容已有用户数据。
        batch_operation.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
        # 添加乐观锁版本字段并为已有记录提供默认值。
        batch_operation.add_column(sa.Column("lock_version", sa.Integer(), nullable=False, server_default="0"))
        # 添加逻辑删除标志并为已有记录提供默认值。
        batch_operation.add_column(sa.Column("deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
    # 为既有用户记录写入更新时间。
    op.execute(sa.text("UPDATE user SET updated_at = CURRENT_TIMESTAMP"))
    # 将已有用户记录补齐后把更新时间调整为非空。
    with op.batch_alter_table("user") as batch_operation:
        # 将更新时间字段设为非空。
        batch_operation.alter_column("updated_at", existing_type=sa.DateTime(timezone=True), nullable=False)
    # 创建用户对话会话表。
    op.create_table(
        "chat_conversation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lock_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    # 创建会话所属用户索引。
    op.create_index("ix_chat_conversation_user_id", "chat_conversation", ["user_id"], unique=False)
    # 创建用户对话消息表。
    op.create_table(
        "chat_message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lock_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.CheckConstraint("role IN ('system', 'user', 'assistant')", name="ck_chat_message_role"),
        sa.ForeignKeyConstraint(["conversation_id"], ["chat_conversation.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    # 创建消息所属会话索引。
    op.create_index("ix_chat_message_conversation_id", "chat_message", ["conversation_id"], unique=False)
    # 创建每条助手消息对应的大模型调用日志表。
    op.create_table(
        "llm_call_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lock_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["message_id"], ["chat_message.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("message_id"),
    )


# 回退 LLM 对话持久化结构并恢复既有用户表名称。
def downgrade() -> None:
    # 删除大模型调用日志表。
    op.drop_table("llm_call_log")
    # 删除消息所属会话索引。
    op.drop_index("ix_chat_message_conversation_id", table_name="chat_message")
    # 删除用户对话消息表。
    op.drop_table("chat_message")
    # 删除会话所属用户索引。
    op.drop_index("ix_chat_conversation_user_id", table_name="chat_conversation")
    # 删除用户对话会话表。
    op.drop_table("chat_conversation")
    # 删除用户表补充的公共字段。
    with op.batch_alter_table("user") as batch_operation:
        # 删除逻辑删除标志字段。
        batch_operation.drop_column("deleted")
        # 删除乐观锁版本字段。
        batch_operation.drop_column("lock_version")
        # 删除更新时间字段。
        batch_operation.drop_column("updated_at")
    # 将用户表名称恢复为旧版复数名称。
    op.rename_table("user", "users")
