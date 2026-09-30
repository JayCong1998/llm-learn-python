from fastapi import APIRouter
from fastapi import Body
from agents.react_agent import call

# 创建聊天 API 路由。
router = APIRouter()

@router.post("/agent/chat")
# 从请求体读取用户消息并调用 LangChain 模型。
async def chat(request: str= Body(...)) -> str:
    return call(request)
