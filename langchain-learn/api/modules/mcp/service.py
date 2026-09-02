"""MCP 连接配置、工具发现和 Agent 调用服务。"""

# 导入当前 Python 解释器路径。
import sys
# 导入文件系统路径类型。
from pathlib import Path
# 导入通用对象和可调用类型。
from typing import Any, Callable

# 导入兼容 Agent 工厂。
from api.core.agents import create_agent_runtime
# 导入 API 设置和 MCP 模式。
from api.core.config import ApiSettings, McpMode
# 导入稳定配置和上游异常。
from api.core.errors import ConfigurationError, UpstreamServiceError
# 导入 Agent 对外响应。
from api.core.schemas import AgentReply
# 导入共享 Agent 消息提取函数。
from api.modules.tools.service import build_agent_reply


# 根据运行模式构造 MCP adapter 连接配置。
def build_mcp_connections(
    settings: ApiSettings,
) -> dict[str, dict[str, object]]:
    # 为内置模式构造 stdio 子进程配置。
    if settings.mcp_mode is McpMode.LOCAL:
        # 定位项目根目录。
        project_root = Path(__file__).resolve().parents[3]
        # 定位内置 MCP Server 脚本。
        server_path = project_root / "mcp_servers" / "demo_server.py"
        # 返回只允许当前解释器和固定脚本的连接。
        return {
            "local-demo": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(server_path)],
                "cwd": str(project_root),
            }
        }
    # 确认远程模式配置了服务地址。
    if not settings.mcp_remote_url:
        # 抛出可操作且不含认证信息的配置错误。
        raise ConfigurationError("远程 MCP 模式需要 MCP_REMOTE_URL")
    # 构造远程 Streamable HTTP 连接。
    remote_connection: dict[str, object] = {
        "transport": "http",
        "url": settings.mcp_remote_url,
    }
    # 仅在存在请求头时传给 adapter。
    if settings.mcp_remote_headers:
        # 复制请求头避免调用方修改配置对象。
        remote_connection["headers"] = dict(settings.mcp_remote_headers)
    # 返回命名远程连接。
    return {"remote-demo": remote_connection}


# 创建可选依赖提供的 MCP client。
def create_mcp_client(connections: dict[str, dict[str, object]]) -> Any:
    # 延迟导入单独安装的 MCP adapter。
    try:
        # 导入多服务 MCP client。
        from langchain_mcp_adapters.client import MultiServerMCPClient
    # 在依赖未安装时提供明确配置错误。
    except ImportError as error:
        # 抛出稳定且可操作的提示。
        raise ConfigurationError(
            "MCP 调用需要安装 langchain-mcp-adapters 和 mcp"
        ) from error
    # 返回配置完成的 MCP client。
    return MultiServerMCPClient(connections)


# 定义 MCP 工具发现和 Agent 调用服务。
class McpService:
    # 初始化 MCP 配置、模型和可替换工厂。
    def __init__(
        self,
        settings: ApiSettings,
        model: Any,
        client_factory: Callable[[dict[str, dict[str, object]]], Any] = (
            create_mcp_client
        ),
        agent_factory: Callable[..., Any] = create_agent_runtime,
    ) -> None:
        # 预先校验并保存连接配置。
        self.connections = build_mcp_connections(settings)
        # 保存统一聊天模型。
        self.model = model
        # 保存可替换的 MCP client 工厂。
        self.client_factory = client_factory
        # 保存可替换的 Agent 工厂。
        self.agent_factory = agent_factory

    # 发现 MCP 工具并回答用户问题。
    async def chat(self, question: str) -> AgentReply:
        # 尝试完成工具发现和 Agent 调用。
        try:
            # 创建当前请求使用的无状态 MCP client。
            client = self.client_factory(self.connections)
            # 异步发现 MCP 服务暴露的工具。
            tools = await client.get_tools()
            # 创建只使用已发现 MCP 工具的 Agent。
            agent = self.agent_factory(
                model=self.model,
                tools=tools,
                system_prompt="需要外部能力时调用 MCP 服务提供的工具。",
            )
            # 异步调用 Agent。
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": question}]}
            )
            # 提取安全回答和调用摘要。
            return build_agent_reply(result["messages"])
        # 保留明确的配置异常。
        except ConfigurationError:
            # 继续抛出配置异常供 HTTP 层映射。
            raise
        # 保留已经清理过的上游异常。
        except UpstreamServiceError:
            # 继续抛出稳定上游异常。
            raise
        # 捕获连接、发现或 Agent 调用异常。
        except Exception as error:
            # 映射为不泄露 URL 请求头的安全错误。
            raise UpstreamServiceError("MCP 服务调用失败") from error
