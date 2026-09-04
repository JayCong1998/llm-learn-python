# 导入环境变量读取工具。
import os
# 导入文件路径类型。
from pathlib import Path

# 导入 DashScope SDK 配置模块。
import dashscope
# 导入 DashScope 文本向量模型。
from dashscope import TextEmbedding
# 导入 Elasticsearch 官方客户端。
from elasticsearch import Elasticsearch, TransportError
# 导入 .env 文件加载函数。
from dotenv import load_dotenv
# 导入 FastAPI 路由与查询参数声明工具。
from fastapi import APIRouter, HTTPException, Query

# 创建 RAG 检索路由实例。
router = APIRouter(tags=["rag"])


# 加载 agent-langchain 目录中的 .env 文件。
def load_environment(env_file: Path | None = None) -> None:
    # 确定当前模块祖父目录中的默认 .env 路径。
    dotenv_path = env_file or Path(__file__).parents[1] / ".env"
    # 加载配置且保留系统中已存在的同名变量。
    load_dotenv(dotenv_path=dotenv_path, override=False)


# 在创建客户端前加载环境变量。
load_environment()


# 读取必需环境变量并在缺失时提示调用方。
def get_required_environment(name: str) -> str:
    # 读取指定名称的环境变量。
    value = os.getenv(name)
    # 在变量缺失或为空时中止无效请求。
    if not value:
        # 提供明确的配置缺失提示。
        raise RuntimeError(f"请设置 {name} 环境变量。")
    # 返回已验证的环境变量值。
    return value


# 获取可被环境变量覆盖的 Elasticsearch 索引名称。
def get_index_name() -> str:
    # 返回配置索引名或默认知识库索引名。
    return os.getenv("ES_INDEX_NAME", "know-engine-vector")


# 创建已配置的 Elasticsearch 官方客户端。
def get_es_client() -> Elasticsearch:
    # 读取 Elasticsearch 服务地址。
    es_url = get_required_environment("ES_URL")
    # 创建 Elasticsearch 客户端初始化参数。
    client_options: dict[str, object] = {}
    # 读取可选的用户名配置。
    username = os.getenv("ES_USERNAME")
    # 读取可选的密码配置。
    password = os.getenv("ES_PASSWORD")
    # 在用户名和密码都存在时启用基本认证。
    if username and password:
        # 写入 Elasticsearch 客户端的基本认证参数。
        client_options["basic_auth"] = (username, password)
    # 读取可选的 CA 证书路径。
    ca_certs = os.getenv("ES_CA_CERTS")
    # 在配置证书路径时启用 TLS 证书校验。
    if ca_certs:
        # 写入 Elasticsearch 客户端的证书路径参数。
        client_options["ca_certs"] = ca_certs
    # 返回连接到配置服务地址的客户端。
    return Elasticsearch(es_url, **client_options)


# 使用百炼文本向量模型生成问题向量。
def create_embedding(question: str) -> list[float]:
    # 读取百炼 API 密钥。
    api_key = get_required_environment("DASHSCOPE_API_KEY")
    # 配置 DashScope SDK 使用当前 API 密钥。
    dashscope.api_key = api_key
    # 尝试调用指定模型为问题生成向量。
    try:
        # 调用指定模型为问题生成向量。
        response = TextEmbedding.call(model="text-embedding-v4", input=question, dimension=1536, text_type="query")
        # 读取首个 embedding 向量。
        embedding = response.output["embeddings"][0]["embedding"]
        # 校验模型返回的向量维度符合索引配置。
        if not isinstance(embedding, list) or len(embedding) != 1536:
            # 提供 embedding 维度不匹配的明确提示。
            raise RuntimeError("百炼 embedding 维度必须为 1536。")
        # 返回经维度校验的 embedding 向量。
        return embedding
    # 保留 embedding 维度校验产生的明确错误。
    except RuntimeError:
        # 继续抛出原始 embedding 校验错误。
        raise
    # 将百炼调用失败转换为明确的运行时错误。
    except Exception as error:
        # 提供无法生成 embedding 的明确提示。
        raise RuntimeError("百炼 embedding 生成失败。") from error


# 将 Elasticsearch 命中映射为 API 响应文档。
def map_hits(hits: list[dict[str, object]]) -> list[dict[str, object]]:
    # 创建映射后的文档列表。
    results: list[dict[str, object]] = []
    # 逐一处理 Elasticsearch 命中。
    for hit in hits:
        # 读取命中的文档来源。
        source = hit.get("_source", {})
        # 将命中内容、元数据和分数加入响应。
        results.append({"text": source.get("text", ""), "metadata": source.get("metadata", {}), "score": hit.get("_score")})
    # 返回全部映射后的文档。
    return results


# 生成查询向量并执行 Elasticsearch KNN 检索。
def search_documents(question: str, top_k: int = 5) -> dict[str, object]:
    # 生成问题对应的查询向量。
    query_vector = create_embedding(question)
    # 获取已配置的 Elasticsearch 客户端。
    client = get_es_client()
    # 将检索服务异常转换为明确的运行时错误。
    try:
        # 发起针对向量字段的 KNN 检索。
        response = client.search(index=get_index_name(), knn={"field": "vector", "query_vector": query_vector, "k": top_k, "num_candidates": top_k * 10}, source=["text", "metadata"])
    # 捕获 Elasticsearch 客户端请求异常。
    except Exception as error:
        # 提供 KNN 检索失败的明确提示。
        raise RuntimeError("Elasticsearch KNN 检索失败。") from error
    # 读取 Elasticsearch 命中列表。
    hits = response.get("hits", {}).get("hits", [])
    # 返回原始问题和映射后的检索结果。
    return {"question": question, "results": map_hits(hits)}


# 提供基于问题文本的 RAG 文档检索接口。
@router.get("/rag/search")
# 声明 RAG 检索接口的查询参数与响应结构。
def rag_search(question: str = Query(min_length=1, description="需要检索的文本"), top_k: int = Query(default=5, ge=1, le=20)) -> dict[str, object]:
    # 尝试执行文档检索。
    try:
        # 执行文档检索并返回结果。
        return search_documents(question, top_k)
    # 保留环境变量缺失的明确配置提示。
    except RuntimeError as error:
        # 在配置缺失时维持默认的服务器错误响应。
        if str(error).startswith("请设置 "):
            # 继续抛出原始配置错误。
            raise
        # 返回向量检索服务不可用的统一提示。
        raise HTTPException(status_code=502, detail="向量检索服务暂时不可用，请稍后重试。") from error
    # 捕获 Elasticsearch 传输层异常。
    except TransportError as error:
        # 返回向量检索服务不可用的统一提示。
        raise HTTPException(status_code=502, detail="向量检索服务暂时不可用，请稍后重试。") from error
    # 捕获其他未预期的检索异常。
    except Exception as error:
        # 返回向量检索服务不可用的统一提示。
        raise HTTPException(status_code=502, detail="向量检索服务暂时不可用，请稍后重试。") from error
