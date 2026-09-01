# 导入 SQLAlchemy 查询构造工具。
from sqlalchemy import select
# 导入 SQLAlchemy 会话类型。
from sqlalchemy.orm import Session
# 导入会话模型。
from app.models.chat_conversation import ChatConversation
# 导入消息模型。
from app.models.chat_message import ChatMessage
# 导入调用日志模型。
from app.models.llm_call_log import LlmCallLog

# 封装聊天持久化访问。
class ChatRepository:
    # 保存数据库会话。
    def __init__(self, database_session: Session) -> None:
        # 保存当前会话。
        self.database_session = database_session
    # 添加任意聊天实体。
    def add(self, entity: ChatConversation | ChatMessage | LlmCallLog) -> None:
        # 将实体加入当前事务。
        self.database_session.add(entity)
    # 查询用户会话。
    def list_conversations(self, user_id: int) -> list[ChatConversation]:
        # 返回未删除会话。
        return list(self.database_session.scalars(select(ChatConversation).where(ChatConversation.user_id == user_id, ChatConversation.deleted.is_(False))))
    # 查询用户拥有的会话。
    def get_conversation(self, conversation_id: int, user_id: int) -> ChatConversation | None:
        # 返回未删除的匹配会话。
        return self.database_session.scalar(select(ChatConversation).where(ChatConversation.id == conversation_id, ChatConversation.user_id == user_id, ChatConversation.deleted.is_(False)))
    # 查询会话消息。
    def list_messages(self, conversation_id: int) -> list[ChatMessage]:
        # 返回未删除消息。
        return list(self.database_session.scalars(select(ChatMessage).where(ChatMessage.conversation_id == conversation_id, ChatMessage.deleted.is_(False)).order_by(ChatMessage.id)))
