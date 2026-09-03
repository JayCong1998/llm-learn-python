# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient
# 导入异步运行工具。
import asyncio
# 导入 HTTP 异常类型。
import httpx
# 导入 LangChain AI 消息类型。
from langchain_core.messages import AIMessage

# 导入唯一的 FastAPI 应用入口。
import main as app_main
# 导入待测试的流式应用模块。
import streaming_demo.main as streaming_main
# 导入待测试的工具 Agent 应用模块。
import tool_agent_demo.main as agent_main


# 定义可控的流式语言模型替身。
class FakeStreamingModel:
    # 定义异步流式响应方法。
    async def astream(self, messages):
        # 产出第一个测试文本块。
        yield type("Chunk", (), {"content": "你好"})()
        # 产出第二个测试文本块。
        yield type("Chunk", (), {"content": "，世界"})()


# 定义会请求时间工具的替身聊天模型。
class FakeToolCallingModel:
    # 保存绑定的工具列表。
    def bind_tools(self, tools):
        # 记录模型可调用的工具。
        self.tools = tools
        # 返回支持调用的模型实例。
        return self

    # 根据对话阶段返回工具调用或最终回答。
    async def ainvoke(self, messages):
        # 在首次调用时请求当前时间工具。
        if len(messages) == 1:
            # 返回时间工具调用请求。
            return AIMessage(content="", tool_calls=[{"name": "get_current_time", "args": {}, "id": "time-1"}])
        # 在接收工具结果后返回最终回答。
        return AIMessage(content="已查询当前时间。")


# 验证天气工具将网络错误转换为文本结果。
def test_weather_tool_returns_message_when_network_fails(monkeypatch):
    # 定义会触发连接错误的异步客户端替身。
    class FailingAsyncClient:
        # 接收与真实客户端一致的初始化参数。
        def __init__(self, **kwargs):
            # 忽略测试中不需要的客户端配置。
            pass

        # 返回异步上下文中的客户端。
        async def __aenter__(self):
            # 返回当前替身实例。
            return self

        # 结束异步上下文。
        async def __aexit__(self, exc_type, exc_value, traceback):
            # 不抑制上下文中的异常。
            return False

        # 模拟天气服务连接失败。
        async def get(self, *args, **kwargs):
            # 抛出 HTTP 客户端连接错误。
            raise httpx.ConnectError("network unavailable")

    # 将 HTTP 客户端替换为失败替身。
    monkeypatch.setattr(agent_main.httpx, "AsyncClient", FailingAsyncClient)
    # 调用天气工具并获取文本结果。
    result = asyncio.run(agent_main.get_weather.ainvoke({"city": "北京"}))
    # 断言连接错误被转换为友好提示。
    assert result == "天气查询暂时不可用，请稍后重试。"


# 验证 Agent API 允许 LLM 调用当前时间工具。
def test_agent_api_uses_llm_tools(monkeypatch):
    # 创建会请求工具的替身模型。
    fake_model = FakeToolCallingModel()
    # 将模型工厂替换为工具调用替身。
    monkeypatch.setattr(agent_main, "get_llm", lambda: fake_model)
    # 创建应用测试客户端。
    client = TestClient(app_main.app)
    # 请求 Agent 接口。
    response = client.get("/agent/chat", params={"message": "现在几点？"})
    # 断言响应成功。
    assert response.status_code == 200
    # 断言返回模型的最终回答。
    assert response.json() == {"content": "已查询当前时间。"}
    # 断言模型已绑定时间与天气工具。
    assert {tool.name for tool in fake_model.tools} == {"get_current_time", "get_weather"}


# 验证应用可从 .env 文件加载 MiniMax 配置。
def test_load_environment_reads_dotenv_file(tmp_path, monkeypatch):
    # 创建临时环境变量文件路径。
    env_file = tmp_path / ".env"
    # 写入测试用 MiniMax 配置。
    env_file.write_text("MINIMAX_API_KEY=dotenv-key\n", encoding="utf-8")
    # 清除已有的测试环境变量。
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    # 加载临时环境变量文件。
    streaming_main.load_environment(env_file)
    # 断言密钥已写入进程环境。
    assert streaming_main.os.getenv("MINIMAX_API_KEY") == "dotenv-key"


# 验证模型工厂读取 MiniMax 的 OpenAI 兼容配置。
def test_get_llm_uses_minimax_openai_compatible_settings(monkeypatch):
    # 定义用于记录初始化参数的替身模型。
    class FakeChatOpenAI:
        # 保存模型初始化参数。
        def __init__(self, **kwargs):
            # 记录传入的模型配置。
            self.kwargs = kwargs

    # 设置 MiniMax API 密钥。
    monkeypatch.setenv("MINIMAX_API_KEY", "test-key")
    # 设置 MiniMax 模型名称。
    monkeypatch.setenv("MINIMAX_MODEL", "MiniMax-M2.7-highspeed")
    # 设置 MiniMax OpenAI 兼容端点。
    monkeypatch.setenv("MINIMAX_BASE_URL", "https://api.minimax.io/v1")
    # 将 LangChain 模型类替换为参数记录替身。
    monkeypatch.setattr(streaming_main, "ChatOpenAI", FakeChatOpenAI)
    # 创建语言模型实例。
    llm = streaming_main.get_llm()
    # 断言模型名称来自 MiniMax 配置。
    assert llm.kwargs["model"] == "MiniMax-M2.7-highspeed"
    # 断言 API 密钥来自 MiniMax 配置。
    assert llm.kwargs["api_key"] == "test-key"
    # 断言端点使用 OpenAI 兼容地址。
    assert llm.kwargs["base_url"] == "https://api.minimax.io/v1"


# 验证健康检查接口返回服务状态。
def test_health_check_returns_ok():
    # 创建应用测试客户端。
    client = TestClient(app_main.app)
    # 请求健康检查接口。
    response = client.get("/health")
    # 断言响应成功。
    assert response.status_code == 200
    # 断言服务状态内容。
    assert response.json() == {"status": "ok"}


# 验证 GET 聊天接口以 SSE 逐块返回语言模型文本。
def test_get_chat_stream_returns_sse_chunks(monkeypatch):
    # 将模型工厂替换为可控替身。
    monkeypatch.setattr(streaming_main, "get_llm", lambda: FakeStreamingModel())
    # 创建应用测试客户端。
    client = TestClient(app_main.app)
    # 通过查询参数请求流式聊天接口。
    response = client.get("/chat/stream", params={"message": "测试"})
    # 断言响应成功。
    assert response.status_code == 200
    # 断言响应采用 SSE 媒体类型。
    assert response.headers["content-type"].startswith("text/event-stream")
    # 断言响应按 SSE 格式输出每个文本块。
    assert response.text == 'data: {"content":"你好"}\n\ndata: {"content":"，世界"}\n\n'
