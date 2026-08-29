import importlib.util
import sys
from pathlib import Path

import pytest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
SPEC = importlib.util.spec_from_file_location("langgraph_learn_app", APP_PATH)
assert SPEC and SPEC.loader
APP = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = APP
SPEC.loader.exec_module(APP)

ConfigurationError = APP.ConfigurationError
build_graph = APP.build_graph
get_settings = APP.get_settings


def test_get_settings_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        get_settings()


def test_graph_contains_call_model_node(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    graph = build_graph()
    assert "call_model" in graph.get_graph().nodes
