# 导入 FastAPI 路由与错误响应工具。
from fastapi import APIRouter, HTTPException
# 导入 LangChain 的用户消息类型。
from langchain_core.messages import HumanMessage
# 导入 Qwen 的 LangChain 聊天模型封装。
from langchain_openai import ChatOpenAI
# 导入请求与响应的数据校验模型。
from pydantic import BaseModel, Field

# 读取模型连接配置。
from core.config import settings
# 导入统一响应模型与构造方法。
from core.response import ApiResponse, success_response

# 创建聊天 API 路由。
router = APIRouter()


# 定义对话接口的请求结构。
class ChatRequest(BaseModel):
    # 接收用户提交的消息文本。
    message: str = Field(min_length=1, max_length=4000)


# 定义对话接口的响应结构。
class ChatResponse(BaseModel):
    # 返回模型生成的回复文本。
    reply: str


# 提供基于 Qwen 的单轮对话接口。
@router.post("/chat", response_model=ApiResponse[ChatResponse], tags=["chat"])
# 从请求体读取用户消息并调用 LangChain 模型。
async def chat(request: ChatRequest) -> ApiResponse[ChatResponse]:
    # 在未配置密钥时返回清楚的客户端错误。
    if not settings.dashscope_api_key:
        # 由全局异常处理器映射模型服务错误码并生成统一响应体。
        raise HTTPException(status_code=503, detail="请先在 .env 中配置 DASHSCOPE_API_KEY")
    # 使用项目配置创建 Qwen 聊天模型。
    model = ChatOpenAI(
        model=settings.qwen_model,
        api_key=settings.dashscope_api_key,
        base_url=settings.qwen_base_url
    )
    # 异步调用模型以避免阻塞 FastAPI 事件循环。
    result = await model.ainvoke([HumanMessage(content=request.message)])
    # 将模型文本回复封装成 API 响应。
    return success_response(ChatResponse(reply=str(result.content)))
