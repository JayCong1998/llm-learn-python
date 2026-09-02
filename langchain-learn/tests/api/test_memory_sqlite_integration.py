# 导入测试框架。
import pytest

# 在可选 SQLite 依赖缺失时跳过本模块。
sqlite_module = pytest.importorskip("langgraph.checkpoint.sqlite")

# 导入确定性的 LangChain 替身模型。
from langchain_core.language_models.fake_chat_models import FakeListChatModel

# 导入消息记忆服务。
from api.modules.memory.service import MemoryChatService

# 读取可选包提供的 SQLite saver。
SqliteSaver = sqlite_module.SqliteSaver


# 验证 SQLite 会话在关闭重开后保留并可按线程删除。
def test_sqlite_memory_survives_reopen_and_deletes_selected_thread(tmp_path) -> None:
    # 创建仅属于当前测试的数据库路径。
    database_path = tmp_path / "memory.sqlite"
    # 打开第一段 SQLite saver 生命周期。
    with SqliteSaver.from_conn_string(str(database_path)) as first_saver:
        # 创建首次写入使用的确定性模型。
        first_model = FakeListChatModel(responses=["已经记住"])
        # 创建使用真实 SQLite saver 的记忆服务。
        first_service = MemoryChatService(
            model=first_model,
            checkpointer=first_saver,
        )
        # 写入需要跨重启保留的会话消息。
        first_service.chat("persistent-session", "我叫小明")
    # 重新打开同一个数据库文件。
    with SqliteSaver.from_conn_string(str(database_path)) as reopened_saver:
        # 创建重开后只用于读取图状态的确定性模型。
        reopened_model = FakeListChatModel(responses=["备用回答"])
        # 创建绑定重开 saver 的新服务实例。
        reopened_service = MemoryChatService(
            model=reopened_model,
            checkpointer=reopened_saver,
        )
        # 读取持久会话的图状态。
        state = reopened_service.agent.get_state(
            {"configurable": {"thread_id": "persistent-session"}}
        )
        # 提取重新加载后的全部消息正文。
        contents = [message.content for message in state.values["messages"]]
        # 验证用户消息确实跨连接保留。
        assert "我叫小明" in contents
        # 清除指定持久会话。
        reopened_service.clear("persistent-session")
        # 验证目标线程已经从 SQLite 删除。
        assert reopened_saver.get_tuple(
            {"configurable": {"thread_id": "persistent-session"}}
        ) is None
