"""异步读取 LangChain 模型文本分块。"""

# 导入异步迭代器类型。
from collections.abc import AsyncIterator
# 导入通用对象类型。
from typing import Any


# 定义模型流式文本服务。
class StreamingService:
    # 保存支持异步流式调用的模型。
    def __init__(self, model: Any) -> None:
        # 保存统一聊天模型。
        self.model = model

    # 异步产出非空模型文本。
    async def stream_tokens(self, question: str) -> AsyncIterator[str]:
        # 异步遍历模型消息分块。
        async for chunk in self.model.astream(question):
            # 读取当前分块正文。
            content = getattr(chunk, "content", "")
            # 仅处理非空字符串。
            if isinstance(content, str) and content:
                # 产出当前有效文本。
                yield content
