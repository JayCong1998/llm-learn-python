# Chinese Line Comments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Chinese comments for each effective Python statement in both learning projects and record the convention in `AGENTS.md`.

**Architecture:** This is a documentation-only source edit: the six Python files retain their imports, functions, control flow, and public interfaces exactly. `AGENTS.md` is the repository-level instruction source for future Python changes. Existing automated tests and compilation prove comments did not alter behavior.

**Tech Stack:** Python 3.13, pytest, Git.

---

### Task 1: Add the repository comment convention

**Files:**
- Create: `AGENTS.md`

- [ ] **Step 1: Create the contributor rule file**

Write `AGENTS.md`:

```markdown
# 代码注释规则

对于本仓库中新增或修改的 Python 有效代码行，必须在其前一行添加准确、简短的中文独立行注释，说明该语句的意图。

空行、纯注释和文档字符串不需要重复添加注释；注释不得泄露密钥或其他敏感信息。
```

- [ ] **Step 2: Verify the file contains the mandatory Chinese-comment rule**

Run: `rg -n "Python 有效代码行|中文独立行注释" AGENTS.md`

Expected: both phrases are present.

### Task 2: Annotate the LangChain learning project

**Files:**
- Modify: `langchain-learn/app.py`
- Modify: `langchain-learn/main.py`
- Modify: `langchain-learn/tests/test_langchain_app.py`

- [ ] **Step 1: Add a Chinese standalone comment before every effective statement**

Preserve all executable source tokens and insert concise Chinese intent comments before imports, class/function definitions, assignments, branches, calls, returns, assertions, and the entry-point guard.

- [ ] **Step 2: Compile the annotated files**

Run: `./llm/Scripts/python.exe -m compileall -q langchain-learn`

Expected: command exits with code 0 and prints no syntax error.

- [ ] **Step 3: Run LangChain project tests**

Run: `./llm/Scripts/python.exe -m pytest langchain-learn/tests -v`

Expected: 2 tests PASS.

### Task 3: Annotate the LangGraph learning project

**Files:**
- Modify: `langgraph-learn/app.py`
- Modify: `langgraph-learn/main.py`
- Modify: `langgraph-learn/tests/test_langgraph_app.py`

- [ ] **Step 1: Add a Chinese standalone comment before every effective statement**

Preserve all executable source tokens and insert concise Chinese intent comments before imports, class/function definitions, assignments, branches, calls, returns, assertions, graph node/edge creation, and the entry-point guard.

- [ ] **Step 2: Compile the annotated files**

Run: `./llm/Scripts/python.exe -m compileall -q langgraph-learn`

Expected: command exits with code 0 and prints no syntax error.

- [ ] **Step 3: Run LangGraph project tests**

Run: `./llm/Scripts/python.exe -m pytest langgraph-learn/tests -v`

Expected: 2 tests PASS.

### Task 4: Verify and commit the documentation-only change

**Files:**
- Modify: `AGENTS.md`
- Modify: `langchain-learn/app.py`
- Modify: `langchain-learn/main.py`
- Modify: `langchain-learn/tests/test_langchain_app.py`
- Modify: `langgraph-learn/app.py`
- Modify: `langgraph-learn/main.py`
- Modify: `langgraph-learn/tests/test_langgraph_app.py`

- [ ] **Step 1: Run the full test suite and compile both projects**

Run: `./llm/Scripts/python.exe -m pytest langchain-learn/tests langgraph-learn/tests -v; ./llm/Scripts/python.exe -m compileall -q langchain-learn langgraph-learn`

Expected: 4 tests PASS and no compilation errors.

- [ ] **Step 2: Inspect the source diff for unintended executable changes**

Run: `git diff --check; git diff --word-diff=porcelain -- langchain-learn langgraph-learn`

Expected: no whitespace errors; changes are only comments.

- [ ] **Step 3: Commit the convention and annotations**

Run: `git add AGENTS.md langchain-learn langgraph-learn docs/superpowers/plans/2026-08-29-chinese-line-comments.md; git commit -m "docs: add Chinese code comments"`

Expected: one commit contains the rule, annotations, and plan.
