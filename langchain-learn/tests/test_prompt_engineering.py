# 导入提示词调用函数以验证 LCEL 链行为。
from prompt_engineering.app import invoke_prompt
# 导入各类提示词构造函数以验证模板格式化行为。
from prompt_engineering.examples import (
    build_chat_prompt,
    build_few_shot_chat_prompt,
    build_few_shot_prompt,
    build_history_prompt,
    build_selector_prompt,
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


# 定义用于模拟模型消息响应的数据对象。
class FakeResponse:
    # 定义模拟模型返回的消息内容。
    content = "模拟回复"


# 定义用于模拟 LCEL 调用链的对象。
class FakeChain:
    # 定义执行链调用并返回模拟响应的方法。
    def invoke(self, values):
        # 保存调用时传入的变量以便断言。
        self.values = values
        # 返回带内容字段的模拟响应。
        return FakeResponse()


# 定义用于模拟可组合提示词的对象。
class FakePrompt:
    # 定义与模型使用管道运算符组合的方法。
    def __or__(self, model):
        # 保存传入的模型以便断言。
        self.model = model
        # 返回可执行的模拟链。
        return FakeChain()


# 定义作为组合对象传入的模拟模型。
class FakeModel:
    """用于验证管道组合的空模型对象。"""


# 验证长度选择器生成的提示词包含示例内容。
def test_selector_prompt_formats_selected_examples():
    # 格式化使用长度选择器的少样本提示词。
    rendered = build_selector_prompt().format(text="阴天")
    # 确认选择后的提示词包含第一个示例。
    assert "输入：晴天" in rendered


# 验证调用函数将变量传给提示词和模型组成的链。
def test_invoke_prompt_passes_values_to_chain():
    # 创建可观察模型组合行为的提示词对象。
    prompt = FakePrompt()
    # 创建作为管道右侧对象的模拟模型。
    model = FakeModel()
    # 调用待验证的提示词链函数。
    result = invoke_prompt(prompt, model, {"topic": "Python"})
    # 确认函数返回模型消息内容。
    assert result == "模拟回复"
    # 确认提示词使用传入模型创建了管道链。
    assert prompt.model is model
