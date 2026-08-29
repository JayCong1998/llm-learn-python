# LangChain and LangGraph Learning Projects Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create two independent, runnable Python learning projects for LangChain and LangGraph, secured by environment-based configuration.

**Architecture:** The root Git repository owns shared development metadata and one existing `llm` virtual environment. Each learning project is self-contained: a small importable application module, executable entry point, dependency list, safe `.env` template, documentation, and offline tests. The LangGraph project represents the same prompt/response use case as an explicit `START -> call_model -> END` state graph.

**Tech Stack:** Python 3.13, `langchain-openai`, `langgraph`, `python-dotenv`, `pytest`, Git.

---

## File structure

- `.gitignore` — ignores virtual environments, secrets, caches, and IDE metadata.
- `langchain-learn/app.py` — config validation and one LangChain model request.
- `langchain-learn/main.py` — command-line entry point and error-to-exit-code handling.
- `langchain-learn/requirements.txt` — LangChain project dependencies.
- `langchain-learn/.env.example` — safe model configuration template.
- `langchain-learn/README.md` — project-specific setup/run directions.
- `langchain-learn/tests/test_app.py` — offline configuration validation tests.
- `langgraph-learn/app.py` — config validation and graph construction.
- `langgraph-learn/main.py` — command-line graph invocation and error handling.
- `langgraph-learn/requirements.txt` — LangGraph project dependencies.
- `langgraph-learn/.env.example` — safe model configuration template.
- `langgraph-learn/README.md` — project-specific setup/run directions.
- `langgraph-learn/tests/test_app.py` — offline configuration and graph interface tests.

### Task 1: Initialize repository metadata

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Initialize Git and inspect the initial working tree**

Run: `git init; git status --short`

Expected: Git creates `.git`; `git status --short` has no tracked files.

- [ ] **Step 2: Add safe ignore rules**

Create `.gitignore`:

```gitignore
# Virtual environments and Python build artifacts
llm/
.venv/
__pycache__/
*.py[cod]
.pytest_cache/

# Secrets
.env
**/.env

# IDE files
.idea/
```

- [ ] **Step 3: Verify secrets and virtual environment are ignored**

Run: `git status --ignored --short`

Expected: `llm/` and `.idea/` appear as ignored; no `.env` file is created.

- [ ] **Step 4: Commit repository setup**

Run: `git add .gitignore docs/superpowers/specs/2026-08-29-langchain-langgraph-learning-design.md docs/superpowers/plans/2026-08-29-langchain-langgraph-learning.md; git commit -m "chore: initialize learning project repository"`

Expected: a commit containing only repository metadata and design documents.

### Task 2: Build the LangChain sample with tests first

**Files:**
- Create: `langchain-learn/app.py`
- Create: `langchain-learn/main.py`
- Create: `langchain-learn/tests/test_app.py`
- Create: `langchain-learn/requirements.txt`
- Create: `langchain-learn/.env.example`
- Create: `langchain-learn/README.md`

- [ ] **Step 1: Write failing configuration tests**

Create `langchain-learn/tests/test_app.py`:

```python
import pytest

from app import ConfigurationError, get_settings


def test_get_settings_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        get_settings()


def test_get_settings_uses_default_model(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    settings = get_settings()
    assert settings.model == "gpt-4.1-mini"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./llm/Scripts/python.exe -m pytest langchain-learn/tests/test_app.py -v`

Expected: FAIL because `app` does not exist.

- [ ] **Step 3: Implement the minimal LangChain application**

Create `langchain-learn/app.py`:

```python
from dataclasses import dataclass
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


class ConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str


def get_settings() -> Settings:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigurationError("OPENAI_API_KEY is missing. Copy .env.example to .env and add your key.")
    return Settings(api_key=api_key, model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))


def ask_question(question: str) -> str:
    settings = get_settings()
    model = ChatOpenAI(model=settings.model, api_key=settings.api_key)
    return model.invoke(question).content
```

Create `langchain-learn/main.py`:

```python
from app import ConfigurationError, ask_question


def main() -> int:
    try:
        print(ask_question("请用一句话解释 LangChain 的用途。"))
    except ConfigurationError as error:
        print(f"Configuration error: {error}")
        return 1
    except Exception as error:
        print(f"Model request failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Add runtime files and documentation**

Create `langchain-learn/requirements.txt`:

```text
langchain-openai
python-dotenv
pytest
```

Create `langchain-learn/.env.example`:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Create `langchain-learn/README.md` with commands to install `requirements.txt`, copy `.env.example` to `.env`, configure the key, and run `main.py` using `../llm/Scripts/python.exe`.

- [ ] **Step 5: Install dependencies and run tests**

Run: `./llm/Scripts/python.exe -m pip install -r langchain-learn/requirements.txt; ./llm/Scripts/python.exe -m pytest langchain-learn/tests/test_app.py -v`

Expected: installation succeeds and both tests PASS.

- [ ] **Step 6: Commit the LangChain sample**

Run: `git add langchain-learn; git commit -m "feat: add LangChain learning example"`

Expected: commit includes all LangChain sample files except `.env`.

### Task 3: Build the LangGraph sample with tests first

**Files:**
- Create: `langgraph-learn/app.py`
- Create: `langgraph-learn/main.py`
- Create: `langgraph-learn/tests/test_app.py`
- Create: `langgraph-learn/requirements.txt`
- Create: `langgraph-learn/.env.example`
- Create: `langgraph-learn/README.md`

- [ ] **Step 1: Write failing configuration and graph tests**

Create `langgraph-learn/tests/test_app.py`:

```python
import pytest

from app import ConfigurationError, build_graph, get_settings


def test_get_settings_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        get_settings()


def test_graph_preserves_question_without_model_call(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    graph = build_graph()
    assert "call_model" in graph.get_graph().nodes
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./llm/Scripts/python.exe -m pytest langgraph-learn/tests/test_app.py -v`

Expected: FAIL because `app` does not exist.

- [ ] **Step 3: Implement the minimal graph application**

Create `langgraph-learn/app.py`:

```python
from dataclasses import dataclass
import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph


class ConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str


class GraphState(TypedDict):
    question: str
    answer: str


def get_settings() -> Settings:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigurationError("OPENAI_API_KEY is missing. Copy .env.example to .env and add your key.")
    return Settings(api_key=api_key, model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))


def build_graph():
    settings = get_settings()
    model = ChatOpenAI(model=settings.model, api_key=settings.api_key)

    def call_model(state: GraphState) -> dict[str, str]:
        return {"answer": model.invoke(state["question"]).content}

    workflow = StateGraph(GraphState)
    workflow.add_node("call_model", call_model)
    workflow.add_edge(START, "call_model")
    workflow.add_edge("call_model", END)
    return workflow.compile()
```

Create `langgraph-learn/main.py`:

```python
from app import ConfigurationError, build_graph


def main() -> int:
    try:
        result = build_graph().invoke({"question": "请用一句话解释 LangGraph 的用途。", "answer": ""})
        print(result["answer"])
    except ConfigurationError as error:
        print(f"Configuration error: {error}")
        return 1
    except Exception as error:
        print(f"Model request failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Add runtime files and documentation**

Create `langgraph-learn/requirements.txt`:

```text
langchain-openai
langgraph
python-dotenv
pytest
```

Create `langgraph-learn/.env.example`:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Create `langgraph-learn/README.md` with commands to install `requirements.txt`, copy `.env.example` to `.env`, configure the key, and run `main.py` using `../llm/Scripts/python.exe`.

- [ ] **Step 5: Install dependencies and run tests**

Run: `./llm/Scripts/python.exe -m pip install -r langgraph-learn/requirements.txt; ./llm/Scripts/python.exe -m pytest langgraph-learn/tests/test_app.py -v`

Expected: installation succeeds and both tests PASS.

- [ ] **Step 6: Commit the LangGraph sample**

Run: `git add langgraph-learn; git commit -m "feat: add LangGraph learning example"`

Expected: commit includes all LangGraph sample files except `.env`.

### Task 4: Run end-to-end offline verification

**Files:**
- Modify: none

- [ ] **Step 1: Compile both projects**

Run: `./llm/Scripts/python.exe -m compileall langchain-learn langgraph-learn`

Expected: compilation succeeds without syntax errors.

- [ ] **Step 2: Run the full test suite**

Run: `./llm/Scripts/python.exe -m pytest langchain-learn/tests langgraph-learn/tests -v`

Expected: all four tests PASS.

- [ ] **Step 3: Verify each entry point handles absent credentials**

Run: `Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue; ./llm/Scripts/python.exe langchain-learn/main.py; ./llm/Scripts/python.exe langgraph-learn/main.py`

Expected: each command prints the configuration guidance and exits with code 1, without attempting a network call.

- [ ] **Step 4: Inspect the final repository state**

Run: `git status --short; git log --oneline -3`

Expected: clean working tree and three topical commits.
