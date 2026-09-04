# 导入模块重载工具。
import importlib

# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient

# 导入健康检查模块。
import app.api.health as health_module
# 导入配置模块。
import app.core.config as config_module
# 导入应用入口模块。
import app.main as main_module
# 导入待实现的应用实例。
from app.main import app

# 创建应用测试客户端。
client = TestClient(app)


# 验证健康检查返回预期服务状态。
def test_health_returns_service_status():
    # 请求健康检查接口。
    response = client.get("/health")

    # 断言接口请求成功。
    assert response.status_code == 200
    # 断言接口返回约定的状态数据。
    assert response.json() == {"code": 0, "message": "success", "data": {"status": "ok", "service": "fastapi-scaffold"}}


# 验证环境变量配置会更新应用标题和服务名称。
def test_health_uses_configured_app_name(monkeypatch):
    # 开始执行临时配置的验证。
    try:
        # 设置测试用应用名称环境变量。
        monkeypatch.setenv("APP_NAME", "configured-name")
        # 重载配置模块以读取环境变量。
        importlib.reload(config_module)
        # 重载健康检查模块以使用新配置。
        importlib.reload(health_module)
        # 重载应用入口模块以使用新配置和路由。
        importlib.reload(main_module)
        # 为重载后的应用创建测试客户端。
        configured_client = TestClient(main_module.app)
        # 请求健康检查接口。
        response = configured_client.get("/health")

        # 断言应用标题使用环境变量配置。
        assert main_module.app.title == "configured-name"
        # 断言服务名称使用环境变量配置。
        assert response.json()["data"]["service"] == "configured-name"
    # 无论测试结果都恢复模块全局状态。
    finally:
        # 立即撤销环境变量补丁。
        monkeypatch.undo()
        # 重载配置模块以恢复默认配置。
        importlib.reload(config_module)
        # 重载健康检查模块以恢复默认配置。
        importlib.reload(health_module)
        # 重载应用入口模块以恢复默认配置和路由。
        importlib.reload(main_module)


# 验证配置测试后应用恢复默认服务名称。
def test_health_restores_default_service_status():
    # 为当前应用创建测试客户端。
    default_client = TestClient(main_module.app)
    # 请求健康检查接口。
    response = default_client.get("/health")

    # 断言应用标题恢复默认值。
    assert main_module.app.title == "fastapi-scaffold"
    # 断言服务名称恢复默认值。
    assert response.json()["data"]["service"] == "fastapi-scaffold"
