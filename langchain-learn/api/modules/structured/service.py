"""使用 Pydantic Schema 约束模型结构化输出。"""

# 导入通用对象类型。
from typing import Any

# 导入 Pydantic 数据模型和字段说明。
from pydantic import BaseModel, Field

# 导入安全上游异常。
from api.core.errors import UpstreamServiceError


# 定义联系人结构化结果。
class ContactInfo(BaseModel):
    # 保存联系人姓名。
    name: str = Field(description="联系人姓名")
    # 保存可选电子邮箱。
    email: str | None = Field(default=None, description="电子邮箱")
    # 保存可选电话号码。
    phone: str | None = Field(default=None, description="电话号码")
    # 保存其他未归类信息。
    notes: str | None = Field(default=None, description="其他备注")


# 定义结构化联系人提取服务。
class StructuredOutputService:
    # 初始化带联系人 Schema 的模型。
    def __init__(self, model: Any) -> None:
        # 尝试绑定 LangChain 结构化输出适配器。
        try:
            # 保存绑定联系人 Schema 后的模型。
            self.structured_model = model.with_structured_output(ContactInfo)
        # 捕获模型适配器初始化异常。
        except Exception as error:
            # 映射为不泄露内部细节的上游错误。
            raise UpstreamServiceError("结构化输出模型初始化失败") from error

    # 从自然语言提取联系人字段。
    def extract(self, text: str) -> ContactInfo:
        # 尝试调用结构化模型。
        try:
            # 请求模型返回联系人对象。
            result = self.structured_model.invoke(text)
        # 捕获模型调用或 Schema 校验异常。
        except Exception as error:
            # 映射为安全上游错误。
            raise UpstreamServiceError("联系人结构化提取失败") from error
        # 确认模型适配器返回目标类型。
        if not isinstance(result, ContactInfo):
            # 拒绝无法验证的返回对象。
            raise UpstreamServiceError("模型未返回有效联系人结构")
        # 返回已经过 Pydantic 校验的联系人。
        return result
