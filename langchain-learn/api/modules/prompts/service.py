"""固定提示词模板的渲染和模型调用服务。"""

# 导入字符串枚举基类。
from enum import Enum
# 导入通用对象类型。
from typing import Any

# 导入 Pydantic 数据模型。
from pydantic import BaseModel

# 导入安全上游异常。
from api.core.errors import UpstreamServiceError
# 导入现有提示词构造函数。
from prompt_engineering.examples import (
    build_chat_prompt,
    build_few_shot_chat_prompt,
    build_few_shot_prompt,
    build_history_prompt,
    build_selector_prompt,
    build_text_prompt,
)


# 定义允许通过 API 选择的模板类型。
class PromptTemplateType(str, Enum):
    # 声明普通文本模板。
    TEXT = "text"
    # 声明聊天消息模板。
    CHAT = "chat"
    # 声明带历史占位符模板。
    HISTORY = "history"
    # 声明文本少样本模板。
    FEW_SHOT = "few-shot"
    # 声明聊天少样本模板。
    FEW_SHOT_CHAT = "few-shot-chat"
    # 声明长度选择少样本模板。
    SELECTOR = "selector"


# 定义提示词端点返回的数据。
class PromptResult(BaseModel):
    # 保存实际选择的模板类型。
    template_type: PromptTemplateType
    # 保存完成变量替换后的提示词。
    rendered: str
    # 保存模型生成的回答。
    answer: str


# 定义固定提示词模板调用服务。
class PromptService:
    # 初始化模型和模板白名单。
    def __init__(self, model: Any) -> None:
        # 保存可组合的聊天模型。
        self.model = model
        # 建立模板类型到构造函数的固定映射。
        self.prompt_builders = {
            PromptTemplateType.TEXT: build_text_prompt,
            PromptTemplateType.CHAT: build_chat_prompt,
            PromptTemplateType.HISTORY: build_history_prompt,
            PromptTemplateType.FEW_SHOT: build_few_shot_prompt,
            PromptTemplateType.FEW_SHOT_CHAT: build_few_shot_chat_prompt,
            PromptTemplateType.SELECTOR: build_selector_prompt,
        }

    # 使用统一文本调用指定提示词模板。
    def invoke(self, template_type: PromptTemplateType, text: str) -> PromptResult:
        # 从白名单创建提示词模板。
        prompt = self.prompt_builders[template_type]()
        # 将统一输入转换为模板所需变量。
        values = _values_for_template(template_type, text)
        # 尝试渲染并调用模型。
        try:
            # 渲染模板以便调用方观察最终提示词。
            rendered = prompt.format_prompt(**values).to_string()
            # 将提示词和模型组合成 LCEL 链。
            response = (prompt | self.model).invoke(values)
        # 捕获模型或模板执行异常。
        except Exception as error:
            # 转换为不泄露上游细节的稳定异常。
            raise UpstreamServiceError("提示词模型调用失败") from error
        # 返回教学展示结果。
        return PromptResult(
            template_type=template_type,
            rendered=rendered,
            answer=str(response.content),
        )


# 将统一文本转换为各模板的变量字典。
def _values_for_template(
    template_type: PromptTemplateType,
    text: str,
) -> dict[str, object]:
    # 为普通文本模板提供主题变量。
    if template_type is PromptTemplateType.TEXT:
        # 返回主题变量。
        return {"topic": text}
    # 为聊天和聊天少样本模板提供问题变量。
    if template_type in {
        PromptTemplateType.CHAT,
        PromptTemplateType.FEW_SHOT_CHAT,
    }:
        # 返回问题变量。
        return {"question": text}
    # 为历史模板提供空历史和当前问题。
    if template_type is PromptTemplateType.HISTORY:
        # 返回历史占位符和问题变量。
        return {"history": [], "question": text}
    # 为文本少样本模板提供文本变量。
    return {"text": text}
