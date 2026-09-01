# 导入时间测量工具。
from time import perf_counter
# 导入应用配置。
from app.core.config import settings
# 导入 SQLAlchemy 会话类型。
from sqlalchemy.orm import Session
# 导入当前用户模型。
from app.models.user import User
# 导入会话模型。
from app.models.chat_conversation import ChatConversation
# 导入消息模型。
from app.models.chat_message import ChatMessage
# 导入调用日志模型。
from app.models.llm_call_log import LlmCallLog
# 导入聊天仓储。
from app.repositories.chat_repository import ChatRepository
# 导入模型客户端。
from app.services.llm_client import LlmClient
# 导入未找到异常。
from app.services.exceptions import NotFoundError

# 编排聊天业务与事务。
class ChatService:
    # 初始化聊天服务。
    def __init__(self, database_session: Session) -> None:
        # 保存数据库会话。
        self.database_session = database_session
        # 创建聊天仓储。
        self.repository = ChatRepository(database_session)
        # 创建模型客户端。
        self.llm_client = LlmClient()
    # 创建用户会话。
    def create_conversation(self, user: User, title: str | None) -> ChatConversation:
        # 创建会话实体。
        conversation = ChatConversation(user_id=user.id, title=title)
        # 保存会话实体。
        self.repository.add(conversation)
        # 提交会话事务。
        self.database_session.commit()
        # 刷新生成字段。
        self.database_session.refresh(conversation)
        # 返回会话。
        return conversation
    # 获取用户会话列表。
    def list_conversations(self, user: User) -> list[ChatConversation]:
        # 返回当前用户会话。
        return self.repository.list_conversations(user.id)
    # 获取会话与历史消息。
    def get_conversation(self, user: User, conversation_id: int) -> ChatConversation:
        # 查询用户会话。
        conversation = self.repository.get_conversation(conversation_id, user.id)
        # 拒绝不存在会话。
        if conversation is None:
            # 抛出资源未找到异常。
            raise NotFoundError("会话不存在")
        # 返回会话。
        return conversation
    # 发送用户消息并生成回复。
    def send_message(self, user: User, conversation_id: int, content: str) -> ChatMessage:
        # 获取已授权会话。
        conversation = self.get_conversation(user, conversation_id)
        # 创建用户消息。
        user_message = ChatMessage(conversation_id=conversation.id, role="user", content=content)
        # 保存用户消息以供模型上下文使用。
        self.repository.add(user_message)
        # 刷新用户消息主键。
        self.database_session.flush()
        # 构造未删除历史上下文。
        prompt_messages = [{"role": message.role, "content": message.content} for message in self.repository.list_messages(conversation.id)]
        # 记录调用起始时间。
        started_at = perf_counter()
        # 调用大模型。
        answer, input_tokens, output_tokens = self.llm_client.chat(prompt_messages)
        # 计算调用耗时。
        latency_ms = int((perf_counter() - started_at) * 1000)
        # 创建助手消息。
        assistant_message = ChatMessage(conversation_id=conversation.id, role="assistant", content=answer)
        # 保存助手消息。
        self.repository.add(assistant_message)
        # 刷新助手消息主键。
        self.database_session.flush()
        # 创建调用日志。
        self.repository.add(LlmCallLog(message_id=assistant_message.id, provider="openai-compatible", model=settings.llm_model, status="succeeded", input_tokens=input_tokens, output_tokens=output_tokens, latency_ms=latency_ms))
        # 提交消息与日志事务。
        self.database_session.commit()
        # 刷新助手消息。
        self.database_session.refresh(assistant_message)
        # 返回助手消息。
        return assistant_message
    # 逻辑删除会话。
    def delete_conversation(self, user: User, conversation_id: int) -> None:
        # 获取已授权会话。
        conversation = self.get_conversation(user, conversation_id)
        # 标记会话已删除。
        conversation.deleted = True
        # 提交删除事务。
        self.database_session.commit()
