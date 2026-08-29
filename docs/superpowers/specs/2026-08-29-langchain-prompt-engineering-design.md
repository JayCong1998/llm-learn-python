# LangChain 提示词工程示例包设计

## 目标

在 `langchain-learn/` 下新增 `prompt_engineering/` Python 包，演示 LangChain 中常用提示词工程 API，并将每种提示词模板通过 LCEL 链连接到现有 OpenAI 兼容聊天模型实际调用。

## 包结构

- `prompt_engineering/__init__.py`：标识该目录为包，并导出面向学习者的示例入口。
- `prompt_engineering/app.py`：复用现有环境变量约定，创建 `ChatOpenAI` 模型；提供将提示词对象与模型组合为 `prompt | model` 链的公共函数。
- `prompt_engineering/examples.py`：每种 API 一个小函数，负责构建提示词、调用链并返回可显示的文本结果。
- `prompt_engineering/main.py`：按固定顺序运行全部示例并输出名称与模型回复。
- `tests/test_prompt_engineering.py`：不联网验证模板的格式化结果、示例函数所依赖的链构建接口及包可导入性。

## 覆盖的 API

示例将覆盖：

1. `PromptTemplate`：带命名变量的文本提示词。
2. `ChatPromptTemplate`：system 与 human 消息组成的聊天提示词。
3. `MessagesPlaceholder`：将一段聊天历史插入模板。
4. `FewShotPromptTemplate`：使用固定示例引导文本任务。
5. `FewShotChatMessagePromptTemplate`：在聊天消息中注入少样本示例。
6. `LengthBasedExampleSelector`：按长度选择少样本示例，避免提示词过长。

## 数据流与错误处理

`main.py` 调用每个示例函数；示例函数从 `app.py` 获取模型并创建 `prompt | model` 链，调用 `invoke()` 后将 AI 消息内容转为字符串。模型配置继续从 `OPENAI_API_KEY`、可选 `OPENAI_MODEL` 和可选 `OPENAI_BASE_URL` 读取。缺少密钥时沿用项目现有的明确配置错误；网络或模型服务错误由入口捕获、打印简洁信息并以非零状态退出。

## 文档与验证

README 增加新包的运行命令、配置复用说明和 API 对照表。测试不需要 API Key，也不会调用网络；使用替身模型或只验证提示词格式化和链构造。实施时遵循仓库规则：每一条新增或修改的 Python 有效代码前均有准确、简短的中文独立行注释。

## 范围边界

本包用于提示词工程学习，不引入记忆、Agent、工具调用、流式输出、Web UI 或新增模型供应商。
