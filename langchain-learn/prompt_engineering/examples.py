"""构建不同类型的 LangChain 提示词模板。"""

# 导入文本提示词模板类。
from langchain_core.prompts import PromptTemplate


# 定义构建文本提示词模板的函数。
def build_text_prompt() -> PromptTemplate:
    """返回带有主题变量的文本提示词模板。"""
    # 根据模板文本创建提示词对象。
    return PromptTemplate.from_template("请用一句话解释 {topic}。")
