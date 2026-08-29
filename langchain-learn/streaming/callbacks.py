"""终端流式回调演示。"""

# 导入标准错误流对象。
import sys

# 导入 LangChain 回调处理器基类。
from langchain_core.callbacks import BaseCallbackHandler


# 定义将流式生命周期事件写入终端的回调处理器。
class ConsoleStreamingCallback(BaseCallbackHandler):
    """将模型生命周期事件输出到标准错误流。"""

    # 定义聊天模型开始时的处理方法。
    def on_chat_model_start(self, serialized, messages, **kwargs):
        # 向标准错误流输出模型开始事件。
        print("[回调] 模型开始", file=sys.stderr, flush=True)

    # 定义收到增量文本时的处理方法。
    def on_llm_new_token(self, token, **kwargs):
        # 向标准错误流输出带引号的增量文本事件。
        print(f"[回调] token: {token!r}", file=sys.stderr, flush=True)

    # 定义模型结束时的处理方法。
    def on_llm_end(self, response, **kwargs):
        # 向标准错误流输出模型结束事件。
        print("[回调] 模型结束", file=sys.stderr, flush=True)

    # 定义模型调用失败时的处理方法。
    def on_llm_error(self, error, **kwargs):
        # 向标准错误流输出模型错误事件。
        print(f"[回调] 模型错误: {error}", file=sys.stderr, flush=True)
