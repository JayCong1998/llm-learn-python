import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import ConfigurationError, build_graph, get_settings


def test_get_settings_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        get_settings()


def test_graph_contains_call_model_node(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    graph = build_graph()
    assert "call_model" in graph.get_graph().nodes
