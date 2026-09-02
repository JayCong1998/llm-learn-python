# 导入异步运行工具。
import asyncio
# 导入文件系统路径。
from pathlib import Path

# 导入 API 配置类型。
from api.core.config import ApiSettings, McpMode, MemoryBackend
# 导入 MCP 服务和连接构造函数。
from api.modules.mcp.service import McpService, build_mcp_connections


# 创建指定 MCP 模式的测试配置。
def make_settings(mode: McpMode) -> ApiSettings:
    # 返回不含真实认证信息的测试配置。
    return ApiSettings(
        memory_backend=MemoryBackend.MEMORY,
        memory_sqlite_path=Path("memory.sqlite"),
        mcp_mode=mode,
        mcp_remote_url="https://mcp.example.invalid/mcp",
        mcp_remote_headers={"Authorization": "Bearer test"},
    )


# 验证本地模式使用当前 Python 启动内置 stdio 服务。
def test_build_mcp_connections_for_local_server() -> None:
    # 构造本地 MCP 连接。
    connections = build_mcp_connections(make_settings(McpMode.LOCAL))
    # 读取内置服务配置。
    local = connections["local-demo"]
    # 验证使用 stdio 传输。
    assert local["transport"] == "stdio"
    # 验证服务脚本路径正确。
    assert str(local["args"][0]).endswith("mcp_servers\\demo_server.py")


# 验证远程模式保留 URL 和请求头。
def test_build_mcp_connections_for_remote_server() -> None:
    # 构造远程 MCP 连接。
    connections = build_mcp_connections(make_settings(McpMode.REMOTE))
    # 读取远程服务配置。
    remote = connections["remote-demo"]
    # 验证使用 HTTP 传输。
    assert remote["transport"] == "http"
    # 验证远程地址。
    assert remote["url"] == "https://mcp.example.invalid/mcp"
    # 验证请求头传给 adapter。
    assert remote["headers"] == {"Authorization": "Bearer test"}


# 定义返回一个工具的替身 MCP client。
class FakeMcpClient:
    # 异步返回固定工具集合。
    async def get_tools(self):
        # 返回可观察的工具对象。
        return ["mcp-add-tool"]


# 定义返回最终消息的替身 Agent。
class FakeMcpAgent:
    # 异步模拟 MCP Agent 调用。
    async def ainvoke(self, payload):
        # 延迟导入消息类型以构造轨迹。
        from langchain_core.messages import AIMessage
        # 返回最终助手回答。
        return {"messages": [AIMessage(content="MCP 结果是 8")]}


# 验证 MCP 工具被交给 Agent 并返回最终回答。
def test_mcp_service_loads_tools_and_invokes_agent() -> None:
    # 保存构造 Agent 时收到的参数。
    captured = {}

    # 定义可观察 Agent 工厂。
    def agent_factory(**values):
        # 保存构造参数。
        captured.update(values)
        # 返回异步替身 Agent。
        return FakeMcpAgent()

    # 创建注入替身 client 的 MCP 服务。
    service = McpService(
        settings=make_settings(McpMode.LOCAL),
        model=object(),
        client_factory=lambda _connections: FakeMcpClient(),
        agent_factory=agent_factory,
    )
    # 运行异步 MCP 聊天。
    result = asyncio.run(service.chat("计算 3+5"))
    # 验证最终回答。
    assert result.answer == "MCP 结果是 8"
    # 验证发现的工具传入 Agent。
    assert captured["tools"] == ["mcp-add-tool"]
