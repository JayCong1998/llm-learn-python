# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient

# 导入工具 service 依赖。
from api.core.dependencies import get_tool_service
# 导入应用工厂。
from api.main import create_app
# 导入 Agent 响应类型。
from api.core.schemas import AgentReply, ToolCallTrace


# 定义返回固定轨迹的替身工具服务。
class FakeToolService:
    # 返回固定 Agent 回答。
    def chat(self, question: str) -> AgentReply:
        # 保存收到的问题。
        self.question = question
        # 返回工具调用摘要。
        return AgentReply(
            answer="结果是 8",
            tool_calls=[
                ToolCallTrace(
                    name="safe_calculate",
                    arguments={"expression": "3+5"},
                )
            ],
        )


# 验证工具调用 API 返回可观察轨迹。
def test_tool_endpoint_returns_answer_and_call_trace() -> None:
    # 创建隔离应用。
    application = create_app()
    # 覆盖真实工具 Agent。
    application.dependency_overrides[get_tool_service] = FakeToolService
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用工具聊天端点。
    response = client.post(
        "/api/v1/tools/chat",
        json={"question": "计算 3+5"},
    )
    # 验证完整响应结构。
    assert response.json() == {
        "data": {
            "answer": "结果是 8",
            "tool_calls": [
                {
                    "name": "safe_calculate",
                    "arguments": {"expression": "3+5"},
                }
            ],
        }
    }
