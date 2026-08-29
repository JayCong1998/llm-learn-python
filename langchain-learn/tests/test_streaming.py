# 导入流式终端回调处理器。
from streaming.callbacks import ConsoleStreamingCallback


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
