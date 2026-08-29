# LangChain 提示词工程示例包 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新建可运行的 LangChain 提示词工程示例包，并将六类提示词模板通过 LCEL 链连接到 OpenAI 兼容模型。

**Architecture:** `prompt_engineering` 包把模型配置与示例分离。`app.py` 仅负责读取环境变量并创建模型；`examples.py` 负责创建模板与调用 `prompt | model`；模块入口顺序执行示例。测试通过模板格式化和伪模型验证行为，不联网。

**Tech Stack:** Python、LangChain Core、langchain-openai、python-dotenv、pytest。

---

## 文件结构

- `langchain-learn/prompt_engineering/__init__.py`：包导出。
- `langchain-learn/prompt_engineering/app.py`：模型配置与 `invoke_prompt`。
- `langchain-learn/prompt_engineering/examples.py`：六个提示词 API 示例。
- `langchain-learn/prompt_engineering/main.py`：命令行入口。
- `langchain-learn/tests/test_prompt_engineering.py`：离线单元测试。
- `langchain-learn/README.md`：运行指引与 API 对照表。

### Task 1: 提示词构造的离线测试

**Files:**
- Create: `langchain-learn/tests/test_prompt_engineering.py`

- [ ] **Step 1: Write the failing test**

```python
def test_build_text_prompt_formats_named_variables():
    prompt = build_text_prompt()
    assert "Python" in prompt.format(topic="Python")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_prompt_engineering.py::test_build_text_prompt_formats_named_variables -v`

Expected: FAIL，因为模块尚不存在。

- [ ] **Step 3: Write minimal implementation**

```python
def build_text_prompt() -> PromptTemplate:
    return PromptTemplate.from_template("请用一句话解释 {topic}。")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_prompt_engineering.py::test_build_text_prompt_formats_named_variables -v`

Expected: PASS。

- [ ] **Step 5: Commit**

```powershell
git add langchain-learn/tests/test_prompt_engineering.py langchain-learn/prompt_engineering
git commit -m "feat: add prompt template example"
```

### Task 2: 聊天模板、消息占位符和少样本模板

**Files:**
- Modify: `langchain-learn/tests/test_prompt_engineering.py`
- Modify: `langchain-learn/prompt_engineering/examples.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_chat_prompt_includes_system_and_human_messages():
    messages = build_chat_prompt().format_messages(question="什么是向量数据库？")
    assert [message.type for message in messages] == ["system", "human"]

def test_history_prompt_accepts_messages_placeholder():
    messages = build_history_prompt().format_messages(history=[], question="继续说明")
    assert messages[-1].content == "继续说明"

def test_few_shot_prompts_include_examples():
    assert "输入：晴天" in build_few_shot_prompt().format(text="下雨")
    assert len(build_few_shot_chat_prompt().format_messages(question="冷")) == 6
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_prompt_engineering.py -v`

Expected: FAIL，因为构造函数尚未定义。

- [ ] **Step 3: Write minimal implementation**

实现 `build_chat_prompt()`、`build_history_prompt()`、`build_few_shot_prompt()` 与 `build_few_shot_chat_prompt()`；分别使用 `ChatPromptTemplate`、`MessagesPlaceholder`、`FewShotPromptTemplate`、`FewShotChatMessagePromptTemplate`。每条 Python 有效代码前加入中文独立行注释。

- [ ] **Step 4: Run tests to verify they pass**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_prompt_engineering.py -v`

Expected: PASS。

- [ ] **Step 5: Commit**

```powershell
git add langchain-learn/tests/test_prompt_engineering.py langchain-learn/prompt_engineering/examples.py
git commit -m "feat: add chat and few-shot prompt examples"
```

### Task 3: 长度示例选择器与模型调用链

**Files:**
- Modify: `langchain-learn/tests/test_prompt_engineering.py`
- Create: `langchain-learn/prompt_engineering/app.py`
- Modify: `langchain-learn/prompt_engineering/examples.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_selector_prompt_formats_selected_examples():
    rendered = build_selector_prompt().format(text="阴天")
    assert "输入：晴天" in rendered

def test_invoke_prompt_passes_values_to_chain():
    result = invoke_prompt(FakePrompt(), FakeModel(), {"topic": "Python"})
    assert result == "模拟回复"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_prompt_engineering.py -v`

Expected: FAIL，因为选择器和调用函数尚未定义。

- [ ] **Step 3: Write minimal implementation**

实现 `build_selector_prompt()`，使用 `LengthBasedExampleSelector`；实现 `get_model()` 和 `invoke_prompt(prompt, model, values)`，其中调用链为 `prompt | model` 并返回 `str(chain.invoke(values).content)`。模型配置使用当前项目既有的 `.env` 与变量名。

- [ ] **Step 4: Run tests to verify they pass**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_prompt_engineering.py -v`

Expected: PASS，且不访问网络。

- [ ] **Step 5: Commit**

```powershell
git add langchain-learn/tests/test_prompt_engineering.py langchain-learn/prompt_engineering
git commit -m "feat: connect prompt examples to chat model"
```

### Task 4: 入口、文档和全量验证

**Files:**
- Create: `langchain-learn/prompt_engineering/main.py`
- Create: `langchain-learn/prompt_engineering/__init__.py`
- Modify: `langchain-learn/README.md`

- [ ] **Step 1: Write the failing import test**

```python
def test_prompt_engineering_package_exports_runner():
    from prompt_engineering.main import run_examples
    assert callable(run_examples)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `..\llm\Scripts\python.exe -m pytest tests/test_prompt_engineering.py::test_prompt_engineering_package_exports_runner -v`

Expected: FAIL，因为入口尚不存在。

- [ ] **Step 3: Write minimal implementation and documentation**

实现 `run_examples()`，以名称和输入值列表顺序执行六个示例，打印模型回答；`main()` 捕获配置与服务异常后返回非零退出码。README 添加 `python -m prompt_engineering.main` 命令和 API 对照表。

- [ ] **Step 4: Run complete verification**

Run: `..\llm\Scripts\python.exe -m compileall prompt_engineering; ..\llm\Scripts\python.exe -m pytest -q`

Expected: 编译成功，全部测试 PASS。

- [ ] **Step 5: Commit**

```powershell
git add langchain-learn/prompt_engineering langchain-learn/tests/test_prompt_engineering.py langchain-learn/README.md
git commit -m "docs: document prompt engineering examples"
```
