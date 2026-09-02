# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient

# 导入 MCP service 依赖。
from api.core.dependencies import get_mcp_service
# 导入 Agent 响应类型。
from api.core.schemas import AgentReply
# 导入应用工厂。
from api.main import create_app


# 定义 MCP API 的异步替身服务。
class FakeMcpService:
    # 返回固定 MCP 回答。
    async def chat(self, question: str) -> AgentReply:
        # 保存收到的问题。
        self.question = question
        # 返回无需工具轨迹的固定回答。
        return AgentReply(answer="MCP 结果是 8")


# 验证 MCP 聊天 API 等待异步 service。
def test_mcp_endpoint_returns_agent_reply() -> None:
    # 创建隔离应用。
    application = create_app()
    # 覆盖真实 MCP 连接依赖。
    application.dependency_overrides[get_mcp_service] = FakeMcpService
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用 MCP 聊天端点。
    response = client.post(
        "/api/v1/mcp/chat",
        json={"question": "计算 3+5"},
    )
    # 验证统一 Agent 响应结构。
    assert response.json() == {
        "data": {"answer": "MCP 结果是 8", "tool_calls": []}
    }
