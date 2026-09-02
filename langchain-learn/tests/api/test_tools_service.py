# 导入 LangChain 消息类型。
from langchain_core.messages import AIMessage, ToolMessage
# 导入测试框架。
import pytest

# 导入待测工具服务函数。
from api.modules.tools.service import (
    ToolService,
    evaluate_expression,
)
# 导入稳定上游异常。
from api.core.errors import UpstreamServiceError


# 验证白名单计算器支持括号和四则运算。
def test_evaluate_expression_calculates_safe_arithmetic() -> None:
    # 计算确定性的四则运算。
    result = evaluate_expression("(3 + 5) * 12")
    # 验证计算结果。
    assert result == 96


# 验证计算器拒绝可能执行代码的表达式。
@pytest.mark.parametrize(
    "expression",
    ["__import__('os')", "open('x')", "(1).__class__", "2 ** 100"],
)
def test_evaluate_expression_rejects_unsafe_syntax(expression: str) -> None:
    # 验证所有非白名单语法均被拒绝。
    with pytest.raises(ValueError):
        # 尝试计算危险表达式。
        evaluate_expression(expression)


# 定义返回固定工具调用轨迹的替身 Agent。
class FakeToolAgent:
    # 模拟 Agent 调用结果。
    def invoke(self, payload):
        # 返回工具请求、工具结果和最终助手消息。
        return {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "safe_calculate",
                            "args": {"expression": "3+5"},
                            "id": "call-1",
                            "type": "tool_call",
                        }
                    ],
                ),
                ToolMessage(content="8", tool_call_id="call-1"),
                AIMessage(content="结果是 8"),
            ]
        }


# 验证工具服务只暴露名称、参数和最终答案。
def test_tool_service_returns_safe_call_trace() -> None:
    # 创建注入替身 Agent 的工具服务。
    service = ToolService(
        model=object(),
        agent_factory=lambda **_values: FakeToolAgent(),
    )
    # 调用工具 Agent。
    result = service.chat("计算 3+5")
    # 验证最终助手答案。
    assert result.answer == "结果是 8"
    # 验证调用摘要不含工具返回正文。
    assert result.tool_calls[0].model_dump() == {
        "name": "safe_calculate",
        "arguments": {"expression": "3+5"},
    }


# 验证 Agent 构造失败映射为稳定上游异常。
def test_tool_service_maps_agent_construction_failure() -> None:
    # 定义会失败的 Agent 工厂。
    def broken_agent_factory(**_values):
        # 抛出内部兼容性错误。
        raise RuntimeError("internal-agent-error")

    # 验证构造失败被转换为稳定异常。
    with pytest.raises(UpstreamServiceError):
        # 尝试创建工具服务。
        ToolService(model=object(), agent_factory=broken_agent_factory)
