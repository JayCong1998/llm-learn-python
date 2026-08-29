# LangChain 与 LangGraph 学习项目设计

## 目标

在仓库根目录创建两个相互独立、可运行的 Python 学习项目：`langchain-learn/` 与 `langgraph-learn/`。二者都使用根目录已有的 `llm` 虚拟环境，并通过环境变量调用 OpenAI 兼容 API。

## 项目结构

每个项目分别包含：

- `main.py`：可执行的最小示例。
- `requirements.txt`：该项目需要的 Python 包。
- `.env.example`：不含真实密钥的配置模板。
- `README.md`：安装、配置和运行说明。
- `tests/`：不联网的基础结构测试。

项目各自维护依赖清单和说明文档，互不导入对方的代码。运行时依赖共享的根目录 `llm` 虚拟环境，避免创建重复环境。

## 示例行为与数据流

`langchain-learn` 从 `.env` 读取 `OPENAI_API_KEY` 与可选的 `OPENAI_MODEL`，构建 `ChatOpenAI`，向模型发送一个固定的中文入门问题，并打印回复。

`langgraph-learn` 使用相同配置定义状态（`question`、`answer`），构建 `START -> call_model -> END` 的最小状态图。节点读取问题、调用模型并写回答案，入口脚本打印最终状态中的回答。

## 错误处理

两个入口都会在 API Key 缺失时提示复制 `.env.example` 为 `.env` 并填写密钥；模型调用失败时打印简洁错误信息并以非零状态退出。真实密钥不会被写入、提交或示例化。

## 验证

为两个项目提供不联网测试，验证所需文件、配置加载函数与 LangGraph 图构建接口可导入。完成后将在 `llm` 环境中安装依赖、编译 Python 文件并执行测试；实际模型调用由用户在配置密钥后自行触发。

## 范围

本次只提供最小的单次问答和单节点图，暂不加入聊天循环、持久记忆、工具调用、Web UI 或部署配置。
