# 导入文本提示词构造函数以验证命名变量格式化行为。
from prompt_engineering.examples import build_text_prompt


# 验证文本提示词能够替换主题变量。
def test_build_text_prompt_formats_named_variables():
    # 创建待验证的文本提示词模板。
    prompt = build_text_prompt()
    # 确认格式化结果包含传入的主题。
    assert "Python" in prompt.format(topic="Python")
