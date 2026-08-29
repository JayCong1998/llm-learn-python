# Python 逐行中文注释与仓库规则设计

## 目标

为 `langchain-learn/` 与 `langgraph-learn/` 中的六个 Python 源码和测试文件补充逐行中文说明，并以根目录 `AGENTS.md` 固化后续 Python 代码的中文注释要求。

## 范围

修改范围仅限以下文件：

- `langchain-learn/app.py`
- `langchain-learn/main.py`
- `langchain-learn/tests/test_langchain_app.py`
- `langgraph-learn/app.py`
- `langgraph-learn/main.py`
- `langgraph-learn/tests/test_langgraph_app.py`
- 根目录 `AGENTS.md`

不修改用户原有的根目录 `main.py`、`llm/` 虚拟环境、依赖代码或已有项目文档。

## 注释策略

每条有效 Python 语句前放置一条简短、准确的中文独立行注释。导入、类和函数定义、赋值、流程控制、调用、断言、返回及入口保护均覆盖。空行、已有注释与模块/函数文档字符串不重复添加说明，以避免无意义重复。

## 仓库规则

`AGENTS.md` 规定：今后新建或修改的项目 Python 有效代码行必须有对应的中文独立行注释；注释应说明意图而非机械复述语法；空行、纯注释和文档字符串可豁免。

## 验证

不改变任何运行逻辑。完成后以项目根目录的 `llm` 环境运行两个项目测试目录的完整 pytest 套件，并运行 `compileall` 验证语法。
