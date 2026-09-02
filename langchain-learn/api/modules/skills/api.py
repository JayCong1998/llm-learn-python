"""本地技能列表与调用 HTTP 路由。"""

# 导入 FastAPI 路由和依赖工具。
from fastapi import APIRouter, Depends
# 导入 Pydantic 数据模型和字段约束。
from pydantic import BaseModel, Field

# 导入本地技能 service 依赖。
from api.core.dependencies import get_skill_service
# 导入统一成功响应。
from api.core.schemas import DataEnvelope
# 导入技能响应和 service 类型。
from api.modules.skills.service import (
    SkillInvokeResult,
    SkillService,
    SkillSummary,
)

# 创建本地技能模块路由。
router = APIRouter(prefix="/api/v1/skills", tags=["skills"])


# 定义技能调用用户输入。
class SkillInvokeRequest(BaseModel):
    # 限制用户输入不能为空且长度有界。
    input: str = Field(min_length=1, max_length=8000)


# 注册本地技能列表端点。
@router.get("", response_model=DataEnvelope[list[SkillSummary]])
def list_local_skills(
    service: SkillService = Depends(get_skill_service),
) -> DataEnvelope[list[SkillSummary]]:
    # 返回不含文件路径和完整指令的摘要列表。
    return DataEnvelope(data=service.list_skills())


# 注册指定本地技能调用端点。
@router.post(
    "/{skill_name}/invoke",
    response_model=DataEnvelope[SkillInvokeResult],
)
def invoke_local_skill(
    skill_name: str,
    payload: SkillInvokeRequest,
    service: SkillService = Depends(get_skill_service),
) -> DataEnvelope[SkillInvokeResult]:
    # 加载白名单技能并调用模型。
    result = service.invoke(skill_name, payload.input)
    # 包装统一成功响应。
    return DataEnvelope(data=result)
