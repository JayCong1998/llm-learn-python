# Elasticsearch RAG 检索模块实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 为现有 FastAPI 示例增加使用百炼 embedding 和 Elasticsearch KNN 的 RAG 文档检索接口。

**架构：** `rag/main.py` 负责读取环境变量、生成查询 embedding、执行 ES KNN 检索和映射响应。该模块导出 FastAPI 路由，由根应用挂载；测试以替身隔离百炼与 ES。

**技术栈：** Python、FastAPI、DashScope SDK、Elasticsearch Python client、pytest。

---

## 文件结构

- 创建：`agent-langchain/rag/__init__.py`，声明 RAG 包。
- 创建：`agent-langchain/rag/main.py`，实现 embedding、ES 查询和 HTTP 路由。
- 修改：`agent-langchain/main.py`，挂载 RAG 路由。
- 修改：`agent-langchain/.env.example`，记录不含密钥的 RAG 配置。
- 修改：`agent-langchain/test_main.py`，覆盖模块行为与 HTTP 返回。

### 任务 1：编写 RAG 模块测试

**文件：**
- 修改：`agent-langchain/test_main.py`

- [ ] **步骤 1：编写失败的测试**

```python
def test_create_embedding_uses_dashscope(monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    monkeypatch.setattr(rag_main.TextEmbedding, "call", lambda **kwargs: FakeEmbeddingResponse())
    assert rag_main.create_embedding("测试问题") == [0.1, 0.2]


def test_search_documents_sends_knn_query(monkeypatch):
    monkeypatch.setattr(rag_main, "create_embedding", lambda question: [0.1, 0.2])
    monkeypatch.setattr(rag_main, "get_es_client", lambda: FakeElasticsearchClient())
    assert rag_main.search_documents("测试问题", 3)["results"][0]["text"] == "命中文本"
```

- [ ] **步骤 2：运行测试验证失败**

运行：`pytest agent-langchain/test_main.py -k rag -v`

预期：FAIL，报错无法导入 `rag.main`。

### 任务 2：实现检索模块

**文件：**
- 创建：`agent-langchain/rag/__init__.py`
- 创建：`agent-langchain/rag/main.py`

- [ ] **步骤 1：实现最少功能**

```python
def create_embedding(question: str) -> list[float]:
    response = TextEmbedding.call(model="text-embedding-v4", input=question)
    return response.output["embeddings"][0]["embedding"]


def search_documents(question: str, top_k: int) -> dict[str, object]:
    response = get_es_client().search(
        index=get_index_name(),
        knn={"field": "vector", "query_vector": create_embedding(question), "k": top_k, "num_candidates": top_k * 10},
        source=["text", "metadata"],
    )
    return {"question": question, "results": map_hits(response["hits"]["hits"])}
```

- [ ] **步骤 2：运行模块测试验证通过**

运行：`pytest agent-langchain/test_main.py -k rag -v`

预期：PASS，所有 RAG 测试通过。

### 任务 3：暴露 API 与配置示例

**文件：**
- 修改：`agent-langchain/main.py`
- 修改：`agent-langchain/.env.example`
- 修改：`agent-langchain/test_main.py`

- [ ] **步骤 1：编写失败的路由测试**

```python
def test_rag_search_api_returns_documents(monkeypatch):
    monkeypatch.setattr(rag_main, "search_documents", lambda question, top_k: {"question": question, "results": []})
    response = TestClient(app_main.app).get("/rag/search", params={"question": "测试"})
    assert response.status_code == 200
    assert response.json() == {"question": "测试", "results": []}
```

- [ ] **步骤 2：挂载路由并更新配置模板**

```python
app.include_router(rag_router)
```

在 `.env.example` 增加 `DASHSCOPE_API_KEY`、`ES_URL`、`ES_INDEX_NAME`、`ES_USERNAME`、`ES_PASSWORD` 和 `ES_CA_CERTS` 的无敏感值示例。

- [ ] **步骤 3：运行全部测试**

运行：`pytest agent-langchain/test_main.py -v`

预期：PASS，现有流式聊天、Agent、健康检查和新增 RAG 测试均通过。

### 任务 4：提交和检查

**文件：**
- 创建或修改：上述所有实现与测试文件。

- [ ] **步骤 1：检查格式与工作区**

运行：`git diff --check` 和 `git status --short`

预期：无空白错误；不暂存或修改无关的 pip 日志。

- [ ] **步骤 2：提交功能**

运行：`git add agent-langchain/main.py agent-langchain/.env.example agent-langchain/rag agent-langchain/test_main.py && git commit -m "feat: add elasticsearch rag retrieval"`

预期：仅 RAG 功能相关文件进入提交。
