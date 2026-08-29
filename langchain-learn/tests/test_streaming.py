# 导入流式终端回调处理器。
from streaming.callbacks import ConsoleStreamingCallback
# 导入用于构造替身消息分块的简单命名空间。
from types import SimpleNamespace
# 导入项目的配置异常类型。
from app import ConfigurationError
# 导入待测的流式文本读取函数。
from streaming.app import stream_text
# 导入待测的流式命令行入口模块。
from streaming import main


# 验证回调处理器会输出完整的模型生命周期事件。
def test_console_callback_writes_lifecycle_events(capsys):
    # 创建待测的终端回调处理器。
    callback = ConsoleStreamingCallback()
    # 触发聊天模型开始事件。
    callback.on_chat_model_start({}, [[]])
    # 触发增量文本事件。
    callback.on_llm_new_token("你")
    # 触发聊天模型结束事件。
    callback.on_llm_end(None)
    # 触发聊天模型错误事件。
    callback.on_llm_error(RuntimeError("网络错误"))
    # 读取标准错误流中的回调信息。
    error_output = capsys.readouterr().err
    # 验证输出包含模型开始事件。
    assert "模型开始" in error_output
    # 验证输出包含增量文本事件。
    assert "'你'" in error_output
    # 验证输出包含模型结束事件。
    assert "模型结束" in error_output
    # 验证输出包含模型错误事件。
    assert "网络错误" in error_output


# 验证流式读取函数会按顺序产出非空文本分块。
def test_stream_text_yields_only_non_empty_content():
    # 定义返回固定消息分块的替身模型。
    class FakeModel:
        # 定义模拟 LangChain stream 接口的方法。
        def stream(self, question):
            # 返回包含空内容和有效内容的分块序列。
            return [SimpleNamespace(content="你"), SimpleNamespace(content=""), SimpleNamespace(content="好")]

    # 将替身模型的分块转换为文本列表。
    result = list(stream_text(FakeModel(), "问候"))
    # 验证空内容不会进入输出。
    assert result == ["你", "好"]


# 验证入口会将配置异常转换为失败退出码。
def test_main_returns_failure_for_configuration_error(monkeypatch, capsys):
    # 定义模拟配置异常的模型创建函数。
    def raise_configuration_error(callbacks):
        # 抛出预期的配置异常。
        raise ConfigurationError("OPENAI_API_KEY is missing")

    # 替换真实模型创建函数以避免读取本地配置。
    monkeypatch.setattr(main, "create_streaming_model", raise_configuration_error)
    # 执行命令行主函数。
    result = main.main()
    # 读取标准错误输出。
    error_output = capsys.readouterr().err
    # 验证入口返回失败状态。
    assert result == 1
    # 验证错误信息包含配置提示。
    assert "Configuration error" in error_output
