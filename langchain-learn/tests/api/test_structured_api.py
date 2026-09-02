# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient

# 导入结构化输出 service 依赖。
from api.core.dependencies import get_structured_service
# 导入应用工厂。
from api.main import create_app
# 导入联系人结果类型。
from api.modules.structured.service import ContactInfo
# 导入结构化 service 和稳定上游异常。
from api.modules.structured.service import StructuredOutputService
# 导入稳定上游异常。
from api.core.errors import UpstreamServiceError
# 导入测试框架。
import pytest


# 定义结构化提取替身服务。
class FakeStructuredService:
    # 返回固定联系人对象。
    def extract(self, text: str) -> ContactInfo:
        # 保存原始输入文本。
        self.text = text
        # 返回经过 Pydantic 校验的联系人。
        return ContactInfo(
            name="张三",
            email="zhangsan@example.com",
            phone="13800138000",
            notes=None,
        )


# 验证自然语言被提取为联系人 JSON。
def test_structured_endpoint_returns_validated_contact() -> None:
    # 创建隔离应用。
    application = create_app()
    # 创建替身结构化服务。
    service = FakeStructuredService()
    # 覆盖真实模型依赖。
    application.dependency_overrides[get_structured_service] = lambda: service
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用联系人提取端点。
    response = client.post(
        "/api/v1/structured/extract",
        json={"text": "张三的邮箱是 zhangsan@example.com"},
    )
    # 验证成功状态码。
    assert response.status_code == 200
    # 验证完整结构化结果。
    assert response.json() == {
        "data": {
            "name": "张三",
            "email": "zhangsan@example.com",
            "phone": "13800138000",
            "notes": None,
        }
    }


# 验证结构化模型绑定失败映射为稳定上游异常。
def test_structured_service_maps_adapter_construction_failure() -> None:
    # 定义绑定结构化输出时失败的模型。
    class BrokenModel:
        # 模拟不兼容的结构化输出适配器。
        def with_structured_output(self, _schema):
            # 抛出内部兼容性错误。
            raise RuntimeError("internal-adapter-error")

    # 验证构造失败不会直接暴露为未处理异常。
    with pytest.raises(UpstreamServiceError):
        # 尝试创建结构化输出服务。
        StructuredOutputService(BrokenModel())
