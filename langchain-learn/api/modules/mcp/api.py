"""MCP Agent HTTP 路由。"""

# 导入 FastAPI 路由和依赖工具。
from fastapi import APIRouter, Depends

# 导入 MCP service 依赖。
from api.core.dependencies import get_mcp_service
# 导入通用 Agent 请求和响应。
from api.core.schemas import AgentReply, DataEnvelope, QuestionRequest
# 导入 MCP 服务类型。
from api.modules.mcp.service import McpService

# 创建 MCP 模块路由。
router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])


# 注册 MCP 工具 Agent 聊天端点。
@router.post("/chat", response_model=DataEnvelope[AgentReply])
async def chat_with_mcp(
    payload: QuestionRequest,
    service: McpService = Depends(get_mcp_service),
) -> DataEnvelope[AgentReply]:
    # 等待 MCP 工具发现和 Agent 调用。
    result = await service.chat(payload.question)
    # 包装统一成功响应。
    return DataEnvelope(data=result)
