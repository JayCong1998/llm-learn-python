# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient

# 导入技能 service 依赖。
# 导入聊天模型和技能 service 依赖。
from api.core.dependencies import get_chat_model, get_skill_service
# 导入配置异常。
from api.core.errors import ConfigurationError
# 导入应用工厂。
from api.main import create_app
# 导入技能响应对象。
from api.modules.skills.service import (
    LocalSkill,
    SkillInvokeResult,
    SkillSummary,
)


# 定义本地技能 API 的替身服务。
class FakeSkillService:
    # 返回固定技能列表。
    def list_skills(self) -> list[SkillSummary]:
        # 返回不含本地路径的技能摘要。
        return [SkillSummary(name="code-explainer", description="解释代码")]

    # 返回固定技能调用结果。
    def invoke(self, name: str, user_input: str) -> SkillInvokeResult:
        # 返回技能名称、描述和模型回答。
        return SkillInvokeResult(
            name=name,
            description="解释代码",
            answer="这是代码解释",
        )


# 验证技能列表和调用端点。
def test_skill_list_and_invoke_endpoints() -> None:
    # 创建隔离应用。
    application = create_app()
    # 覆盖真实技能文件和模型依赖。
    application.dependency_overrides[get_skill_service] = FakeSkillService
    # 创建同步测试客户端。
    client = TestClient(application)
    # 获取技能列表。
    list_response = client.get("/api/v1/skills")
    # 验证列表不暴露文件路径。
    assert list_response.json() == {
        "data": [{"name": "code-explainer", "description": "解释代码"}]
    }
    # 调用代码解释技能。
    invoke_response = client.post(
        "/api/v1/skills/code-explainer/invoke",
        json={"input": "print('hello')"},
    )
    # 验证技能调用结果。
    assert invoke_response.json() == {
        "data": {
            "name": "code-explainer",
            "description": "解释代码",
            "answer": "这是代码解释",
        }
    }


# 验证本地技能枚举和名称校验不依赖模型密钥。
def test_local_skill_operations_precede_model_configuration() -> None:
    # 创建隔离应用。
    application = create_app()

    # 定义不可用的模型依赖。
    def unavailable_model():
        # 模拟缺少 API key 的环境。
        raise ConfigurationError("缺少模型调用配置")

    # 覆盖模型依赖以确保端点不会提前创建模型。
    application.dependency_overrides[get_chat_model] = unavailable_model
    # 创建同步测试客户端。
    client = TestClient(application)
    # 枚举纯本地技能文件。
    list_response = client.get("/api/v1/skills")
    # 验证列表端点不需要模型配置。
    assert list_response.status_code == 200
    # 调用非法技能名称。
    invalid_response = client.post(
        "/api/v1/skills/UPPER/invoke",
        json={"input": "内容"},
    )
    # 验证非法名称优先返回 422。
    assert invalid_response.status_code == 422
    # 调用不存在但格式合法的技能。
    missing_response = client.post(
        "/api/v1/skills/missing-skill/invoke",
        json={"input": "内容"},
    )
    # 验证未知技能优先返回 404。
    assert missing_response.status_code == 404
