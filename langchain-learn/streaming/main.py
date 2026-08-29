"""LangChain 流式输出命令行入口。"""

# 导入标准错误流对象。
import sys

# 导入项目的配置异常类型。
from app import ConfigurationError
# 导入终端流式回调处理器。
from streaming.callbacks import ConsoleStreamingCallback
# 导入模型创建和文本流式读取函数。
from streaming.app import create_streaming_model, stream_text


# 定义流式演示的命令行主函数。
def main() -> int:
    """运行模型流式文本与回调事件演示。"""
    # 创建用于显示 LangChain 事件的回调处理器。
    callback = ConsoleStreamingCallback()
    # 尝试创建模型并读取模型文本分块。
    try:
        # 创建附加回调处理器的聊天模型。
        model = create_streaming_model([callback])
        # 向用户显示流式正文开始标记。
        print("模型正文：", flush=True)
        # 逐块输出模型生成的正文文本。
        for text in stream_text(model, "请用一句话解释 LangChain 的流式输出。"):
            # 立即输出当前文本分块而不换行。
            print(text, end="", flush=True)
        # 在正文输出完成后补充换行。
        print()
    # 单独处理缺少配置的预期错误。
    except ConfigurationError as error:
        # 向标准错误流输出配置错误信息。
        print(f"Configuration error: {error}", file=sys.stderr)
        # 返回非零状态码表示运行失败。
        return 1
    # 处理模型服务或网络等其他错误。
    except Exception as error:
        # 向标准错误流输出模型调用错误信息。
        print(f"Model request failed: {error}", file=sys.stderr)
        # 返回非零状态码表示运行失败。
        return 1
    # 返回零状态码表示运行成功。
    return 0


# 仅在直接作为模块执行时启动程序。
if __name__ == "__main__":
    # 使用主函数返回值作为进程退出码。
    raise SystemExit(main())
