# LangChain 学习项目

这是一个使用 LangChain 调用 OpenAI 兼容聊天模型的学习项目，同时提供命令行示例和 FastAPI API Demo。

## 运行

在本目录执行：

```powershell
Copy-Item .env.example .env
# 编辑 .env，填入真实的 OPENAI_API_KEY
..\llm\Scripts\python.exe -m pip install -r requirements.txt
..\llm\Scripts\python.exe main.py
```

`.env` 含有密钥，已被 Git 忽略，不能提交。

## FastAPI Demo

安装依赖并配置 `.env` 后，在本目录启动服务：

```powershell
..\llm\Scripts\python.exe -m uvicorn api.main:app --reload
```

浏览器打开 `http://127.0.0.1:8000/docs`，即可在 Swagger 中直接调用所有示例。健康检查地址为 `http://127.0.0.1:8000/health`。

### API 列表

| API | 演示内容 |
| --- | --- |
| `POST /api/v1/prompts/{template_type}/invoke` | 六种固定提示词模板及 LCEL 调用。 |
| `POST /api/v1/stream/text` | `text/plain` 文本分块。 |
| `POST /api/v1/stream/sse` | 带 `token`、`done`、`error` 事件的 SSE。 |
| `POST /api/v1/memory/chat` | 使用 `session_id` 延续短期消息记忆。 |
| `DELETE /api/v1/memory/{session_id}` | 清理指定会话。 |
| `POST /api/v1/structured/extract` | 将联系人描述提取为 Pydantic JSON。 |
| `POST /api/v1/tools/chat` | 调用安全计算器或时区时间工具。 |
| `POST /api/v1/mcp/chat` | 调用内置或远程 MCP 工具。 |
| `GET /api/v1/skills` | 列出允许调用的本地技能。 |
| `POST /api/v1/skills/{skill_name}/invoke` | 使用本地 `SKILL.md` 处理输入。 |

### PowerShell 调用示例

```powershell
# 提示词模板
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/prompts/text/invoke -ContentType 'application/json' -Body '{"text":"LangChain"}'

# 有消息记忆的聊天
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/memory/chat -ContentType 'application/json' -Body '{"session_id":"demo-1","message":"我叫小明"}'

# 删除指定会话的消息记忆
Invoke-RestMethod -Method Delete -Uri http://127.0.0.1:8000/api/v1/memory/demo-1

# 结构化联系人提取
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/structured/extract -ContentType 'application/json' -Body '{"text":"张三的邮箱是 zhangsan@example.com"}'

# 安全工具调用
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/tools/chat -ContentType 'application/json' -Body '{"question":"计算 (3+5)*12"}'

# 内置或远程 MCP 调用
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/mcp/chat -ContentType 'application/json' -Body '{"question":"计算 3+5"}'

# 查看并调用本地 Skill
Invoke-RestMethod http://127.0.0.1:8000/api/v1/skills
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/skills/code-explainer/invoke -ContentType 'application/json' -Body '{"input":"print(123)"}'
```

纯文本流和 SSE 可用 `curl.exe -N` 观察实时分块：

```powershell
curl.exe -N -X POST http://127.0.0.1:8000/api/v1/stream/text -H "Content-Type: application/json" -d '{"question":"请介绍 LangChain"}'
curl.exe -N -X POST http://127.0.0.1:8000/api/v1/stream/sse -H "Content-Type: application/json" -d '{"question":"请介绍 LangChain"}'
```

### 消息记忆后端

默认 `MEMORY_BACKEND=memory`，适合单进程教学，服务重启后清空。切换为 SQLite：

```dotenv
MEMORY_BACKEND=sqlite
MEMORY_SQLITE_PATH=data/memory.sqlite
```

SQLite 模式需要 `langgraph-checkpoint-sqlite`，适合本地轻量 Demo，不作为多实例生产存储。

### MCP 模式

默认 `MCP_MODE=local`，LangChain MCP adapter 会通过当前 Python 解释器启动 `mcp_servers/demo_server.py`。切换远程 Streamable HTTP MCP：

```dotenv
MCP_MODE=remote
MCP_REMOTE_URL=https://your-mcp-server.example/mcp
MCP_REMOTE_HEADERS={"Authorization":"Bearer replace-me"}
```

远程认证头只能放在本地 `.env`，不能提交到仓库或写入日志。MCP 功能需要安装 `langchain-mcp-adapters` 和 `mcp`。

### 本地 Skill

技能放在 `skills/<安全名称>/SKILL.md`。服务只加载固定技能根目录的一层子目录，拒绝绝对路径、路径分隔符和 `..`。项目包含 `code-explainer` 与 `text-summarizer` 两个示例。

## 流式输出与回调事件

在已安装依赖并配置 `.env` 后，从本目录运行：

```powershell
..\llm\Scripts\python.exe -m streaming.main
```

模型正文会实时写入标准输出；`[回调]` 开头的模型开始、token、结束或错误事件会实时写入标准错误流。终端通常会同时显示两类信息。

## 提示词工程示例

完成上述配置后，在本目录运行：

```powershell
..\llm\Scripts\python.exe -m prompt_engineering.main
```

该命令会使用同一份 OpenAI 兼容模型配置，依次调用下列提示词工程 API：

| API | 演示内容 |
| --- | --- |
| `PromptTemplate` | 使用命名变量创建文本提示词。 |
| `ChatPromptTemplate` | 组合 system 与 human 聊天消息。 |
| `MessagesPlaceholder` | 在聊天模板中插入历史消息。 |
| `FewShotPromptTemplate` | 使用文本格式的固定示例引导输出。 |
| `FewShotChatMessagePromptTemplate` | 使用聊天消息格式的问答示例。 |
| `LengthBasedExampleSelector` | 按提示词长度选择少样本示例。 |

示例源码位于 `prompt_engineering/`。每个构造函数只负责创建一种提示词，`app.py` 负责通过 `prompt | model` 把模板连接到模型并调用。
