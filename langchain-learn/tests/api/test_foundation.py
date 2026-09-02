# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient

# 导入应用工厂。
from api.main import create_app
# 导入可覆盖的提示词 service 依赖。
from api.core.dependencies import get_prompt_service
# 导入稳定业务异常。
from api.core.errors import ConfigurationError, UpstreamServiceError


# 验证健康检查不依赖模型配置。
def test_health_endpoint_is_available_without_model() -> None:
    # 创建隔离的测试应用。
    application = create_app()
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用健康检查端点。
    response = client.get("/health")
    # 验证端点成功响应。
    assert response.status_code == 200
    # 验证稳定的健康检查结构。
    assert response.json() == {"data": {"status": "ok"}}


# 验证 OpenAPI 包含所有约定路由。
def test_openapi_contains_all_demo_routes() -> None:
    # 创建隔离的测试应用。
    application = create_app()
    # 读取应用生成的 OpenAPI 路径。
    paths = application.openapi()["paths"]
    # 定义设计中确认的路径集合。
    expected_paths = {
        "/health",
        "/api/v1/prompts/{template_type}/invoke",
        "/api/v1/stream/text",
        "/api/v1/stream/sse",
        "/api/v1/memory/chat",
        "/api/v1/memory/{session_id}",
        "/api/v1/structured/extract",
        "/api/v1/tools/chat",
        "/api/v1/mcp/chat",
        "/api/v1/skills",
        "/api/v1/skills/{skill_name}/invoke",
    }
    # 验证全部路径已注册。
    assert expected_paths <= set(paths)


# 验证配置异常映射为服务不可用。
def test_configuration_error_maps_to_safe_503_response() -> None:
    # 创建隔离应用。
    application = create_app()

    # 定义会抛出稳定配置异常的依赖。
    def raise_configuration_error():
        # 抛出不包含密钥的安全说明。
        raise ConfigurationError("缺少模型调用配置")

    # 覆盖提示词 service 依赖。
    application.dependency_overrides[get_prompt_service] = (
        raise_configuration_error
    )
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用依赖模型配置的端点。
    response = client.post(
        "/api/v1/prompts/text/invoke",
        json={"text": "Python"},
    )
    # 验证配置错误状态码。
    assert response.status_code == 503
    # 验证稳定错误结构。
    assert response.json() == {
        "error": {
            "code": "configuration_error",
            "message": "缺少模型调用配置",
        }
    }


# 验证上游异常映射为错误网关。
def test_upstream_error_maps_to_safe_502_response() -> None:
    # 创建隔离应用。
    application = create_app()

    # 定义会抛出安全上游异常的依赖。
    def raise_upstream_error():
        # 抛出不包含内部响应的稳定说明。
        raise UpstreamServiceError("模型调用失败")

    # 覆盖提示词 service 依赖。
    application.dependency_overrides[get_prompt_service] = raise_upstream_error
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用依赖上游模型的端点。
    response = client.post(
        "/api/v1/prompts/text/invoke",
        json={"text": "Python"},
    )
    # 验证上游错误状态码。
    assert response.status_code == 502
    # 验证稳定错误码。
    assert response.json()["error"]["code"] == "upstream_service_error"
