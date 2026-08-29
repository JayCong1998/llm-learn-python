"""LangChain 流式文本读取演示。"""

# 导入通用对象类型。
from typing import Any
# 导入迭代器类型。
from collections.abc import Iterator

# 导入 LangChain 回调处理器类型。
from langchain_core.callbacks import BaseCallbackHandler
# 导入 OpenAI 聊天模型封装。
from langchain_openai import ChatOpenAI

# 导入项目既有的模型配置读取函数。
from app import get_settings


# 定义创建已附加回调的聊天模型的函数。
def create_streaming_model(callbacks: list[BaseCallbackHandler]) -> ChatOpenAI:
    """使用项目配置创建支持流式输出的聊天模型。"""
    # 获取已经校验过的模型配置。
    settings = get_settings()
    # 返回应用模型配置和回调处理器的聊天模型。
    return ChatOpenAI(model=settings.model, api_key=settings.api_key, base_url=settings.base_url, callbacks=callbacks)


# 定义按顺序读取模型文本分块的函数。
def stream_text(model: Any, question: str) -> Iterator[str]:
    """产出模型流式响应中的非空文本内容。"""
    # 遍历模型返回的所有消息分块。
    for chunk in model.stream(question):
        # 取得当前分块的文本内容。
        content = getattr(chunk, "content", "")
        # 仅将非空字符串内容产出给调用方。
        if isinstance(content, str) and content:
            # 产出当前非空文本分块。
            yield content
