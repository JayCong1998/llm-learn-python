# LLM Chat Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add persistent LLM chat domain tables with common audit, optimistic-lock, and soft-delete fields.

**Architecture:** Rename the existing `users` table to `user` while preserving existing rows, then add ORM models for conversations, messages, and per-assistant-message LLM invocation logs. A second Alembic migration upgrades the existing initial schema; no API, service, repository, or tool-call persistence is added.

**Tech Stack:** Python 3.11, SQLAlchemy 2 ORM, Alembic, SQLite, pytest.

---

### Task 1: Specify and test LLM persistence ORM mappings

**Files:**
- Create: `fastapi-scaffold/tests/test_llm_chat_persistence.py`
- Modify: `fastapi-scaffold/tests/test_foundation.py`

- [ ] **Step 1: Write failing tests for the four tables, relations, constrained roles, and common columns**

```python
def test_llm_chat_models_create_required_tables_and_common_columns(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'llm-chat.db'}")
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)

    assert {"user", "chat_conversation", "chat_message", "llm_call_log"} <= set(inspector.get_table_names())
    for table_name in ("user", "chat_conversation", "chat_message", "llm_call_log"):
        assert {"created_at", "updated_at", "lock_version", "deleted"} <= {column["name"] for column in inspector.get_columns(table_name)}


def test_llm_call_log_belongs_to_one_assistant_message(tmp_path):
    # Persist a user, conversation, user message, assistant message, and one call log.
    # Assert the log is linked to the assistant message and no log is linked to the user message.
```

- [ ] **Step 2: Run the focused tests and verify they fail because the models do not exist**

Run: `python -m pytest tests/test_llm_chat_persistence.py -q`

Expected: FAIL with an import error for the new chat model modules.

- [ ] **Step 3: Add the models and common columns**

```python
class ChatConversation(Base):
    __tablename__ = "chat_conversation"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="RESTRICT"), nullable=False, index=True)


class ChatMessage(Base):
    __tablename__ = "chat_message"
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    __table_args__ = (CheckConstraint("role IN ('system', 'user', 'assistant')", name="ck_chat_messages_role"),)


class LlmCallLog(Base):
    __tablename__ = "llm_call_log"
    message_id: Mapped[int] = mapped_column(ForeignKey("chat_message.id", ondelete="RESTRICT"), nullable=False, unique=True)
```

Each new or changed Python statement must have the required preceding Chinese line comment. Every table includes `created_at`, `updated_at`, `lock_version`, and `deleted`; `llm_call_logs.message_id` is unique and points only to an assistant message by service-layer convention.

- [ ] **Step 4: Run the focused tests and verify they pass**

Run: `python -m pytest tests/test_llm_chat_persistence.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fastapi-scaffold/app/models fastapi-scaffold/tests/test_llm_chat_persistence.py
git commit -m "feat: add LLM chat persistence models"
```

### Task 2: Add an Alembic upgrade for existing databases

**Files:**
- Create: `fastapi-scaffold/alembic/versions/20260901_0002_add_llm_chat_tables.py`
- Modify: `fastapi-scaffold/alembic/env.py`
- Test: `fastapi-scaffold/tests/test_llm_chat_persistence.py`

- [ ] **Step 1: Write a failing migration-content test**

```python
def test_llm_chat_migration_creates_tables_and_user_common_columns():
    migration_source = Path("alembic/versions/20260901_0002_add_llm_chat_tables.py").read_text(encoding="utf-8")

    assert 'op.rename_table("users", "user")' in migration_source
    assert '"chat_conversation"' in migration_source
    assert '"chat_message"' in migration_source
    assert '"llm_call_log"' in migration_source
```

- [ ] **Step 2: Run the migration test and verify it fails because the revision file is absent**

Run: `python -m pytest tests/test_llm_chat_persistence.py::test_llm_chat_migration_creates_tables_and_user_common_columns -q`

Expected: FAIL with `FileNotFoundError`.

- [ ] **Step 3: Create the migration and import all models in Alembic environment**

```python
def upgrade() -> None:
    op.rename_table("users", "user")
    op.create_table("chat_conversation", ...)
    op.create_table("chat_message", ...)
    op.create_table("llm_call_log", ...)
```

Use a temporary nullable `users.updated_at` migration column so existing rows remain migratable, populate it with the current timestamp, then change it to non-null. Include matching indexes and a downgrade that removes child tables before parent columns.

- [ ] **Step 4: Run the focused persistence tests and verify they pass**

Run: `python -m pytest tests/test_llm_chat_persistence.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add fastapi-scaffold/alembic fastapi-scaffold/tests/test_llm_chat_persistence.py
git commit -m "feat: migrate LLM chat persistence schema"
```

### Task 3: Verify the complete scaffold

**Files:**
- Modify: `fastapi-scaffold/README.md`
- Test: `fastapi-scaffold/tests/`

- [ ] **Step 1: Add a short data-model note to the README**

```markdown
### LLM 对话持久化

`user`、`chat_conversation`、`chat_message` 与 `llm_call_log` 均包含创建、更新时间、乐观锁版本与逻辑删除字段。工具调用只保留在单次请求的内存上下文中，不写入数据库。
```

- [ ] **Step 2: Run the full backend suite**

Run: `python -m pytest -q`

Expected: PASS with all tests green.

- [ ] **Step 3: Apply migrations to a temporary SQLite database and inspect the schema**

Run: `$env:DATABASE_URL = "sqlite:///./data/llm-chat-verify.db"; python -m alembic upgrade head`

Expected: Alembic upgrades through `20260901_0002` without errors; the temporary database has all four tables.

- [ ] **Step 4: Commit**

```bash
git add fastapi-scaffold/README.md
git commit -m "docs: describe LLM chat persistence"
```
