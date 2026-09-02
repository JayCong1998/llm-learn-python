# 导入异步运行工具。
import asyncio

# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient
# 导入确定性的 LangChain 替身模型。
from langchain_core.language_models.fake_chat_models import FakeListChatModel
# 导入测试框架。
import pytest

# 导入记忆 service 依赖。
from api.core.dependencies import get_memory_service
# 导入应用工厂和生命周期函数。
from api.main import _application_lifespan, create_app
# 导入依赖模块以替换模型工厂。
from api.core import dependencies


# 定义记忆 API 的替身服务。
class FakeMemoryService:
    # 返回固定的有上下文回答。
    def chat(self, session_id: str, message: str) -> str:
        # 保存会话标识。
        self.session_id = session_id
        # 保存当前消息。
        self.message = message
        # 返回固定回答。
        return "记得你叫小明"

    # 记录被清理的会话。
    def clear(self, session_id: str) -> None:
        # 保存清理目标。
        self.cleared_session_id = session_id


# 验证记忆聊天和清理端点共享会话标识。
def test_memory_chat_and_clear_endpoints() -> None:
    # 创建隔离应用。
    application = create_app()
    # 创建替身记忆服务。
    service = FakeMemoryService()
    # 覆盖真实存储依赖。
    application.dependency_overrides[get_memory_service] = lambda: service
    # 创建同步测试客户端。
    client = TestClient(application)
    # 发送有会话标识的聊天请求。
    chat_response = client.post(
        "/api/v1/memory/chat",
        json={"session_id": "session-a", "message": "我叫什么？"},
    )
    # 验证聊天响应结构。
    assert chat_response.json() == {
        "data": {"session_id": "session-a", "answer": "记得你叫小明"}
    }
    # 清理同一会话。
    clear_response = client.delete("/api/v1/memory/session-a")
    # 验证清理响应结构。
    assert clear_response.json() == {
        "data": {"session_id": "session-a", "cleared": True}
    }
    # 验证服务收到清理目标。
    assert service.cleared_session_id == "session-a"


# 验证每个 FastAPI 应用独立拥有并释放记忆服务。
def test_app_lifespan_owns_memory_service(monkeypatch) -> None:
    # 固定使用进程内记忆后端。
    monkeypatch.setenv("MEMORY_BACKEND", "memory")
    # 替换真实模型为确定性聊天模型。
    monkeypatch.setattr(
        dependencies,
        "get_chat_model",
        lambda: FakeListChatModel(responses=["记住了"]),
    )
    # 创建隔离应用。
    application = create_app()
    # 通过上下文管理器启动并关闭应用生命周期。
    with TestClient(application) as client:
        # 触发记忆服务的延迟创建。
        response = client.post(
            "/api/v1/memory/chat",
            json={"session_id": "session-a", "message": "我叫小明"},
        )
        # 验证请求成功。
        assert response.status_code == 200
        # 验证应用状态拥有当前记忆服务。
        assert application.state.memory_service is not None
    # 验证应用关闭后释放服务引用。
    assert application.state.memory_service is None


# 验证应用关闭时关闭 SQLite 连接。
def test_app_lifespan_closes_sqlite_connection(monkeypatch) -> None:
    # 定义可观察关闭状态的替身连接。
    class FakeConnection:
        # 初始化未关闭状态。
        def __init__(self) -> None:
            # 保存连接关闭标记。
            self.closed = False

        # 模拟关闭 SQLite 连接。
        def close(self) -> None:
            # 标记连接已经关闭。
            self.closed = True

    # 定义供生命周期组装的最小记忆服务。
    class LifecycleMemoryService:
        # 接收模型和 saver 以匹配真实构造函数。
        def __init__(self, model, checkpointer) -> None:
            # 保存 saver 以便确认构造完成。
            self.checkpointer = checkpointer

        # 返回固定聊天回答。
        def chat(self, session_id: str, message: str) -> str:
            # 返回确定性生命周期测试结果。
            return "已保存"

    # 创建替身连接。
    connection = FakeConnection()
    # 创建替身 saver。
    checkpointer = object()
    # 固定使用 SQLite 后端。
    monkeypatch.setenv("MEMORY_BACKEND", "sqlite")
    # 替换真实模型构造。
    monkeypatch.setattr(dependencies, "get_chat_model", lambda: object())
    # 替换需要可选依赖的 SQLite saver 工厂。
    monkeypatch.setattr(
        dependencies,
        "_create_sqlite_checkpointer",
        lambda _path: (checkpointer, connection),
    )
    # 替换真实 Agent 记忆服务。
    monkeypatch.setattr(
        dependencies,
        "MemoryChatService",
        LifecycleMemoryService,
    )
    # 创建隔离应用。
    application = create_app()
    # 启动应用并触发 SQLite 资源创建。
    with TestClient(application) as client:
        # 调用消息记忆端点。
        response = client.post(
            "/api/v1/memory/chat",
            json={"session_id": "session-a", "message": "保存"},
        )
        # 验证请求成功。
        assert response.status_code == 200
        # 验证运行期间连接保持打开。
        assert connection.closed is False
    # 验证生命周期关闭了连接。
    assert connection.closed is True


# 验证异常退出时仍逐个关闭全部应用资源。
def test_app_lifespan_closes_all_resources_after_failure() -> None:
    # 保存实际执行过的关闭动作。
    closed_resources = []

    # 定义会失败的资源关闭函数。
    def failing_closer() -> None:
        # 记录失败关闭函数已被调用。
        closed_resources.append("failing")
        # 模拟单个资源关闭失败。
        raise RuntimeError("close-error")

    # 定义正常的资源关闭函数。
    def successful_closer() -> None:
        # 记录正常关闭函数已被调用。
        closed_resources.append("successful")

    # 异步触发应用生命周期内部异常。
    async def exercise_lifespan() -> None:
        # 创建隔离应用。
        application = create_app()
        # 注入可观察的资源关闭函数。
        application.state.resource_closers.extend(
            [successful_closer, failing_closer]
        )
        # 验证业务异常继续传播给调用方。
        with pytest.raises(ValueError):
            # 启动应用生命周期上下文。
            async with _application_lifespan(application):
                # 模拟应用运行期间失败。
                raise ValueError("application-error")
        # 验证关闭函数列表已经清空。
        assert application.state.resource_closers == []

    # 执行异步生命周期测试。
    asyncio.run(exercise_lifespan())
    # 验证单个关闭失败没有阻止其他资源关闭。
    assert closed_resources == ["failing", "successful"]


# 验证 SQLite Agent 构造失败时立即关闭本次连接。
def test_sqlite_connection_closes_when_memory_service_construction_fails(
    monkeypatch,
) -> None:
    # 定义可观察关闭状态的替身连接。
    class FakeConnection:
        # 初始化未关闭状态。
        def __init__(self) -> None:
            # 保存连接关闭标记。
            self.closed = False

        # 模拟关闭 SQLite 连接。
        def close(self) -> None:
            # 标记连接已经关闭。
            self.closed = True

    # 定义会失败的记忆服务构造器。
    class BrokenMemoryService:
        # 接收真实构造参数并模拟失败。
        def __init__(self, model, checkpointer) -> None:
            # 抛出 Agent 构造异常。
            raise RuntimeError("agent-construction-error")

    # 创建替身连接。
    connection = FakeConnection()
    # 固定使用 SQLite 后端。
    monkeypatch.setenv("MEMORY_BACKEND", "sqlite")
    # 替换真实模型构造。
    monkeypatch.setattr(dependencies, "get_chat_model", lambda: object())
    # 替换 SQLite saver 工厂。
    monkeypatch.setattr(
        dependencies,
        "_create_sqlite_checkpointer",
        lambda _path: (object(), connection),
    )
    # 替换为会失败的服务构造器。
    monkeypatch.setattr(dependencies, "MemoryChatService", BrokenMemoryService)
    # 创建隔离应用。
    application = create_app()
    # 启动测试客户端。
    with TestClient(application) as client:
        # 验证构造异常继续传播。
        with pytest.raises(RuntimeError):
            # 触发 SQLite 服务首次构造。
            client.post(
                "/api/v1/memory/chat",
                json={"session_id": "session-a", "message": "保存"},
            )
        # 验证失败连接没有注册到长期关闭列表。
        assert application.state.resource_closers == []
    # 验证构造失败后已立即关闭连接。
    assert connection.closed is True
