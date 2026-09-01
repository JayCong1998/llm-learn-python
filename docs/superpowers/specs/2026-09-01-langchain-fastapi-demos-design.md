# LangChain FastAPI 功能示例设计

## 目标

在 `langchain-learn` 中增加 FastAPI 依赖和一组可独立学习、可通过 Swagger 调用的 API Demo，覆盖提示词模板、两种流式输出、两种消息记忆后端、结构化输出、本地工具调用、本地与远程 MCP 调用，以及本地 `SKILL.md` 技能调用。

现有提示词工程与流式命令行示例继续保留。新 API 复用其中适合的模板和模型配置，但不会破坏已有入口。

## 已确认的范围

- Skill 指项目内的本地 `SKILL.md`，不调用 OpenAI 托管 Skill。
- 消息记忆同时支持进程内和 SQLite，并通过环境变量选择后端。
- MCP 同时支持项目内置的本地 Server 和通过 URL 配置的远程 Server。
- 流式输出同时提供纯文本分块与 SSE。
- 所有 Python 新增或修改的有效代码行前，都必须有准确、简短的中文独立行注释。
- 自动化测试不得依赖真实密钥、真实模型或外部网络。

## 方案选择

采用模块化 FastAPI 应用，每项能力拥有独立 router 和 service，共享配置、模型工厂、响应约定与异常处理。这种结构比单文件教学示例更易于理解和测试，同时比把全部能力隐藏在统一 Agent 中更能展示每个 LangChain 概念的最小实现。

未采用的方案：

- 单文件 FastAPI：文件较少，但八类功能会让模型配置、MCP 生命周期、记忆状态和路由逻辑互相耦合。
- 统一 LangGraph Agent：扩展能力更强，但会掩盖提示词、结构化输出和基础工具绑定各自的用法。

## 目录设计

```text
langchain-learn/
├─ api/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  ├─ dependencies.py
│  │  ├─ errors.py
│  │  └─ schemas.py
│  └─ modules/
│     ├─ prompts/
│     ├─ streaming/
│     ├─ memory/
│     ├─ structured/
│     ├─ tools/
│     ├─ mcp/
│     └─ skills/
├─ mcp_servers/
│  └─ demo_server.py
├─ skills/
│  ├─ code_explainer/SKILL.md
│  └─ text_summarizer/SKILL.md
└─ tests/api/
```

每个模块目录只包含该主题的请求/响应模型、服务和 router。跨模块共用行为放入 `api/core`，不会建立模块之间的反向依赖。

## API 设计

### 通用约定

- API 前缀为 `/api/v1`。
- 非流式成功响应使用 `{"data": ...}` 外层结构。
- Agent、工具与 MCP 响应在 `data` 中同时返回 `answer` 和精简的 `tool_calls`。
- FastAPI 自动生成 `/docs` 和 `/openapi.json`。
- `GET /health` 不读取密钥、不创建模型，只返回应用存活状态。

### 端点

| 方法与路径 | 用途 |
| --- | --- |
| `GET /health` | 应用存活检查。 |
| `POST /api/v1/prompts/{template_type}/invoke` | 调用注册表内的固定提示词模板。 |
| `POST /api/v1/stream/text` | 以 `text/plain` 返回模型文本分块。 |
| `POST /api/v1/stream/sse` | 以 `text/event-stream` 返回 `token`、`done`、`error` 事件。 |
| `POST /api/v1/memory/chat` | 根据 `session_id` 继续一段有记忆的会话。 |
| `DELETE /api/v1/memory/{session_id}` | 清除指定会话，不影响其他会话。 |
| `POST /api/v1/structured/extract` | 将自然语言联系人描述提取成经 Pydantic 校验的 JSON。 |
| `POST /api/v1/tools/chat` | 让 Agent 在固定安全工具中选择并调用。 |
| `POST /api/v1/mcp/chat` | 发现并调用当前配置的本地或远程 MCP 工具。 |
| `GET /api/v1/skills` | 列出项目允许调用的本地技能及描述。 |
| `POST /api/v1/skills/{skill_name}/invoke` | 加载指定 `SKILL.md` 并按其指令处理输入。 |

提示词 `template_type` 使用固定枚举，覆盖现有的文本模板、聊天模板、历史占位符、文本少样本、聊天少样本和长度选择少样本。请求只提供模板所需变量，不允许提交任意系统提示词。

## 组件与数据流

### 配置与模型

配置层继续读取 `langchain-learn/.env`，并统一校验 `OPENAI_API_KEY`、`OPENAI_MODEL` 和 `OPENAI_BASE_URL`。模型工厂按请求需要创建 `ChatOpenAI`，测试可通过 FastAPI 依赖覆盖注入替身模型。

新增配置包括：

- `MEMORY_BACKEND=memory|sqlite`
- `MEMORY_SQLITE_PATH`，默认指向项目内未纳入版本控制的数据文件
- `MCP_MODE=local|remote`
- `MCP_REMOTE_URL`
- 可选的远程 MCP 请求头配置，其值不得写入日志或响应

### 提示词模板

router 根据枚举从固定注册表取得模板，service 使用 LCEL 的 `prompt | model` 组合执行。响应包含模板类型和模型文本，便于从 Swagger 对比各种模板行为。

### 流式输出

一个异步生成器负责消费模型增量消息并只产出非空文本。纯文本端点直接转发文本；SSE 适配器把同一批分块序列化为命名事件。正常结束发出 `done`，生成期间失败发出不含内部异常信息的 `error`。客户端断开时取消后续消费。

### 消息记忆

记忆服务使用 LangGraph checkpointer 保存按线程隔离的消息状态。`session_id` 映射为 `thread_id`。内存模式适合教学和单进程运行；SQLite 模式允许应用重启后继续会话。两者实现同一服务接口，router 和请求格式不随后端变化。

清理操作只删除给定线程的状态。空白或超长 `session_id` 在进入存储层前由请求校验拒绝。

### 结构化输出

联系人提取 Schema 包含姓名、电子邮箱、电话号码和备注等教学字段。service 使用 `ChatOpenAI.with_structured_output()` 获取 Pydantic 对象，FastAPI 再根据响应模型序列化。模型返回不符合 Schema 时映射为统一上游响应错误。

### 本地工具调用

工具 Agent 只注册项目定义的安全工具，例如受限四则运算和当前时间。计算器使用允许的 AST 节点或等价的安全解析逻辑，禁止 `eval`、属性访问、函数调用和任意代码执行。响应从 Agent 消息中提取最终答案及工具名称和参数，不暴露内部推理文本。

### MCP 调用

项目提供一个可通过 stdio 启动的内置 MCP Demo Server，暴露确定性的计算或查询工具。远程模式使用 `MultiServerMCPClient` 读取 URL 和可选请求头。客户端发现工具后，把适配后的 LangChain tools 交给 Agent，并在请求完成后释放无状态会话资源。

本地和远程模式共享 `/api/v1/mcp/chat` 请求格式。未配置远程 URL、连接失败或工具发现失败时返回经过清理的上游错误，不回显认证头。

### 本地 Skill 调用

技能加载器只扫描固定 `skills` 根目录下一层的安全名称，并要求目标文件名严格为 `SKILL.md`。名称必须满足小写字母、数字、连字符或下划线组成的 slug；绝对路径、分隔符和 `..` 均被拒绝。加载后的技能指令作为受控系统消息，用户输入作为独立 human 消息交给模型。

首批示例技能为代码解释和文本总结。技能列表端点只返回名称与简短描述，不返回文件系统绝对路径。

## 错误处理与安全

- 请求字段不合法由 FastAPI 返回 422。
- 缺少模型或后端必要配置返回 503。
- 模型、MCP 或其他上游调用失败返回 502。
- 未找到本地技能返回 404，非法技能名称返回 422。
- 业务错误响应使用稳定错误码和面向调用者的说明，不包含堆栈、密钥、认证头或上游响应原文。
- `.env`、SQLite 运行数据和测试临时文件不得提交到 Git。
- 服务不接受任意 Python 表达式、任意本地路径或客户端自定义 MCP 启动命令。

## 依赖

在现有 `langchain-openai`、`python-dotenv` 和 `pytest` 基础上加入 FastAPI、ASGI Server、LangChain Agent/LangGraph、SQLite checkpointer、MCP adapter、MCP SDK，以及 FastAPI 测试客户端需要的 HTTP 库。实施时锁定彼此兼容的最低版本范围，并在 README 中给出安装命令。

## 测试策略

采用测试先行：每个行为先写失败测试，确认失败原因正确，再写最小实现。

- 应用测试验证健康检查、router 注册和 OpenAPI 路径。
- 每个非流式模块覆盖成功、请求校验、配置缺失和上游失败。
- 流式测试验证媒体类型、分块顺序、空分块过滤、SSE 事件名称与结束事件。
- 记忆测试分别使用进程内 saver 和临时 SQLite，验证同会话延续、跨会话隔离、清理和 SQLite 重建后的恢复。
- 工具测试验证合法计算与危险表达式拒绝，并使用替身 Agent 验证调用摘要。
- MCP 测试验证本地/远程配置选择、工具发现结果和错误映射；默认测试不建立外部网络连接。
- Skill 测试验证枚举、合法调用、未知技能、非法名称和目录穿越拦截。
- 模型、Agent、MCP Client 和存储实现通过依赖注入替换，测试不读取用户的真实 `.env`。

完成前运行项目全量 `pytest`，确认应用可导入，并检查生成的 OpenAPI 文档包含全部约定端点。真实模型与远程 MCP 作为 README 中的手工验证步骤，不作为离线测试通过条件。

## 文档与演示

`langchain-learn/README.md` 将补充：

- 安装依赖和启动 Uvicorn 的命令
- 完整环境变量说明
- Swagger `/docs` 地址
- 每个端点的 PowerShell 或 `curl` 示例
- 两种记忆后端、两种 MCP 模式和两种流式协议的切换方法
- 本地 MCP Server 与本地 Skill 的扩展示例

这样，用户既能在 Swagger 中逐项调用，也能从独立模块源码看到每个 LangChain 能力的最小实现。
