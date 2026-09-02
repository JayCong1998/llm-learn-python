"""多个 API 模块共享的请求与响应模型。"""

# 导入泛型类型变量。
from typing import Generic, TypeVar

# 导入 Pydantic 数据模型和字段约束。
from pydantic import BaseModel, Field

# 声明响应数据的泛型类型。
DataT = TypeVar("DataT")


# 定义统一成功响应外层结构。
class DataEnvelope(BaseModel, Generic[DataT]):
    # 保存端点返回的数据。
    data: DataT


# 定义通用自然语言问题请求。
class QuestionRequest(BaseModel):
    # 限制问题不能为空且避免无界输入。
    question: str = Field(min_length=1, max_length=4000)


# 定义一次工具调用摘要。
class ToolCallTrace(BaseModel):
    # 保存工具名称。
    name: str
    # 保存模型生成的结构化参数。
    arguments: dict[str, object]


# 定义 Agent 类端点的结果。
class AgentReply(BaseModel):
    # 保存最终自然语言答案。
    answer: str
    # 保存实际发生的工具调用摘要。
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)
