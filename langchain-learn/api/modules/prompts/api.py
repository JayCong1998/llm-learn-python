"""提示词模板 HTTP 路由。"""

# 导入 FastAPI 路由和依赖工具。
from fastapi import APIRouter, Depends
# 导入 Pydantic 数据模型和字段约束。
from pydantic import BaseModel, Field

# 导入提示词 service 依赖。
from api.core.dependencies import get_prompt_service
# 导入统一成功响应。
from api.core.schemas import DataEnvelope
# 导入提示词类型和结果模型。
from api.modules.prompts.service import (
    PromptResult,
    PromptService,
    PromptTemplateType,
)

# 创建提示词模块路由。
router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])


# 定义提示词统一输入。
class PromptRequest(BaseModel):
    # 限制模板输入不能为空且长度有界。
    text: str = Field(min_length=1, max_length=4000)


# 注册固定模板调用端点。
@router.post(
    "/{template_type}/invoke",
    response_model=DataEnvelope[PromptResult],
)
def invoke_prompt_template(
    template_type: PromptTemplateType,
    payload: PromptRequest,
    service: PromptService = Depends(get_prompt_service),
) -> DataEnvelope[PromptResult]:
    # 调用所选模板并包装统一响应。
    return DataEnvelope(data=service.invoke(template_type, payload.text))
