# 导入枚举基类以定义稳定的事件类型。
from enum import StrEnum
# 导入任意负载类型以描述事件内容。
from typing import Any
# 导入 Pydantic 模型以校验和序列化事件。
from pydantic import BaseModel, ConfigDict, Field


# 定义 Agent 流式输出的事件类别。
class AgentStreamEventType(StrEnum):
    # 表示一次 Agent 执行开始。
    RUN_STARTED = "run_started"
    # 表示模型开始进行思考或推理。
    THINKING = "thinking"
    # 表示模型产生了思考内容片段。
    THINKING_DELTA = "thinking_delta"
    # 表示模型准备发起工具调用。
    TOOL_CALL_STARTED = "tool_call_started"
    # 表示工具调用参数正在流式生成。
    TOOL_CALL_DELTA = "tool_call_delta"
    # 表示工具调用已完成。
    TOOL_CALL_COMPLETED = "tool_call_completed"
    # 表示工具调用执行失败。
    TOOL_CALL_FAILED = "tool_call_failed"
    # 表示工具返回了执行结果。
    TOOL_RESULT = "tool_result"
    # 表示模型开始输出面向用户的内容。
    CONTENT = "content"
    # 表示面向用户的内容增量片段。
    CONTENT_DELTA = "content_delta"
    # 表示 Agent 已完成本次执行。
    RUN_COMPLETED = "run_completed"
    # 表示 Agent 执行过程中发生错误。
    ERROR = "error"


# 定义统一的 Agent 流式输出事件结构。
class AgentStreamEvent(BaseModel):
    # 允许下游附加协议字段而不影响基础事件解析。
    model_config = ConfigDict(extra="allow")

    # 保存事件类别以便消费者按类型分发处理。
    type: AgentStreamEventType
    # 保存事件携带的文本、结果或其他数据。
    data: Any = None
    # 保存对应的工具名称。
    tool_name: str | None = None
    # 保存一次工具调用的唯一标识。
    tool_call_id: str | None = None
    # 保存本次 Agent 执行的标识。
    run_id: str | None = None
    # 保存关联的对话轮次或步骤序号。
    step: int | None = None
    # 保存扩展元数据。
    metadata: dict[str, Any] = Field(default_factory=dict)
