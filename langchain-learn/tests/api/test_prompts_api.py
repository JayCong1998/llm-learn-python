# 导入简单命名空间构造替身结果。
from types import SimpleNamespace

# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient

# 导入提示词依赖函数。
from api.core.dependencies import get_prompt_service
# 导入应用工厂。
from api.main import create_app


# 定义可观察调用参数的提示词替身服务。
class FakePromptService:
    # 调用固定模板并返回演示结果。
    def invoke(self, template_type, text: str):
        # 保存收到的模板类型。
        self.template_type = template_type
        # 保存收到的统一文本。
        self.text = text
        # 返回与真实 service 相同字段的结果。
        return SimpleNamespace(
            template_type=template_type,
            rendered=f"请用一句话解释 {text}。",
            answer="模拟回答",
        )


# 验证提示词端点调用固定模板服务。
def test_prompt_endpoint_invokes_selected_template() -> None:
    # 创建隔离应用。
    application = create_app()
    # 创建替身提示词服务。
    service = FakePromptService()
    # 覆盖真实模型依赖。
    application.dependency_overrides[get_prompt_service] = lambda: service
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用文本提示词端点。
    response = client.post(
        "/api/v1/prompts/text/invoke",
        json={"text": "Python"},
    )
    # 验证端点成功响应。
    assert response.status_code == 200
    # 验证统一响应结构和教学字段。
    assert response.json() == {
        "data": {
            "template_type": "text",
            "rendered": "请用一句话解释 Python。",
            "answer": "模拟回答",
        }
    }
    # 验证请求文本传入 service。
    assert service.text == "Python"


# 验证未知模板类型由路径枚举拒绝。
def test_prompt_endpoint_rejects_unknown_template() -> None:
    # 创建测试客户端。
    client = TestClient(create_app())
    # 调用不存在的模板类型。
    response = client.post(
        "/api/v1/prompts/unknown/invoke",
        json={"text": "Python"},
    )
    # 验证请求校验状态码。
    assert response.status_code == 422


# 验证空文本在进入模型前被拒绝。
def test_prompt_endpoint_rejects_empty_text() -> None:
    # 创建测试客户端。
    client = TestClient(create_app())
    # 提交空白之外的空字符串。
    response = client.post(
        "/api/v1/prompts/text/invoke",
        json={"text": ""},
    )
    # 验证请求校验状态码。
    assert response.status_code == 422
