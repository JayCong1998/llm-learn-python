# 导入环境变量读取工具。
import os
# 导入文件路径类型。
from pathlib import Path

# 导入 DashScope SDK 配置模块。
import dashscope
# 导入 DashScope 文本向量模型。
from dashscope import TextEmbedding
# 导入 .env 文件加载函数。
from dotenv import load_dotenv
# 导入 FastAPI 路由与查询参数声明工具。
from fastapi import APIRouter, HTTPException, Query
# 导入 LangChain 文档类型。
from langchain_core.documents import Document
# 导入 LangChain Embeddings 抽象基类。
from langchain_core.embeddings import Embeddings
# 导入 LangChain 提示词模板。
from langchain_core.prompts import ChatPromptTemplate
# 导入 LangChain 文本输出解析器。
from langchain_core.output_parsers import StrOutputParser
# 导入 LangChain Elasticsearch 向量库实现。
from langchain_elasticsearch import ElasticsearchStore
# 导入 OpenAI 兼容的 LangChain 聊天模型。
from langchain_openai import ChatOpenAI

# 创建 RAG 检索路由实例。
router = APIRouter(tags=["rag"])


# 加载 agent-langchain 目录中的 .env 文件。
def load_environment(env_file: Path | None = None) -> None:
    # 确定当前模块祖父目录中的默认 .env 路径。
    dotenv_path = env_file or Path(__file__).parents[1] / ".env"
    # 加载配置且保留系统中已存在的同名变量。
    load_dotenv(dotenv_path=dotenv_path, override=False)


# 在创建 LangChain 组件前加载环境变量。
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


# 调用百炼生成指定角色的 1536 维向量。
def create_bailian_embedding(text: str, text_type: str) -> list[float]:
    # 读取百炼 API 密钥。
    api_key = get_required_environment("DASHSCOPE_API_KEY")
    # 配置 DashScope SDK 使用当前 API 密钥。
    dashscope.api_key = api_key
    # 尝试调用指定模型为文本生成向量。
    try:
        # 调用模型并要求与现有 ES 索引一致的 1536 维度。
        response = TextEmbedding.call(model="text-embedding-v4", input=text, dimension=1536, text_type=text_type)
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


# 使用查询角色生成问题向量以兼容原有调用接口。
def create_embedding(question: str) -> list[float]:
    # 调用百炼查询向量生成函数。
    return create_bailian_embedding(question, "query")


# 定义供 LangChain 向量库调用的百炼 Embeddings 适配器。
class BailianEmbeddings(Embeddings):
    # 为检索问题生成查询向量。
    def embed_query(self, text: str) -> list[float]:
        # 调用百炼查询向量生成函数。
        return create_bailian_embedding(text, "query")

    # 为待写入文本生成文档向量。
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # 逐条调用百炼文档向量生成函数。
        return [create_bailian_embedding(text, "document") for text in texts]


# 创建 LangChain 百炼 Embeddings 实例。
def get_embeddings() -> Embeddings:
    # 返回适配现有 1536 维 ES 索引的 Embeddings 实例。
    return BailianEmbeddings()


# 创建连接现有 Elasticsearch 索引的 LangChain 向量库。
def get_vector_store() -> ElasticsearchStore:
    # 读取 Elasticsearch 服务地址。
    es_url = get_required_environment("ES_URL")
    # 读取可选的 Elasticsearch 用户名。
    username = os.getenv("ES_USERNAME")
    # 读取可选的 Elasticsearch 密码。
    password = os.getenv("ES_PASSWORD")
    # 创建 Elasticsearch 客户端的额外参数。
    es_params: dict[str, object] = {}
    # 读取可选的 CA 证书路径。
    ca_certs = os.getenv("ES_CA_CERTS")
    # 在配置证书路径时启用 TLS 证书校验。
    if ca_certs:
        # 写入 Elasticsearch 客户端的证书路径参数。
        es_params["ca_certs"] = ca_certs
    # 返回绑定现有字段映射的 LangChain Elasticsearch 向量库。
    return ElasticsearchStore(index_name=get_index_name(), embedding=get_embeddings(), es_url=es_url, es_user=username, es_password=password, vector_query_field="vector", query_field="text", num_dimensions=1536, es_params=es_params or None)


# 创建标准 LangChain Retriever。
def get_retriever(top_k: int):
    # 获取绑定现有索引的 LangChain 向量库。
    vector_store = get_vector_store()
    # 返回按指定数量执行相似度检索的 Retriever。
    return vector_store.as_retriever(search_kwargs={"k": top_k})


# 创建项目当前配置的 MiniMax LangChain 聊天模型。
def get_llm() -> ChatOpenAI:
    # 读取 MiniMax API 密钥。
    api_key = get_required_environment("MINIMAX_API_KEY")
    # 读取 MiniMax 模型名称并提供默认值。
    model_name = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")
    # 读取 MiniMax 的 OpenAI 兼容 API 端点。
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
    # 返回温度为零的确定性聊天模型。
    return ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url, temperature=0)


# 将 LangChain 文档映射为 API 响应。
def map_documents(documents: list[Document]) -> list[dict[str, object]]:
    # 返回正文与元数据组成的结果列表。
    return [{"text": document.page_content, "metadata": document.metadata} for document in documents]


# 将检索文档拼接为供大模型阅读的上下文。
def format_context(documents: list[Document]) -> str:
    # 在检索无结果时提供明确上下文提示。
    if not documents:
        # 返回空检索结果说明。
        return "未检索到相关资料。"
    # 使用分隔符拼接每条文档正文。
    return "\n\n---\n\n".join(document.page_content for document in documents)


# 使用 LangChain 检索上下文和大模型生成最终答案。
def answer_question(question: str, top_k: int = 5) -> dict[str, object]:
    # 获取 LangChain Retriever。
    retriever = get_retriever(top_k)
    # 检索与用户问题相关的 LangChain 文档。
    documents = retriever.invoke(question)
    # 创建要求基于上下文回答的 LangChain 提示词。
    prompt = ChatPromptTemplate.from_template("""你是知识库问答助手。请只依据下面的检索资料回答问题；资料不足时明确说明无法从资料中确认。\n\n检索资料：\n{context}\n\n用户问题：\n{question}""")
    # 组合提示词、聊天模型和文本解析器形成 LangChain RAG 链。
    rag_chain = prompt | get_llm() | StrOutputParser()
    # 调用 RAG 链生成最终答案。
    answer = rag_chain.invoke({"context": format_context(documents), "question": question})
    # 返回模型答案和可追溯的检索来源。
    return {"answer": answer, "sources": map_documents(documents)}


# 通过 LangChain Retriever 检索相近文档。
def search_documents(question: str, top_k: int = 5) -> dict[str, object]:
    # 获取 LangChain Retriever。
    retriever = get_retriever(top_k)
    # 调用 Retriever 检索相关 LangChain 文档。
    documents = retriever.invoke(question)
    # 返回原始问题和映射后的检索结果。
    return {"question": question, "results": map_documents(documents)}


# 提供基于 LangChain Retriever 的 RAG 文档检索接口。
@router.get("/rag/search")
# 声明 RAG 检索接口的查询参数与响应结构。
def rag_search(question: str = Query(min_length=1, description="需要检索的文本"), top_k: int = Query(default=5, ge=1, le=20)) -> dict[str, object]:
    # 尝试执行 LangChain 文档检索。
    try:
        # 执行完整 RAG 问答并返回答案与来源。
        result = answer_question(question, top_k)
        # 返回原始问题和 RAG 问答结果。
        return {"question": question, **result}
    # 保留环境变量缺失的明确配置提示。
    except RuntimeError as error:
        # 在配置缺失时维持默认的服务器错误响应。
        if str(error).startswith("请设置 "):
            # 继续抛出原始配置错误。
            raise
        # 返回向量检索服务不可用的统一提示。
        raise HTTPException(status_code=502, detail="向量检索服务暂时不可用，请稍后重试。") from error
    # 捕获其他未预期的检索异常。
    except Exception as error:
        # 返回向量检索服务不可用的统一提示。
        raise HTTPException(status_code=502, detail="向量检索服务暂时不可用，请稍后重试。") from error
