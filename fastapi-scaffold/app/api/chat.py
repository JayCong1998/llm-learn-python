# 导入 FastAPI 路由类。
from fastapi import APIRouter
# 导入依赖注入工具。
from fastapi import Depends
# 导入 HTTP 异常类型。
from fastapi import HTTPException
# 导入 HTTP 状态码常量。
from fastapi import status
# 导入当前用户依赖。
from app.core.dependencies import get_current_user
# 导入数据库会话注解。
from app.core.dependencies import DatabaseSession
# 导入用户模型。
from app.models.user import User
# 导入聊天请求响应模型。
from app.schemas.chat import ConversationCreate, ConversationDetail, ConversationRead, MessageCreate, MessageRead
# 导入聊天服务。
from app.services.chat_service import ChatService
# 导入未找到异常。
from app.services.exceptions import NotFoundError

# 创建聊天路由。
router = APIRouter(prefix="/chat", tags=["chat"])

# 创建对话会话。
@router.post("/conversations", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
# 定义创建会话接口。
def create_conversation(payload: ConversationCreate, database_session: DatabaseSession, current_user: User = Depends(get_current_user)) -> ConversationRead:
    # 返回新建会话。
    return ChatService(database_session).create_conversation(current_user, payload.title)

# 查询当前用户会话列表。
@router.get("/conversations", response_model=list[ConversationRead])
# 定义会话列表接口。
def list_conversations(database_session: DatabaseSession, current_user: User = Depends(get_current_user)) -> list[ConversationRead]:
    # 返回当前用户会话。
    return ChatService(database_session).list_conversations(current_user)

# 查询会话详情。
@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
# 定义会话详情接口。
def get_conversation(conversation_id: int, database_session: DatabaseSession, current_user: User = Depends(get_current_user)) -> ConversationDetail:
    # 创建聊天服务。
    service = ChatService(database_session)
    # 尝试读取会话。
    try:
        # 获取会话实体。
        conversation = service.get_conversation(current_user, conversation_id)
    # 转换未找到异常。
    except NotFoundError as error:
        # 返回未找到响应。
        raise HTTPException(status_code=404, detail=str(error)) from error
    # 返回会话及历史消息。
    return ConversationDetail(id=conversation.id, title=conversation.title, messages=service.repository.list_messages(conversation.id))

# 发送会话消息。
@router.post("/conversations/{conversation_id}/messages", response_model=MessageRead)
# 定义发送消息接口。
def send_message(conversation_id: int, payload: MessageCreate, database_session: DatabaseSession, current_user: User = Depends(get_current_user)) -> MessageRead:
    # 尝试发送消息。
    try:
        # 返回模型生成的助手消息。
        return ChatService(database_session).send_message(current_user, conversation_id, payload.content)
    # 转换未找到异常。
    except NotFoundError as error:
        # 返回未找到响应。
        raise HTTPException(status_code=404, detail=str(error)) from error

# 逻辑删除会话。
@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
# 定义删除会话接口。
def delete_conversation(conversation_id: int, database_session: DatabaseSession, current_user: User = Depends(get_current_user)) -> None:
    # 尝试删除会话。
    try:
        # 执行逻辑删除。
        ChatService(database_session).delete_conversation(current_user, conversation_id)
    # 转换未找到异常。
    except NotFoundError as error:
        # 返回未找到响应。
        raise HTTPException(status_code=404, detail=str(error)) from error
