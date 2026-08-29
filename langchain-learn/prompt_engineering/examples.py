"""构建不同类型的 LangChain 提示词模板。"""

# 导入聊天提示词、少样本模板和消息占位符类。
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)


# 定义构建文本提示词模板的函数。
def build_text_prompt() -> PromptTemplate:
    """返回带有主题变量的文本提示词模板。"""
    # 根据模板文本创建提示词对象。
    return PromptTemplate.from_template("请用一句话解释 {topic}。")


# 定义构建聊天提示词模板的函数。
def build_chat_prompt() -> ChatPromptTemplate:
    """返回包含系统指令和用户问题的聊天提示词。"""
    # 根据消息角色和内容创建聊天提示词。
    return ChatPromptTemplate.from_messages(
        [
            ("system", "你是一名善于用通俗中文解释技术概念的助手。"),
            ("human", "请解释：{question}"),
        ]
    )


# 定义构建带聊天历史占位符模板的函数。
def build_history_prompt() -> ChatPromptTemplate:
    """返回可插入历史消息的聊天提示词。"""
    # 根据系统消息、历史占位符和当前问题创建模板。
    return ChatPromptTemplate.from_messages(
        [
            ("system", "你需要根据历史对话保持上下文一致。"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )


# 定义构建文本少样本提示词模板的函数。
def build_few_shot_prompt() -> FewShotPromptTemplate:
    """返回通过示例学习天气描述风格的文本提示词。"""
    # 定义用于演示的输入和输出样本。
    examples = [
        {"text": "晴天", "description": "阳光充足，适合户外活动。"},
        {"text": "大风", "description": "风力明显，外出请注意保暖和安全。"},
    ]
    # 定义单个样本的格式化模板。
    example_prompt = PromptTemplate.from_template(
        "输入：{text}\n描述：{description}"
    )
    # 将样本、样本模板和待处理输入组合为少样本提示词。
    return FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        suffix="输入：{text}\n描述：",
        input_variables=["text"],
    )


# 定义构建聊天少样本提示词模板的函数。
def build_few_shot_chat_prompt() -> ChatPromptTemplate:
    """返回在聊天消息中插入问答样本的提示词。"""
    # 定义用于演示的问答样本。
    examples = [
        {"question": "热", "answer": "请注意补水并避免长时间暴晒。"},
        {"question": "冷", "answer": "建议添加衣物并注意保暖。"},
    ]
    # 定义每组样本对应的用户和助手消息。
    example_prompt = ChatPromptTemplate.from_messages(
        [("human", "{question}"), ("ai", "{answer}")]
    )
    # 创建会把多组样本转换为聊天消息的少样本模板。
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
    )
    # 将系统指令、少样本消息和最终问题组合为聊天提示词。
    return ChatPromptTemplate.from_messages(
        [
            ("system", "请模仿示例，以简洁方式给出天气建议。"),
            few_shot_prompt,
            ("human", "{question}"),
        ]
    )
