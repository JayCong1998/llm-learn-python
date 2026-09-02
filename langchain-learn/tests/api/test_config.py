# 导入测试框架。
import pytest

# 导入 API 配置和异常类型。
from api.core.config import ApiSettings, McpMode, MemoryBackend
# 导入配置异常。
from api.core.errors import ConfigurationError


# 验证 API 配置提供教学环境的安全默认值。
def test_api_settings_use_demo_defaults(monkeypatch) -> None:
    # 清除可能继承的记忆后端设置。
    monkeypatch.delenv("MEMORY_BACKEND", raising=False)
    # 清除可能继承的 MCP 模式设置。
    monkeypatch.delenv("MCP_MODE", raising=False)
    # 清除可能继承的远程请求头设置。
    monkeypatch.delenv("MCP_REMOTE_HEADERS", raising=False)
    # 从当前测试环境读取配置。
    settings = ApiSettings.from_environment()
    # 验证默认使用进程内记忆。
    assert settings.memory_backend is MemoryBackend.MEMORY
    # 验证默认使用内置本地 MCP。
    assert settings.mcp_mode is McpMode.LOCAL
    # 验证默认请求头为空。
    assert settings.mcp_remote_headers == {}


# 验证无效请求头不会泄露具体值。
def test_api_settings_reject_invalid_headers_without_leaking_value(monkeypatch) -> None:
    # 设置包含敏感文本的非法 JSON。
    monkeypatch.setenv("MCP_REMOTE_HEADERS", "secret-token")
    # 捕获安全的配置异常。
    with pytest.raises(ConfigurationError) as captured:
        # 触发请求头解析。
        ApiSettings.from_environment()
    # 验证异常没有回显敏感文本。
    assert "secret-token" not in str(captured.value)
