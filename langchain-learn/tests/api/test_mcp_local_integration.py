# 导入异步运行工具。
import asyncio
# 导入文件系统路径类型。
from pathlib import Path

# 导入测试框架。
import pytest

# 在可选 MCP SDK 缺失时跳过本模块。
pytest.importorskip("mcp")
# 在可选 LangChain MCP adapter 缺失时跳过本模块。
client_module = pytest.importorskip("langchain_mcp_adapters.client")

# 导入 API 配置类型。
from api.core.config import ApiSettings, McpMode, MemoryBackend
# 导入本地 MCP 连接构造函数。
from api.modules.mcp.service import build_mcp_connections

# 读取可选包提供的多服务 MCP client。
MultiServerMCPClient = client_module.MultiServerMCPClient


# 异步发现并真实调用内置 stdio MCP 工具。
async def _load_and_call_local_mcp_tools() -> tuple[set[str], float]:
    # 创建本地 MCP 模式测试配置。
    settings = ApiSettings(
        memory_backend=MemoryBackend.MEMORY,
        memory_sqlite_path=Path("memory.sqlite"),
        mcp_mode=McpMode.LOCAL,
        mcp_remote_url=None,
        mcp_remote_headers={},
    )
    # 创建连接内置 MCP Server 的真实客户端。
    client = MultiServerMCPClient(build_mcp_connections(settings))
    # 通过 stdio 子进程发现全部工具。
    tools = await client.get_tools()
    # 按工具名建立可调用索引。
    tools_by_name = {tool.name: tool for tool in tools}
    # 真实调用内置加法工具。
    result = await tools_by_name["add"].ainvoke({"a": 3, "b": 5})
    # 返回工具名称和数值结果。
    return set(tools_by_name), float(result)


# 验证 adapter 能发现并调用内置 stdio MCP Server。
def test_local_mcp_server_exposes_and_runs_tools() -> None:
    # 执行真实异步 MCP 集成流程。
    tool_names, result = asyncio.run(_load_and_call_local_mcp_tools())
    # 验证两个教学工具都被发现。
    assert {"add", "city_note"}.issubset(tool_names)
    # 验证真实 MCP 调用返回正确加法结果。
    assert result == 8.0
