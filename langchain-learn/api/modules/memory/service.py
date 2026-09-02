"""基于 LangGraph checkpointer 的短期消息记忆服务。"""

# 导入通用对象和可调用类型。
from typing import Any, Callable

# 导入兼容 Agent 工厂。
from api.core.agents import create_agent_runtime
# 导入安全上游异常。
from api.core.errors import UpstreamServiceError


# 定义有线程级短期记忆的聊天服务。
class MemoryChatService:
    # 初始化模型、检查点存储和 Agent。
    def __init__(
        self,
        model: Any,
        checkpointer: Any,
        agent_factory: Callable[..., Any] = create_agent_runtime,
    ) -> None:
        # 保存检查点存储以支持清理。
        self.checkpointer = checkpointer
        # 尝试创建不带工具的有记忆 Agent。
        try:
            # 保存已经初始化的消息记忆 Agent。
            self.agent = agent_factory(
                model=model,
                tools=[],
                checkpointer=checkpointer,
                system_prompt="请结合当前会话历史回答用户问题。",
            )
        # 捕获 Agent 工厂初始化异常。
        except Exception as error:
            # 映射为不泄露内部细节的上游错误。
            raise UpstreamServiceError("消息记忆 Agent 初始化失败") from error

    # 在指定会话中发送一条增量消息。
    def chat(self, session_id: str, message: str) -> str:
        # 将 API 会话标识映射为 LangGraph 线程标识。
        config = {"configurable": {"thread_id": session_id}}
        # 尝试调用带检查点存储的 Agent。
        try:
            # 只提交当前新增的用户消息。
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
            )
            # 读取最后一条助手消息正文。
            answer = result["messages"][-1].content
        # 捕获模型或存储执行异常。
        except Exception as error:
            # 映射为不泄露内部详情的上游错误。
            raise UpstreamServiceError("消息记忆调用失败") from error
        # 返回字符串形式的助手回答。
        return str(answer)

    # 清除指定会话的全部检查点。
    def clear(self, session_id: str) -> None:
        # 尝试删除目标线程。
        try:
            # 只删除指定线程的检查点和写入。
            self.checkpointer.delete_thread(session_id)
        # 捕获存储清理异常。
        except Exception as error:
            # 映射为安全上游错误。
            raise UpstreamServiceError("消息记忆清理失败") from error
