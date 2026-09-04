# Elasticsearch RAG 检索模块设计

## 目标

为 `agent-langchain` 新增一个可通过 HTTP 调用的检索模块：接收用户问题，使用百炼 `text-embedding-v4` 生成查询向量，并从 Elasticsearch 索引 `know-engine-vector` 返回最相近的文本分块。

## 范围

- 新增 `rag` Python 包和 `/rag/search` GET 接口。
- 从环境变量读取百炼和 Elasticsearch 配置。
- 查询向量写入 ES `knn` 检索请求的 `vector` 字段。
- 返回每条命中的 `text`、`metadata` 和 `_score`。
- 为环境变量缺失、向量生成和 ES 请求构造添加单元测试。

本次不包含基于检索结果调用大模型生成答案、文档写入或删除、访问权限过滤，以及多轮对话记忆。

## 数据与接口

索引 `know-engine-vector` 的 `vector` 字段是使用余弦相似度的 1536 维 `dense_vector`；`text` 保存分块正文，`metadata` 保存来源信息。

接口为 `GET /rag/search`，参数包括非空 `question` 与默认值为 5 的 `top_k`。成功时返回原始问题和结果列表；每个结果包含 `text`、`metadata` 与 `score`。

## 实现方案

使用 DashScope Python SDK 的 `TextEmbedding.call` 调用 `text-embedding-v4`，取得单个查询的 embedding。使用官方 Elasticsearch Python 客户端发起 `knn` 查询，检索索引中的 `vector` 字段，并只提取 `text` 与 `metadata`。

连接配置使用 `DASHSCOPE_API_KEY`、`ES_URL`、可选的 `ES_USERNAME`、`ES_PASSWORD` 和 `ES_CA_CERTS`。索引名称固定为现有的 `know-engine-vector`，但可以通过 `ES_INDEX_NAME` 覆盖，方便不同环境复用。所有密钥只保存在 `.env` 或部署环境中。

## 错误处理

缺少百炼密钥或 ES 地址时抛出明确的运行时错误。百炼调用失败或未返回 embedding 时转换为运行时错误；ES 客户端异常由 FastAPI 转换为 HTTP 502，避免将底层细节直接暴露给调用方。

## 验证

测试通过替身替换百炼 embedding 调用和 ES 客户端，不连接真实服务。覆盖 embedding 参数、`knn` 请求字段、结果映射、配置缺失和 API 成功响应。最后运行 `pytest` 验证整个示例应用未回归。
