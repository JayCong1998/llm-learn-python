"""安全本地工具调用 HTTP 路由。"""

# 导入 FastAPI 路由和依赖工具。
from fastapi import APIRouter, Depends

# 导入工具 service 依赖。
from api.core.dependencies import get_tool_service
# 导入通用 Agent 请求与响应。
from api.core.schemas import AgentReply, DataEnvelope, QuestionRequest
# 导入工具服务类型。
from api.modules.tools.service import ToolService

# 创建本地工具模块路由。
router = APIRouter(prefix="/api/v1/tools", tags=["tools"])


# 注册安全工具 Agent 聊天端点。
@router.post("/chat", response_model=DataEnvelope[AgentReply])
def chat_with_tools(
    payload: QuestionRequest,
    service: ToolService = Depends(get_tool_service),
) -> DataEnvelope[AgentReply]:
    # 调用工具 Agent 并包装统一响应。
    return DataEnvelope(data=service.chat(payload.question))
