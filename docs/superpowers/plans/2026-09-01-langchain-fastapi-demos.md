# LangChain FastAPI 功能示例 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `langchain-learn` 中交付可通过 Swagger 调用的 FastAPI 教学 API，完整演示提示词模板、纯文本/SSE 流、内存/SQLite 消息记忆、结构化输出、本地工具、本地/远程 MCP 与本地 `SKILL.md`。

**Architecture:** 使用一个 FastAPI 应用聚合七个边界清晰的功能包；路由只处理 HTTP 和响应映射，service 负责 LangChain/LangGraph 调用。模型、Agent、checkpointer、MCP client 和技能根目录均可注入，使全套测试无需真实密钥和网络。

**Tech Stack:** Python 3.11+、FastAPI 0.141+、Uvicorn、LangChain 1.x、langchain-openai 1.6+、LangGraph 1.2+、langgraph-checkpoint-sqlite、langchain-mcp-adapters 0.3+、MCP Python SDK、Pydantic 2、HTTPX、pytest。

---

## 文件结构

- Create: `langchain-learn/api/__init__.py` — API 包入口。
- Create: `langchain-learn/api/main.py` — FastAPI 工厂、router 注册和异常处理。
- Create: `langchain-learn/api/core/config.py` — API 专用配置和枚举。
- Create: `langchain-learn/api/core/dependencies.py` — 模型与 service 依赖工厂。
- Create: `langchain-learn/api/core/errors.py` — 稳定业务异常。
- Create: `langchain-learn/api/core/schemas.py` — 通用请求、响应与工具轨迹模型。
- Create: `langchain-learn/api/modules/*/api.py` — 各主题的请求模型与 HTTP router。
- Create: `langchain-learn/api/modules/*/service.py` — 各主题的 LangChain 行为。
- Create: `langchain-learn/mcp_servers/demo_server.py` — 内置 stdio MCP Server。
- Create: `langchain-learn/skills/code_explainer/SKILL.md` — 代码解释技能。
- Create: `langchain-learn/skills/text_summarizer/SKILL.md` — 文本总结技能。
- Create: `langchain-learn/tests/api/` — 离线 API、service 和安全测试。
- Modify: `langchain-learn/requirements.txt` — 增加 API、Agent、持久化和 MCP 依赖。
- Modify: `langchain-learn/.env.example` — 增加记忆与 MCP 配置示例。
- Modify: `.gitignore` — 忽略 SQLite 运行数据。
- Modify: `langchain-learn/README.md` — 增加启动和全部端点示例。

所有新增或修改的 Python 有效代码行前必须有准确、简短的中文独立行注释。以下代码块展示目标接口；实现时同样逐行添加注释，不得用行尾注释代替。

### Task 1: 增加依赖、配置、通用 Schema 与应用壳

**Files:**
- Modify: `langchain-learn/requirements.txt`
- Create: `langchain-learn/api/__init__.py`
- Create: `langchain-learn/api/core/__init__.py`
- Create: `langchain-learn/api/core/config.py`
- Create: `langchain-learn/api/core/errors.py`
- Create: `langchain-learn/api/core/schemas.py`
- Create: `langchain-learn/api/main.py`
- Create: `langchain-learn/tests/api/conftest.py`
- Create: `langchain-learn/tests/api/test_foundation.py`

- [ ] **Step 1: 写应用壳失败测试**

```python
# 导入 FastAPI 测试客户端。
from fastapi.testclient import TestClient

# 导入应用工厂。
from api.main import create_app


# 验证健康检查不依赖模型配置。
def test_health_endpoint_is_available_without_model() -> None:
    # 创建隔离的测试应用。
    application = create_app()
    # 创建同步测试客户端。
    client = TestClient(application)
    # 调用健康检查端点。
    response = client.get("/health")
    # 验证端点成功响应。
    assert response.status_code == 200
    # 验证稳定的健康检查结构。
    assert response.json() == {"data": {"status": "ok"}}


# 验证 OpenAPI 包含所有约定路由。
def test_openapi_contains_all_demo_routes() -> None:
    # 创建隔离的测试应用。
    application = create_app()
    # 读取应用生成的 OpenAPI 路径。
    paths = application.openapi()["paths"]
    # 定义设计中确认的路径集合。
    expected_paths = {
        "/health",
        "/api/v1/prompts/{template_type}/invoke",
        "/api/v1/stream/text",
        "/api/v1/stream/sse",
        "/api/v1/memory/chat",
        "/api/v1/memory/{session_id}",
        "/api/v1/structured/extract",
        "/api/v1/tools/chat",
        "/api/v1/mcp/chat",
        "/api/v1/skills",
        "/api/v1/skills/{skill_name}/invoke",
    }
    # 验证全部路径已注册。
    assert expected_paths <= set(paths)
```

- [ ] **Step 2: 运行测试并确认因 `api` 包缺失而失败**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_foundation.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'api'`。

- [ ] **Step 3: 增加兼容依赖与通用类型**

将 `requirements.txt` 更新为：

```text
fastapi>=0.141,<1
httpx>=0.28,<1
langchain>=1.2,<2
langchain-mcp-adapters>=0.3,<1
langchain-openai>=1.6,<2
langgraph>=1.2,<2
langgraph-checkpoint-sqlite>=3.0,<4
mcp>=1.0,<2
python-dotenv>=1.0,<2
pytest>=8,<9
uvicorn[standard]>=0.35,<1
```

在 `config.py` 定义 `MemoryBackend(str, Enum)` 的 `memory`、`sqlite` 和 `McpMode(str, Enum)` 的 `local`、`remote`，并定义不可变 `ApiSettings`。`ApiSettings.from_environment()` 读取 `MEMORY_BACKEND`、`MEMORY_SQLITE_PATH`、`MCP_MODE`、`MCP_REMOTE_URL` 和 JSON 格式的 `MCP_REMOTE_HEADERS`；无效枚举或非字符串请求头抛出 `ConfigurationError`，异常文本不得包含请求头值。

在 `schemas.py` 实现以下通用对象：

```python
# 导入泛型类型变量。
from typing import Generic, TypeVar

# 导入 Pydantic 数据模型和字段约束。
from pydantic import BaseModel, Field

# 声明响应数据的泛型类型。
DataT = TypeVar("DataT")


# 定义统一成功响应外层结构。
class DataEnvelope(BaseModel, Generic[DataT]):
    # 保存端点返回的数据。
    data: DataT


# 定义通用自然语言请求。
class QuestionRequest(BaseModel):
    # 限制问题不能为空且避免无界输入。
    question: str = Field(min_length=1, max_length=4000)


# 定义一次工具调用摘要。
class ToolCallTrace(BaseModel):
    # 保存工具名称。
    name: str
    # 保存模型生成的结构化参数。
    arguments: dict[str, object]


# 定义 Agent 类端点的结果。
class AgentReply(BaseModel):
    # 保存最终自然语言答案。
    answer: str
    # 保存实际发生的工具调用摘要。
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)
```

在 `errors.py` 定义 `ConfigurationError`、`UpstreamServiceError`、`ResourceNotFoundError` 和 `InvalidResourceNameError`，每类保存稳定 `code` 与安全 `message`。

- [ ] **Step 4: 创建应用工厂并先注册占位 router 对象**

`create_app()` 创建标题为 `LangChain API Demos` 的 FastAPI 实例，注册 `/health` 和七个模块 router。模块初始 router 只需存在，具体行为在后续任务通过 TDD 增加。注册异常处理器：配置错误映射 503、上游错误映射 502、资源不存在映射 404、非法资源名映射 422，统一返回 `{"error": {"code": error.code, "message": error.message}}`。

- [ ] **Step 5: 安装依赖并运行基础测试**

Run: `..\llm\Scripts\python.exe -m pip install -r requirements.txt`

Expected: exit 0，所有依赖解析成功。

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_foundation.py::test_health_endpoint_is_available_without_model -v`

Expected: PASS；OpenAPI 完整路径测试此时仍 FAIL，以便后续模块逐个补齐。

- [ ] **Step 6: 提交基础设施**

```powershell
git add langchain-learn/requirements.txt langchain-learn/api langchain-learn/tests/api
git commit -m "feat: scaffold langchain demo api"
```

### Task 2: 提示词模板 API

**Files:**
- Create: `langchain-learn/api/modules/prompts/__init__.py`
- Create: `langchain-learn/api/modules/prompts/service.py`
- Create: `langchain-learn/api/modules/prompts/api.py`
- Create: `langchain-learn/tests/api/test_prompts_api.py`

- [ ] **Step 1: 写失败的模板调用测试**

测试参数化六种类型：`text`、`chat`、`history`、`few-shot`、`few-shot-chat`、`selector`。依赖覆盖传入 `FakePromptService`，其 `invoke(template_type, text)` 返回可观察的 `template_type`、`rendered`、`answer`。断言 `POST /api/v1/prompts/text/invoke` 接收 `{"text":"Python"}` 并返回：

```json
{"data":{"template_type":"text","rendered":"请用一句话解释 Python。","answer":"模拟回答"}}
```

另写未知枚举返回 422、空文本返回 422 的测试。

- [ ] **Step 2: 运行并确认路由缺失失败**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_prompts_api.py -v`

Expected: FAIL，路径返回 404 或缺少依赖符号。

- [ ] **Step 3: 实现固定模板注册表与 LCEL 调用**

`PromptService` 复用 `prompt_engineering.examples` 的六个 builder。它把统一 `text` 映射为各模板需要的 `topic`、`question` 或 `text`，历史模板固定传入空 `history`。先调用 `prompt.format_prompt(**values)` 得到可展示文本，再执行 `prompt | model`；只返回 `str(response.content)`。

```python
# 定义提示词 API 的响应数据。
class PromptResult(BaseModel):
    # 保存选中的固定模板类型。
    template_type: PromptTemplateType
    # 保存完成变量替换后的提示词文本。
    rendered: str
    # 保存模型回答。
    answer: str


# 定义提示词 service 的核心调用。
def invoke(self, template_type: PromptTemplateType, text: str) -> PromptResult:
    # 从白名单注册表创建指定模板。
    prompt = self.prompt_builders[template_type]()
    # 将统一输入转换为模板变量。
    values = self.value_builders[template_type](text)
    # 渲染模板以便教学展示。
    rendered = prompt.format_prompt(**values).to_string()
    # 组合模板和模型形成 LCEL 链。
    response = (prompt | self.model).invoke(values)
    # 返回模板、渲染结果和模型正文。
    return PromptResult(template_type=template_type, rendered=rendered, answer=str(response.content))
```

- [ ] **Step 4: 运行提示词测试和既有回归**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_prompts_api.py tests/test_prompt_engineering.py -v`

Expected: PASS。

- [ ] **Step 5: 提交提示词 API**

```powershell
git add langchain-learn/api/modules/prompts langchain-learn/tests/api/test_prompts_api.py
git commit -m "feat: expose prompt template api"
```

### Task 3: 纯文本与 SSE 流式 API

**Files:**
- Create: `langchain-learn/api/modules/streaming/__init__.py`
- Create: `langchain-learn/api/modules/streaming/service.py`
- Create: `langchain-learn/api/modules/streaming/api.py`
- Create: `langchain-learn/tests/api/test_streaming_api.py`

- [ ] **Step 1: 写两个协议的失败测试**

覆盖 streaming service，让它依次异步产出 `你`、空串、`好`。断言 `/text` 的 content-type 以 `text/plain` 开头且正文为 `你好`；断言 `/sse` 的 content-type 以 `text/event-stream` 开头，正文依次包含 `event: token`、两个 JSON token 数据和 `event: done`。再让替身在第一个 token 后抛错，验证 SSE 只发安全 `error` 事件，不包含原始异常。

- [ ] **Step 2: 运行并确认流式路由不存在**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_streaming_api.py -v`

Expected: FAIL with 404。

- [ ] **Step 3: 实现共享异步分块与两个适配器**

```python
# 定义异步读取非空模型文本的生成器。
async def stream_tokens(self, question: str) -> AsyncIterator[str]:
    # 异步遍历模型消息分块。
    async for chunk in self.model.astream(question):
        # 读取当前分块内容。
        content = getattr(chunk, "content", "")
        # 只转发非空字符串。
        if isinstance(content, str) and content:
            # 产出当前文本分块。
            yield content


# 将 token 转换为 SSE 帧。
def encode_sse(event: str, data: dict[str, object]) -> str:
    # 用 JSON 保留中文并避免手工转义。
    payload = json.dumps(data, ensure_ascii=False)
    # 返回标准命名 SSE 事件。
    return f"event: {event}\ndata: {payload}\n\n"
```

`/text` 使用 `StreamingResponse(service.stream_tokens(payload.question), media_type="text/plain; charset=utf-8")`。`/sse` 的内部生成器正常时逐 token 发事件并最终发 `done`；异常时发 `{"message":"模型流式调用失败"}` 的 `error` 事件。请求取消异常必须继续抛出，不转换为错误帧。

- [ ] **Step 4: 回归新旧流式测试**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_streaming_api.py tests/test_streaming.py -v`

Expected: PASS。

- [ ] **Step 5: 提交流式 API**

```powershell
git add langchain-learn/api/modules/streaming langchain-learn/tests/api/test_streaming_api.py
git commit -m "feat: add text and sse streaming api"
```

### Task 4: 内存与 SQLite 消息记忆 API

**Files:**
- Create: `langchain-learn/api/modules/memory/__init__.py`
- Create: `langchain-learn/api/modules/memory/service.py`
- Create: `langchain-learn/api/modules/memory/api.py`
- Create: `langchain-learn/tests/api/test_memory_service.py`
- Create: `langchain-learn/tests/api/test_memory_api.py`

- [ ] **Step 1: 写两种后端的失败测试**

用一个确定性 fake chat model 创建 Agent，分别传 `InMemorySaver()` 与连接到 `tmp_path / "memory.sqlite"` 的 `SqliteSaver`。依次向相同 `session_id` 发送“我叫小明”和“我叫什么”，断言第二次调用的模型输入含第一轮消息；另用不同 session 断言历史隔离。关闭并重新打开 SQLite 连接后，重新创建 service 并验证同一线程状态仍存在。最后调用 `clear("session-a")`，断言只删除该线程。

- [ ] **Step 2: 运行并确认 memory service 缺失**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_memory_service.py -v`

Expected: FAIL with missing `MemoryChatService`。

- [ ] **Step 3: 实现 checkpointer 工厂和线程级调用**

```python
# 定义有会话记忆的聊天服务。
class MemoryChatService:
    # 初始化模型、检查点存储和无工具 Agent。
    def __init__(self, model: BaseChatModel, checkpointer: BaseCheckpointSaver) -> None:
        # 保存检查点存储以支持清理。
        self.checkpointer = checkpointer
        # 创建使用短期记忆的 Agent。
        self.agent = create_agent(model=model, tools=[], checkpointer=checkpointer, system_prompt="请结合当前会话历史回答。")

    # 在指定会话中发送一条消息。
    def chat(self, session_id: str, message: str) -> str:
        # 将 API 会话标识映射为 LangGraph 线程标识。
        config = {"configurable": {"thread_id": session_id}}
        # 只提交当前新增的用户消息。
        result = self.agent.invoke({"messages": [{"role": "user", "content": message}]}, config=config)
        # 返回 Agent 最后一条消息正文。
        return str(result["messages"][-1].content)

    # 清除指定会话的全部检查点。
    def clear(self, session_id: str) -> None:
        # 删除目标线程且不影响其他线程。
        self.checkpointer.delete_thread(session_id)
```

内存模式使用单例 `InMemorySaver`；SQLite 模式用 `sqlite3.connect(path, check_same_thread=False)` 创建单例连接并交给 `SqliteSaver`。应用 lifespan 关闭 SQLite 连接。router 的 `session_id` 和 `message` 都限制长度，`DELETE /api/v1/memory/session-a` 返回 `{"data":{"session_id":"session-a","cleared":true}}`。

- [ ] **Step 4: 运行 service 与 API 测试**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_memory_service.py tests/api/test_memory_api.py -v`

Expected: PASS，临时 SQLite 文件位于 pytest 临时目录。

- [ ] **Step 5: 提交记忆 API**

```powershell
git add langchain-learn/api/modules/memory langchain-learn/tests/api/test_memory_service.py langchain-learn/tests/api/test_memory_api.py
git commit -m "feat: add memory and sqlite chat api"
```

### Task 5: Pydantic 结构化输出 API

**Files:**
- Create: `langchain-learn/api/modules/structured/__init__.py`
- Create: `langchain-learn/api/modules/structured/service.py`
- Create: `langchain-learn/api/modules/structured/api.py`
- Create: `langchain-learn/tests/api/test_structured_api.py`

- [ ] **Step 1: 写失败的联系人提取测试**

覆盖 structured service，返回 `ContactInfo(name="张三", email="zhangsan@example.com", phone="13800138000", notes=None)`。断言端点把 Pydantic 对象序列化到 `data`。再让 service 抛 `UpstreamServiceError`，断言返回 502 和稳定错误码 `upstream_service_error`。

- [ ] **Step 2: 运行并确认路由缺失**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_structured_api.py -v`

Expected: FAIL with 404。

- [ ] **Step 3: 实现 Schema 与 `with_structured_output`**

```python
# 定义联系人结构化结果。
class ContactInfo(BaseModel):
    # 保存联系人姓名。
    name: str = Field(description="联系人姓名")
    # 保存可选电子邮箱。
    email: str | None = Field(default=None, description="电子邮箱")
    # 保存可选电话号码。
    phone: str | None = Field(default=None, description="电话号码")
    # 保存其他未归类信息。
    notes: str | None = Field(default=None, description="其他备注")


# 定义结构化提取服务。
class StructuredOutputService:
    # 初始化带原生 Schema 约束的模型。
    def __init__(self, model: BaseChatModel) -> None:
        # 绑定联系人输出 Schema。
        self.structured_model = model.with_structured_output(ContactInfo)

    # 从自然语言提取联系人。
    def extract(self, text: str) -> ContactInfo:
        # 调用结构化模型并取得已校验对象。
        result = self.structured_model.invoke(text)
        # 确认模型适配器返回目标类型。
        if not isinstance(result, ContactInfo):
            # 将异常返回类型映射为安全上游错误。
            raise UpstreamServiceError("模型未返回有效联系人结构")
        # 返回已校验联系人。
        return result
```

- [ ] **Step 4: 运行结构化输出测试**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_structured_api.py -v`

Expected: PASS。

- [ ] **Step 5: 提交结构化输出 API**

```powershell
git add langchain-learn/api/modules/structured langchain-learn/tests/api/test_structured_api.py
git commit -m "feat: add structured output api"
```

### Task 6: 安全本地工具调用 API

**Files:**
- Create: `langchain-learn/api/modules/tools/__init__.py`
- Create: `langchain-learn/api/modules/tools/service.py`
- Create: `langchain-learn/api/modules/tools/api.py`
- Create: `langchain-learn/tests/api/test_tools_service.py`
- Create: `langchain-learn/tests/api/test_tools_api.py`

- [ ] **Step 1: 写计算器安全边界和 Agent 轨迹失败测试**

断言 `safe_calculate("(3 + 5) * 12") == "96"`，并参数化拒绝 `__import__('os')`、`open('x')`、`(1).__class__`、指数过大和超过长度限制的表达式。用 fake agent 返回包含 `AIMessage(content="", tool_calls=[{"name":"safe_calculate","args":{"expression":"3+5"},"id":"call-1","type":"tool_call"}])`、`ToolMessage(content="8", tool_call_id="call-1")` 和 `AIMessage(content="结果是 8")` 的 state，断言 service 只暴露工具名与参数，不暴露 ToolMessage 原文。

- [ ] **Step 2: 运行并确认安全工具函数缺失**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_tools_service.py -v`

Expected: FAIL with missing `safe_calculate`。

- [ ] **Step 3: 实现 AST 白名单计算器、时区工具与轨迹提取**

```python
# 定义允许的二元运算符。
ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


# 安全计算四则运算表达式。
@tool
def safe_calculate(expression: str) -> str:
    """计算只含数字、括号和四则运算符的表达式。"""
    # 拒绝过长输入以限制解析成本。
    if len(expression) > 200:
        # 抛出明确的安全校验错误。
        raise ValueError("表达式过长")
    # 以表达式模式解析抽象语法树。
    tree = ast.parse(expression, mode="eval")
    # 递归计算白名单节点。
    value = evaluate_node(tree.body)
    # 返回便于模型读取的字符串。
    return str(value)


# 读取 Agent 最终答案和调用摘要。
def build_agent_reply(messages: list[BaseMessage]) -> AgentReply:
    # 收集所有模型工具调用。
    traces = [ToolCallTrace(name=call["name"], arguments=call["args"]) for message in messages if isinstance(message, AIMessage) for call in message.tool_calls]
    # 读取最后一条 AI 消息正文。
    answer = next(str(message.content) for message in reversed(messages) if isinstance(message, AIMessage) and message.content)
    # 返回不含内部推理和工具结果的安全响应。
    return AgentReply(answer=answer, tool_calls=traces)
```

`evaluate_node` 只接受 `ast.Constant` 数字、`ast.BinOp` 四则运算和一元正负号；其他节点统一抛 `ValueError`。除零和过大绝对值同样拒绝。`current_time` 只接受 `zoneinfo.available_timezones()` 中的时区。`ToolService` 使用 `create_agent(model, tools=[safe_calculate, current_time])`。

- [ ] **Step 4: 运行工具 service 与 API 测试**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_tools_service.py tests/api/test_tools_api.py -v`

Expected: PASS。

- [ ] **Step 5: 提交工具调用 API**

```powershell
git add langchain-learn/api/modules/tools langchain-learn/tests/api/test_tools_service.py langchain-learn/tests/api/test_tools_api.py
git commit -m "feat: add safe tool calling api"
```

### Task 7: 内置与远程 MCP 调用 API

**Files:**
- Create: `langchain-learn/mcp_servers/__init__.py`
- Create: `langchain-learn/mcp_servers/demo_server.py`
- Create: `langchain-learn/api/modules/mcp/__init__.py`
- Create: `langchain-learn/api/modules/mcp/service.py`
- Create: `langchain-learn/api/modules/mcp/api.py`
- Create: `langchain-learn/tests/api/test_mcp_service.py`
- Create: `langchain-learn/tests/api/test_mcp_api.py`

- [ ] **Step 1: 写连接配置与调用失败测试**

本地模式断言连接配置包含当前 `sys.executable`、`demo_server.py` 绝对路径和 `transport="stdio"`。远程模式断言配置包含 `transport="http"`、URL 和解析后的 headers；远程 URL 缺失时断言 `ConfigurationError`。注入 fake `MultiServerMCPClient` 和 fake agent factory，断言 tools 被传入 Agent，响应工具轨迹正确。

- [ ] **Step 2: 运行并确认 MCP service 缺失**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_mcp_service.py -v`

Expected: FAIL with missing `build_mcp_connections`。

- [ ] **Step 3: 实现可独立运行的 FastMCP Server**

```python
# 导入 FastMCP 服务封装。
from mcp.server.fastmcp import FastMCP

# 创建教学用 MCP 服务。
mcp = FastMCP("LangChain Demo MCP")


# 注册两数相加工具。
@mcp.tool()
def add(a: float, b: float) -> float:
    """返回两个数字的和。"""
    # 返回确定性的加法结果。
    return a + b


# 注册城市说明工具。
@mcp.tool()
def city_note(city: str) -> str:
    """返回教学用的固定城市说明。"""
    # 定义不依赖网络的城市数据。
    notes = {"北京": "中国首都", "上海": "中国重要的国际化城市"}
    # 返回匹配结果或明确的未知提示。
    return notes.get(city, "暂无该城市的演示数据")


# 仅在脚本直接执行时启动 stdio 服务。
if __name__ == "__main__":
    # 以标准输入输出协议运行 MCP。
    mcp.run(transport="stdio")
```

- [ ] **Step 4: 实现 MCP client 和 Agent 调用**

`build_mcp_connections(settings)` 仅生成 `local-demo` 或 `remote-demo` 一个命名连接。`McpService.chat()` 创建 `MultiServerMCPClient`、等待 `get_tools()`、创建 Agent 并 `ainvoke`。捕获连接、发现和调用异常后抛安全 `UpstreamServiceError("MCP 服务调用失败")`，不得拼接原异常。通过共享 `build_agent_reply` 提取最终答案和调用摘要。

- [ ] **Step 5: 运行 MCP 测试**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_mcp_service.py tests/api/test_mcp_api.py -v`

Expected: PASS，且测试不访问网络、不启动真实子进程。

- [ ] **Step 6: 手工验证内置 MCP Server 可启动**

Run: `..\llm\Scripts\python.exe mcp_servers/demo_server.py`

Expected: 进程等待 stdio MCP 输入且无 Python 导入错误；发送 Ctrl+C 后正常退出。

- [ ] **Step 7: 提交 MCP API**

```powershell
git add langchain-learn/mcp_servers langchain-learn/api/modules/mcp langchain-learn/tests/api/test_mcp_service.py langchain-learn/tests/api/test_mcp_api.py
git commit -m "feat: add local and remote mcp api"
```

### Task 8: 本地 `SKILL.md` 加载与调用 API

**Files:**
- Create: `langchain-learn/api/modules/skills/__init__.py`
- Create: `langchain-learn/api/modules/skills/service.py`
- Create: `langchain-learn/api/modules/skills/api.py`
- Create: `langchain-learn/skills/code_explainer/SKILL.md`
- Create: `langchain-learn/skills/text_summarizer/SKILL.md`
- Create: `langchain-learn/tests/api/test_skills_service.py`
- Create: `langchain-learn/tests/api/test_skills_api.py`

- [ ] **Step 1: 写技能白名单与目录穿越失败测试**

在 `tmp_path` 创建两个有效技能和一个缺少 `SKILL.md` 的目录。断言列表只含有效技能且按名称排序。参数化拒绝 `../secret`、`C:\\secret`、`a/b`、空字符串和大写名称。断言不存在的合法 slug 抛 `ResourceNotFoundError`。用 fake model 验证技能正文只进入 system 消息，用户输入只进入 human 消息。

- [ ] **Step 2: 运行并确认 SkillLoader 缺失**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_skills_service.py -v`

Expected: FAIL with missing `SkillLoader`。

- [ ] **Step 3: 实现安全技能加载器**

```python
# 定义本地技能名称白名单格式。
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


# 定义本地技能加载器。
class SkillLoader:
    # 保存固定技能根目录。
    def __init__(self, root: Path) -> None:
        # 解析根目录以便执行边界检查。
        self.root = root.resolve()

    # 加载指定技能正文。
    def load(self, name: str) -> LocalSkill:
        # 拒绝任何不符合白名单的名称。
        if not SKILL_NAME_PATTERN.fullmatch(name):
            # 抛出不回显文件系统信息的业务异常。
            raise InvalidResourceNameError("技能名称不合法")
        # 构造固定层级的技能文件。
        skill_file = (self.root / name / "SKILL.md").resolve()
        # 确认解析后文件仍位于技能根目录。
        if skill_file.parent.parent != self.root:
            # 拒绝越过固定目录边界的路径。
            raise InvalidResourceNameError("技能名称不合法")
        # 确认技能文件真实存在。
        if not skill_file.is_file():
            # 报告稳定的未找到错误。
            raise ResourceNotFoundError("本地技能不存在")
        # 以 UTF-8 读取受信任技能内容。
        instructions = skill_file.read_text(encoding="utf-8")
        # 从首个一级标题生成展示描述。
        description = extract_skill_description(instructions)
        # 返回不包含绝对路径的技能对象。
        return LocalSkill(name=name, description=description, instructions=instructions)
```

列表只遍历根目录直接子目录，不递归。调用 service 通过 `ChatPromptTemplate.from_messages([("system", skill.instructions), ("human", "{input}")]) | model` 执行。API 响应只返回 `name`、`description` 和 `answer`。

- [ ] **Step 4: 增加两个技能文件**

`code_explainer/SKILL.md` 指示模型用“用途、关键步骤、注意事项”三段中文解释用户代码，不执行代码。`text_summarizer/SKILL.md` 指示模型输出一句摘要和最多三个要点，不补充原文没有的事实。两个文件均包含一级标题和简短描述。

- [ ] **Step 5: 运行技能 service 与 API 测试**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_skills_service.py tests/api/test_skills_api.py -v`

Expected: PASS。

- [ ] **Step 6: 提交本地技能 API**

```powershell
git add langchain-learn/api/modules/skills langchain-learn/skills langchain-learn/tests/api/test_skills_service.py langchain-learn/tests/api/test_skills_api.py
git commit -m "feat: add local skill invocation api"
```

### Task 9: 完成依赖注入、错误映射与应用生命周期

**Files:**
- Create: `langchain-learn/api/core/dependencies.py`
- Modify: `langchain-learn/api/main.py`
- Modify: `langchain-learn/api/modules/*/api.py`
- Modify: `langchain-learn/tests/api/conftest.py`
- Modify: `langchain-learn/tests/api/test_foundation.py`

- [ ] **Step 1: 写配置错误和上游错误映射测试**

覆盖任一 service 依赖，让它分别抛 `ConfigurationError("缺少模型配置")` 与 `UpstreamServiceError("模型调用失败")`。断言 HTTP 状态分别为 503/502，响应只包含稳定 code 和安全 message；原始异常、API key 和 headers 不在响应正文。再次运行 Task 1 的 OpenAPI 全路径测试，确认此时所有路径应存在。

- [ ] **Step 2: 运行并确认异常映射或全路径测试失败**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_foundation.py -v`

Expected: 至少一个新增断言 FAIL，且原因是依赖或异常映射尚未统一。

- [ ] **Step 3: 完成依赖工厂和 lifespan**

`get_chat_model()` 复用顶层 `get_settings()` 创建 `ChatOpenAI`。各 `get_*_service()` 只组合配置、模型和 service。用 `functools.lru_cache` 缓存 API 配置、checkpointer、memory service 和技能 loader。应用 lifespan 在退出时关闭 SQLite connection，并清除资源缓存，防止测试和 reload 遗留句柄。

所有 router 使用 `Depends(get_*_service)`，测试通过 `application.dependency_overrides` 替换。service 中非业务异常统一转换为 `UpstreamServiceError`，但不得吞掉 `ConfigurationError`、`ResourceNotFoundError` 和 `InvalidResourceNameError`。

- [ ] **Step 4: 运行全部 API 测试**

Run: `..\llm\Scripts\python.exe -m pytest tests/api -v`

Expected: PASS，且无网络请求、无真实 `.env` 读取、无 SQLite 文件残留在仓库。

- [ ] **Step 5: 提交应用组装**

```powershell
git add langchain-learn/api langchain-learn/tests/api
git commit -m "feat: assemble langchain demo api"
```

### Task 10: 环境示例、忽略规则与使用文档

**Files:**
- Modify: `langchain-learn/.env.example`
- Modify: `.gitignore`
- Modify: `langchain-learn/README.md`
- Create: `langchain-learn/tests/api/test_documentation.py`

- [ ] **Step 1: 写文档契约失败测试**

测试读取 README 和 `.env.example`，断言包含 Uvicorn 启动命令、`/docs`、全部 API 路径、`MEMORY_BACKEND`、`MEMORY_SQLITE_PATH`、`MCP_MODE`、`MCP_REMOTE_URL`，以及 text/SSE、memory/SQLite、local/remote MCP 的示例说明。断言根 `.gitignore` 包含 `langchain-learn/data/*.sqlite*`。

- [ ] **Step 2: 运行并确认文档测试失败**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_documentation.py -v`

Expected: FAIL，列出当前 README 缺少的 API 文档内容。

- [ ] **Step 3: 更新配置示例和 README**

`.env.example` 使用无效占位密钥，不写真实认证信息：

```dotenv
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=https://api.openai.com/v1
MEMORY_BACKEND=memory
MEMORY_SQLITE_PATH=data/memory.sqlite
MCP_MODE=local
MCP_REMOTE_URL=http://127.0.0.1:8001/mcp
MCP_REMOTE_HEADERS={}
```

README 提供：

- `..\llm\Scripts\python.exe -m pip install -r requirements.txt`
- `..\llm\Scripts\python.exe -m uvicorn api.main:app --reload`
- `http://127.0.0.1:8000/docs`
- 每个端点至少一个 PowerShell `Invoke-RestMethod` 示例
- SSE 使用 `curl.exe -N` 的示例
- SQLite 和远程 MCP 的环境变量切换示例
- 内置 `mcp_servers/demo_server.py` 与两个本地技能的说明
- 生产注意事项：内存后端只适合单进程 Demo，SQLite saver 只适合本地轻量使用，远程 MCP 认证头不得提交

- [ ] **Step 4: 运行文档测试并检查格式**

Run: `..\llm\Scripts\python.exe -m pytest tests/api/test_documentation.py -v`

Expected: PASS。

Run: `git diff --check`

Expected: exit 0，无空白错误。

- [ ] **Step 5: 提交文档**

```powershell
git add .gitignore langchain-learn/.env.example langchain-learn/README.md langchain-learn/tests/api/test_documentation.py
git commit -m "docs: explain langchain api demos"
```

### Task 11: 全量回归、注释规则与启动验证

**Files:**
- Modify only if verification reveals a defect in files created by Tasks 1–10.

- [ ] **Step 1: 运行全部 LangChain 项目测试**

Run: `..\llm\Scripts\python.exe -m pytest -q`

Expected: 所有既有 CLI 测试和新增 API 测试 PASS，零失败。

- [ ] **Step 2: 验证应用导入和 OpenAPI**

Run: `..\llm\Scripts\python.exe -c "from api.main import app; schema = app.openapi(); assert len(schema['paths']) == 11; print('openapi-paths=11')"`

Expected: 输出 `openapi-paths=11`，exit 0。

- [ ] **Step 3: 审计 Python 中文独立行注释**

Run: `rg -n "^[[:space:]]*(from |import |class |def |async def |if |for |while |try:|except |with |return |raise |yield |[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=)" api mcp_servers tests/api`

逐项确认每个匹配的有效代码行前一行是准确、简短的中文独立行注释；装饰器对应的注释位于装饰器前，续行不重复注释。若发现遗漏，先补注释再重新运行相关测试。

- [ ] **Step 4: 启动 Uvicorn 并验证健康检查**

Run: `..\llm\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000`

Expected: Uvicorn 成功启动且无导入错误。另一个终端运行 `Invoke-RestMethod http://127.0.0.1:8000/health`，返回 `data.status = "ok"`；随后用 Ctrl+C 停止服务。

- [ ] **Step 5: 检查工作树和差异质量**

Run: `git status --short`

Expected: 只出现计划内尚未提交的修正，理想结果为空。

Run: `git diff --check HEAD~10..HEAD`

Expected: exit 0。

- [ ] **Step 6: 若验证阶段产生修正则提交**

```powershell
git add langchain-learn
git commit -m "test: verify langchain api demos"
```

若没有产生文件修正，则跳过空提交。
