# LangChain 流式输出示例包 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增同时展示实时文本和 LangChain 回调事件的终端演示包。

**Architecture:** 回调处理器将生命周期事件写入标准错误流，流式读取函数将模型的非空文本分块产出给入口，入口将正文立即写入标准输出。模型配置复用顶层 `app.py` 的环境变量读取逻辑。

**Tech Stack:** Python、LangChain OpenAI、pytest。

---

## File structure

- Create: `langchain-learn/streaming/__init__.py` — 导出流式读取接口。
- Create: `langchain-learn/streaming/callbacks.py` — 终端回调处理器。
- Create: `langchain-learn/streaming/app.py` — 模型创建和文本分块过滤。
- Create: `langchain-learn/streaming/main.py` — 可运行入口。
- Create: `langchain-learn/tests/test_streaming.py` — 不联网单元测试。
- Modify: `langchain-learn/README.md` — 运行说明。

### Task 1: 回调处理器

**Files:**
- Create: `langchain-learn/streaming/callbacks.py`
- Test: `langchain-learn/tests/test_streaming.py`

- [ ] **Step 1: 先写失败的生命周期输出测试**

```python
def test_console_callback_writes_lifecycle_events(capsys):
    callback = ConsoleStreamingCallback()
    callback.on_chat_model_start({}, [[]])
    callback.on_llm_new_token("你")
    callback.on_llm_end(None)
    callback.on_llm_error(RuntimeError("网络错误"))
    assert "模型开始" in capsys.readouterr().err
```

- [ ] **Step 2: 确认测试因模块缺失而失败**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_streaming.py::test_console_callback_writes_lifecycle_events -v`

Expected: FAIL，提示 `streaming.callbacks` 不存在。

- [ ] **Step 3: 实现最小回调类**

使用 `BaseCallbackHandler` 定义 `ConsoleStreamingCallback`，实现 `on_chat_model_start`、`on_llm_new_token`、`on_llm_end` 和 `on_llm_error`。四个方法均用 `print(..., file=sys.stderr, flush=True)` 输出带 `[回调]` 前缀的中文事件；每个 Python 有效代码行前添加中文独立行注释。

- [ ] **Step 4: 确认测试通过后提交**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_streaming.py::test_console_callback_writes_lifecycle_events -v`

Expected: PASS。

Commit: `git add -- langchain-learn/streaming/callbacks.py langchain-learn/tests/test_streaming.py; git commit -m "feat: add LangChain streaming callback demo"`

### Task 2: 流式文本读取

**Files:**
- Create: `langchain-learn/streaming/__init__.py`
- Create: `langchain-learn/streaming/app.py`
- Modify: `langchain-learn/tests/test_streaming.py`

- [ ] **Step 1: 先写失败的分块过滤测试**

```python
def test_stream_text_yields_only_non_empty_content():
    class FakeModel:
        def stream(self, question):
            return [SimpleNamespace(content="你"), SimpleNamespace(content=""), SimpleNamespace(content="好")]
    assert list(stream_text(FakeModel(), "问候")) == ["你", "好"]
```

- [ ] **Step 2: 确认测试因函数缺失而失败**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_streaming.py::test_stream_text_yields_only_non_empty_content -v`

Expected: FAIL，提示 `stream_text` 不存在。

- [ ] **Step 3: 实现模型和文本迭代器**

在 `app.py` 中从顶层 `app.py` 导入 `get_settings`，定义 `create_streaming_model(callbacks)` 并将设置和回调传给 `ChatOpenAI`。定义 `stream_text(model, question)`，遍历 `model.stream(question)`，仅 `yield` 非空字符串 `chunk.content`。在 `__init__.py` 导出 `stream_text`。所有 Python 有效代码行均添加前置中文注释。

- [ ] **Step 4: 确认测试通过后提交**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_streaming.py::test_stream_text_yields_only_non_empty_content -v`

Expected: PASS。

Commit: `git add -- langchain-learn/streaming/__init__.py langchain-learn/streaming/app.py langchain-learn/tests/test_streaming.py; git commit -m "feat: add streamed text iterator"`

### Task 3: 命令行入口与文档

**Files:**
- Create: `langchain-learn/streaming/main.py`
- Modify: `langchain-learn/tests/test_streaming.py`
- Modify: `langchain-learn/README.md`

- [ ] **Step 1: 先写失败的配置错误入口测试**

```python
def test_main_returns_failure_for_configuration_error(monkeypatch, capsys):
    monkeypatch.setattr(main, "create_streaming_model", raise_configuration_error)
    assert main.main() == 1
    assert "Configuration error" in capsys.readouterr().err
```

- [ ] **Step 2: 确认测试因入口模块缺失而失败**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_streaming.py::test_main_returns_failure_for_configuration_error -v`

Expected: FAIL，提示 `streaming.main` 不存在。

- [ ] **Step 3: 实现入口并更新说明**

入口创建 `ConsoleStreamingCallback`、调用 `create_streaming_model([callback])` 和 `stream_text()`，逐块 `print(text, end="", flush=True)`；单独处理 `ConfigurationError` 与其他异常并返回 `1`。README 增加 `..\llm\Scripts\python.exe -m streaming.main` 命令，说明正文写入标准输出、`[回调]` 事件写入标准错误流。每行 Python 有效代码都添加中文前置注释。

- [ ] **Step 4: 运行完整测试、检查格式并提交**

Run: `..\llm\Scripts\python.exe -m pytest -q`

Expected: PASS，且不访问网络。

Run: `git diff --check`

Expected: 无空白错误。

Commit: `git add -- langchain-learn/streaming/main.py langchain-learn/tests/test_streaming.py langchain-learn/README.md; git commit -m "docs: add streaming demo usage"`
