# 导入简单命名空间构造替身消息。
from types import SimpleNamespace

# 导入确定性的 LangChain 替身模型。
from langchain_core.language_models.fake_chat_models import FakeListChatModel
# 导入进程内 LangGraph saver。
from langgraph.checkpoint.memory import InMemorySaver

# 导入消息记忆服务。
from api.modules.memory.service import MemoryChatService
# 导入稳定上游异常。
from api.core.errors import UpstreamServiceError
# 导入测试框架。
import pytest


# 定义可观察 Agent 调用的替身。
class FakeAgent:
    # 模拟一次带记忆配置的调用。
    def invoke(self, payload, config):
        # 保存当前增量消息。
        self.payload = payload
        # 保存线程配置。
        self.config = config
        # 返回固定助手消息。
        return {"messages": [SimpleNamespace(content="记得你叫小明")]}


# 定义可观察清理调用的替身 checkpointer。
class FakeCheckpointer:
    # 删除指定线程。
    def delete_thread(self, thread_id: str) -> None:
        # 保存被删除的线程标识。
        self.deleted_thread_id = thread_id


# 验证会话标识映射为 LangGraph 线程标识。
def test_memory_service_maps_session_to_thread_id() -> None:
    # 创建替身 Agent。
    agent = FakeAgent()
    # 创建替身检查点存储。
    checkpointer = FakeCheckpointer()
    # 创建注入替身 Agent 的记忆服务。
    service = MemoryChatService(
        model=object(),
        checkpointer=checkpointer,
        agent_factory=lambda **_values: agent,
    )
    # 在指定会话中发送消息。
    answer = service.chat("session-a", "我叫什么？")
    # 验证最终助手正文被返回。
    assert answer == "记得你叫小明"
    # 验证会话标识传给 thread_id。
    assert agent.config == {"configurable": {"thread_id": "session-a"}}
    # 验证只提交当前新增消息。
    assert agent.payload == {
        "messages": [{"role": "user", "content": "我叫什么？"}]
    }


# 验证清理操作只删除指定线程。
def test_memory_service_clears_selected_thread() -> None:
    # 创建替身检查点存储。
    checkpointer = FakeCheckpointer()
    # 创建记忆服务。
    service = MemoryChatService(
        model=object(),
        checkpointer=checkpointer,
        agent_factory=lambda **_values: FakeAgent(),
    )
    # 清理指定会话。
    service.clear("session-b")
    # 验证只向存储传入目标线程。
    assert checkpointer.deleted_thread_id == "session-b"


# 验证真实 InMemorySaver 延续历史并隔离线程。
def test_memory_service_persists_and_isolates_real_in_memory_threads() -> None:
    # 创建可连续返回固定答案的模型。
    model = FakeListChatModel(
        responses=["记住了", "你叫小明", "另一个会话"],
    )
    # 创建真实进程内检查点存储。
    checkpointer = InMemorySaver()
    # 创建使用真实 LangGraph Agent 的服务。
    service = MemoryChatService(model=model, checkpointer=checkpointer)
    # 写入第一轮会话。
    service.chat("session-a", "我叫小明")
    # 写入同一会话的第二轮。
    service.chat("session-a", "我叫什么？")
    # 写入不同会话。
    service.chat("session-b", "这是另一个会话")
    # 读取第一段线程的真实图状态。
    first_state = service.agent.get_state(
        {"configurable": {"thread_id": "session-a"}}
    )
    # 读取第二段线程的真实图状态。
    second_state = service.agent.get_state(
        {"configurable": {"thread_id": "session-b"}}
    )
    # 提取第一段会话的消息正文。
    first_contents = [
        message.content for message in first_state.values["messages"]
    ]
    # 提取第二段会话的消息正文。
    second_contents = [
        message.content for message in second_state.values["messages"]
    ]
    # 验证同一线程保留两轮用户消息。
    assert "我叫小明" in first_contents
    # 验证同一线程保留后续问题。
    assert "我叫什么？" in first_contents
    # 验证另一个线程不包含第一段会话。
    assert "我叫小明" not in second_contents
    # 清除第一段会话。
    service.clear("session-a")
    # 验证第一段线程检查点已删除。
    assert checkpointer.get_tuple(
        {"configurable": {"thread_id": "session-a"}}
    ) is None
    # 验证第二段线程仍然存在。
    assert checkpointer.get_tuple(
        {"configurable": {"thread_id": "session-b"}}
    ) is not None


# 验证记忆 Agent 构造失败映射为稳定上游异常。
def test_memory_service_maps_agent_construction_failure() -> None:
    # 定义会失败的 Agent 工厂。
    def broken_agent_factory(**_values):
        # 抛出内部兼容性错误。
        raise RuntimeError("internal-agent-error")

    # 验证构造失败不会成为未处理异常。
    with pytest.raises(UpstreamServiceError):
        # 尝试创建记忆服务。
        MemoryChatService(
            model=object(),
            checkpointer=FakeCheckpointer(),
            agent_factory=broken_agent_factory,
        )
