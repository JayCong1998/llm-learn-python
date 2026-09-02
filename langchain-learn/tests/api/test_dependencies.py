# 导入测试框架。
import pytest

# 导入依赖模块以替换模型构造器。
from api.core import dependencies
# 导入稳定配置异常。
from api.core.errors import ConfigurationError


# 验证模型适配器构造失败映射为不泄露配置的稳定异常。
def test_chat_model_construction_failure_maps_to_configuration_error(
    monkeypatch,
) -> None:
    # 创建最小模型配置替身。
    class FakeSettings:
        # 提供模型名称。
        model = "demo-model"
        # 提供测试密钥。
        api_key = "test-key"
        # 提供会导致底层失败的地址文本。
        base_url = "sensitive-invalid-url"

    # 定义会回显底层地址的失败模型构造器。
    def broken_model_factory(**_values):
        # 抛出包含敏感配置的底层异常。
        raise RuntimeError("sensitive-invalid-url")

    # 替换设置读取函数。
    monkeypatch.setattr(dependencies, "get_settings", lambda: FakeSettings())
    # 替换真实模型适配器。
    monkeypatch.setattr(dependencies, "ChatOpenAI", broken_model_factory)
    # 捕获稳定配置异常。
    with pytest.raises(ConfigurationError) as captured:
        # 尝试创建统一聊天模型。
        dependencies.get_chat_model()
    # 验证对外消息没有回显原始地址。
    assert "sensitive-invalid-url" not in str(captured.value)
