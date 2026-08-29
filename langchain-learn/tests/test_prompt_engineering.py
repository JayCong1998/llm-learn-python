# 导入各类提示词构造函数以验证模板格式化行为。
from prompt_engineering.examples import (
    build_chat_prompt,
    build_few_shot_chat_prompt,
    build_few_shot_prompt,
    build_history_prompt,
    build_text_prompt,
)


# 验证文本提示词能够替换主题变量。
def test_build_text_prompt_formats_named_variables():
    # 创建待验证的文本提示词模板。
    prompt = build_text_prompt()
    # 确认格式化结果包含传入的主题。
    assert "Python" in prompt.format(topic="Python")


# 验证聊天模板包含系统消息和用户消息。
def test_chat_prompt_includes_system_and_human_messages():
    # 使用测试问题格式化聊天提示词。
    messages = build_chat_prompt().format_messages(question="什么是向量数据库？")
    # 确认消息角色顺序正确。
    assert [message.type for message in messages] == ["system", "human"]


# 验证聊天历史占位符能够接收消息列表。
def test_history_prompt_accepts_messages_placeholder():
    # 传入空历史并格式化聊天提示词。
    messages = build_history_prompt().format_messages(history=[], question="继续说明")
    # 确认最终用户消息使用传入的问题。
    assert messages[-1].content == "继续说明"


# 验证两类少样本模板均包含预设示例。
def test_few_shot_prompts_include_examples():
    # 格式化文本少样本提示词。
    text_prompt = build_few_shot_prompt().format(text="下雨")
    # 格式化聊天少样本提示词。
    chat_messages = build_few_shot_chat_prompt().format_messages(question="冷")
    # 确认文本模板包含预设示例。
    assert "输入：晴天" in text_prompt
    # 确认聊天模板包含系统消息、四条示例消息和最终问题。
    assert len(chat_messages) == 6
