"""消息记忆聊天与清理路由。"""

# 导入 FastAPI 路由、依赖和路径校验工具。
from fastapi import APIRouter, Depends, Path
# 导入 Pydantic 数据模型和字段约束。
from pydantic import BaseModel, Field

# 导入记忆 service 依赖。
from api.core.dependencies import get_memory_service
# 导入统一成功响应。
from api.core.schemas import DataEnvelope
# 导入记忆服务类型。
from api.modules.memory.service import MemoryChatService

# 创建消息记忆模块路由。
router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


# 定义有会话标识的聊天请求。
class MemoryChatRequest(BaseModel):
    # 限制会话标识为安全短字符串。
    session_id: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
    )
    # 限制当前消息不能为空且长度有界。
    message: str = Field(min_length=1, max_length=4000)


# 定义记忆聊天响应。
class MemoryChatResult(BaseModel):
    # 返回当前会话标识。
    session_id: str
    # 返回结合历史生成的回答。
    answer: str


# 定义记忆清理响应。
class MemoryClearResult(BaseModel):
    # 返回被清理的会话标识。
    session_id: str
    # 标记清理操作已完成。
    cleared: bool


# 注册有短期记忆的聊天端点。
@router.post("/chat", response_model=DataEnvelope[MemoryChatResult])
def chat_with_memory(
    payload: MemoryChatRequest,
    service: MemoryChatService = Depends(get_memory_service),
) -> DataEnvelope[MemoryChatResult]:
    # 调用指定会话并包装统一响应。
    return DataEnvelope(
        data=MemoryChatResult(
            session_id=payload.session_id,
            answer=service.chat(payload.session_id, payload.message),
        )
    )


# 注册指定会话清理端点。
@router.delete(
    "/{session_id}",
    response_model=DataEnvelope[MemoryClearResult],
)
def clear_memory(
    session_id: str = Path(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
    service: MemoryChatService = Depends(get_memory_service),
) -> DataEnvelope[MemoryClearResult]:
    # 清除目标会话的检查点。
    service.clear(session_id)
    # 返回稳定的清理确认。
    return DataEnvelope(
        data=MemoryClearResult(session_id=session_id, cleared=True)
    )
