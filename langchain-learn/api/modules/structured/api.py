"""联系人结构化提取 HTTP 路由。"""

# 导入 FastAPI 路由和依赖工具。
from fastapi import APIRouter, Depends
# 导入 Pydantic 数据模型和字段约束。
from pydantic import BaseModel, Field

# 导入结构化输出 service 依赖。
from api.core.dependencies import get_structured_service
# 导入统一成功响应。
from api.core.schemas import DataEnvelope
# 导入联系人类型和 service。
from api.modules.structured.service import (
    ContactInfo,
    StructuredOutputService,
)

# 创建结构化输出模块路由。
router = APIRouter(prefix="/api/v1/structured", tags=["structured-output"])


# 定义待提取的自然语言请求。
class ExtractRequest(BaseModel):
    # 限制输入文本不能为空且长度有界。
    text: str = Field(min_length=1, max_length=4000)


# 注册联系人结构化提取端点。
@router.post("/extract", response_model=DataEnvelope[ContactInfo])
def extract_contact(
    payload: ExtractRequest,
    service: StructuredOutputService = Depends(get_structured_service),
) -> DataEnvelope[ContactInfo]:
    # 调用结构化模型并包装统一响应。
    return DataEnvelope(data=service.extract(payload.text))
