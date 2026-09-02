# 导入异步迭代器类型。
from collections.abc import AsyncIterator

# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient

# 导入流式 service 依赖。
from api.core.dependencies import get_streaming_service
# 导入应用工厂。
from api.main import create_app


# 定义按顺序产出文本的替身服务。
class FakeStreamingService:
    # 异步产出包含空值的固定分块。
    async def stream_tokens(self, question: str) -> AsyncIterator[str]:
        # 保存收到的问题。
        self.question = question
        # 产出第一个文本分块。
        yield "你"
        # 产出空分块以验证适配器行为。
        yield ""
        # 产出第二个文本分块。
        yield "好"


# 定义产生安全错误事件所需的失败服务。
class FailingStreamingService:
    # 在首个分块后模拟上游失败。
    async def stream_tokens(self, question: str) -> AsyncIterator[str]:
        # 先产出一个有效分块。
        yield "开"
        # 抛出包含内部信息的异常。
        raise RuntimeError("secret-upstream-detail")


# 验证纯文本端点连接全部分块。
def test_text_stream_returns_plain_text_chunks() -> None:
    # 创建隔离应用。
    application = create_app()
    # 创建替身流式服务。
    service = FakeStreamingService()
    # 覆盖真实模型依赖。
    application.dependency_overrides[get_streaming_service] = lambda: service
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用纯文本流式端点。
    response = client.post("/api/v1/stream/text", json={"question": "问候"})
    # 验证请求成功。
    assert response.status_code == 200
    # 验证返回纯文本媒体类型。
    assert response.headers["content-type"].startswith("text/plain")
    # 验证文本分块保持顺序。
    assert response.text == "你好"


# 验证 SSE 端点发送命名 token 和完成事件。
def test_sse_stream_returns_token_and_done_events() -> None:
    # 创建隔离应用。
    application = create_app()
    # 覆盖真实流式服务。
    application.dependency_overrides[get_streaming_service] = FakeStreamingService
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用 SSE 流式端点。
    response = client.post("/api/v1/stream/sse", json={"question": "问候"})
    # 验证返回 SSE 媒体类型。
    assert response.headers["content-type"].startswith("text/event-stream")
    # 验证有效 token 均被编码。
    assert response.text.count("event: token") == 2
    # 验证第一个 token 数据存在。
    assert 'data: {"token": "你"}' in response.text
    # 验证第二个 token 数据存在。
    assert 'data: {"token": "好"}' in response.text
    # 验证流正常完成事件存在。
    assert "event: done" in response.text


# 验证 SSE 上游失败被转换为安全错误事件。
def test_sse_stream_hides_upstream_error_details() -> None:
    # 创建隔离应用。
    application = create_app()
    # 覆盖为会失败的流式服务。
    application.dependency_overrides[get_streaming_service] = (
        FailingStreamingService
    )
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用 SSE 流式端点。
    response = client.post("/api/v1/stream/sse", json={"question": "问候"})
    # 验证返回错误事件而非中断 HTTP 响应。
    assert "event: error" in response.text
    # 验证响应不泄露原始异常。
    assert "secret-upstream-detail" not in response.text
