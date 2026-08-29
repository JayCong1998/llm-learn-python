# 导入按文件路径加载模块的工具。
import importlib.util
# 导入模块缓存字典。
import sys
# 导入构造应用文件路径的路径工具。
from pathlib import Path

# 导入测试框架。
import pytest

# 定位 LangChain 项目的应用模块文件。
APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
# 为应用模块创建独立的导入规范。
SPEC = importlib.util.spec_from_file_location("langchain_learn_app", APP_PATH)
# 确认导入规范及加载器均已成功创建。
assert SPEC and SPEC.loader
# 根据导入规范创建模块对象。
APP = importlib.util.module_from_spec(SPEC)
# 将模块以唯一名称放入缓存，避免和另一个项目冲突。
sys.modules[SPEC.name] = APP
# 执行模块加载器以加载应用代码。
SPEC.loader.exec_module(APP)

# 取得待测的配置异常类型。
ConfigurationError = APP.ConfigurationError
# 取得待测的配置读取函数。
get_settings = APP.get_settings


# 验证未设置 API 密钥时会抛出配置异常。
def test_get_settings_requires_api_key(monkeypatch):
    # 清除可能继承的 API 密钥环境变量。
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # 断言配置读取会报告缺少密钥。
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        # 触发配置读取逻辑。
        get_settings()


# 验证未指定模型时会使用默认模型。
def test_get_settings_uses_default_model(monkeypatch):
    # 提供测试专用的 API 密钥。
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    # 清除模型名称以测试默认值。
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    # 读取当前测试环境中的设置。
    settings = get_settings()
    # 验证默认模型名称正确。
    assert settings.model == "gpt-4.1-mini"
