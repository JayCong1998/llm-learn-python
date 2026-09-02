"""兼容当前与推荐 LangChain Agent 构造接口。"""

# 导入局部告警控制工具。
import warnings
# 导入通用对象类型。
from typing import Any


# 创建带相同调用表面的 LangChain Agent。
def create_agent_runtime(
    *,
    model: Any,
    tools: list[Any],
    checkpointer: Any = None,
    system_prompt: str | None = None,
) -> Any:
    # 优先尝试当前推荐的 LangChain Agent 工厂。
    try:
        # 延迟导入可选的 LangChain 主包。
        from langchain.agents import create_agent
    # 在离线开发环境缺少主包时使用已安装的 LangGraph 工厂。
    except ImportError:
        # 导入兼容的 LangGraph ReAct Agent 工厂。
        from langgraph.prebuilt import create_react_agent

        # 仅在兼容分支中抑制旧工厂自身的弃用提示。
        with warnings.catch_warnings():
            # 忽略已知的旧工厂弃用告警。
            warnings.simplefilter("ignore", DeprecationWarning)
            # 使用旧接口的 prompt 参数创建兼容 Agent。
            return create_react_agent(
                model=model,
                tools=tools,
                checkpointer=checkpointer,
                prompt=system_prompt,
            )
    # 使用推荐接口创建 Agent。
    return create_agent(
        model=model,
        tools=tools,
        checkpointer=checkpointer,
        system_prompt=system_prompt,
    )
