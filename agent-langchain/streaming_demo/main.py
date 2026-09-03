# 导入 JSON 编码工具。
import json
# 导入环境变量读取工具。
import os
# 导入异步迭代类型标注。
from collections.abc import AsyncIterator
# 导入文件路径类型。
from pathlib import Path

# 导入 .env 文件加载函数。
from dotenv import load_dotenv
# 导入 FastAPI 路由与查询参数声明工具。
from fastapi import APIRouter, Query
# 导入 LangChain 人类消息类型。
from langchain_core.messages import HumanMessage
# 导入 OpenAI 的 LangChain 聊天模型实现。
from langchain_openai import ChatOpenAI
# 导入 FastAPI 流式响应类。
from starlette.responses import StreamingResponse

# 创建流式聊天路由实例。
router = APIRouter(tags=["streaming"])


# 加载项目根目录中的 .env 文件。
def load_environment(env_file: Path | None = None) -> None:
    # 确定演示目录父级中的默认 .env 路径。
    dotenv_path = env_file or Path(__file__).parents[1] / ".env"
    # 加载配置且保留系统中已存在的同名变量。
    load_dotenv(dotenv_path=dotenv_path, override=False)


# 在创建模型前加载环境变量。
load_environment()


# 创建配置完成的 MiniMax 聊天模型。
def get_llm() -> ChatOpenAI:
    # 读取 MiniMax API 密钥。
    api_key = os.getenv("MINIMAX_API_KEY")
    # 在未配置密钥时阻止应用发送无效请求。
    if not api_key:
        # 提示调用方配置必需的 MiniMax 密钥。
        raise RuntimeError("请设置 MINIMAX_API_KEY 环境变量。")
    # 读取 MiniMax 模型名称并提供默认值。
    model_name = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")
    # 读取中国大陆的 OpenAI 兼容 API 端点。
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
    # 返回支持异步流式调用的聊天模型。
    return ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url, temperature=0)


# 将 LangChain 文本块转换为 SSE 数据帧。
def format_sse(content: str) -> str:
    # 生成包含文本内容的 JSON 数据帧。
    payload = json.dumps({"content": content}, ensure_ascii=False, separators=(",", ":"))
    # 返回符合 SSE 协议的事件文本。
    return f"data: {payload}\n\n"


# 从模型流中逐块生成 SSE 数据。
async def stream_chat(message: str) -> AsyncIterator[str]:
    # 获取配置完成的 LangChain 模型。
    llm = get_llm()
    # 以人类消息调用模型的异步流式接口。
    async for chunk in llm.astream([HumanMessage(content=message)]):
        # 提取当前响应块的文本内容。
        content = chunk.content
        # 忽略工具调用等非字符串响应块。
        if not isinstance(content, str) or not content:
            # 跳过不包含文本的响应块。
            continue
        # 输出当前文本块的 SSE 数据帧。
        yield format_sse(content)


# 提供 LangChain 大模型的 GET SSE 流式聊天接口。
@router.get("/chat/stream")
async def chat_stream(message: str = Query(min_length=1, description="发送给大模型的文本")) -> StreamingResponse:
    # 返回采用 SSE 媒体类型的模型文本流。
    return StreamingResponse(stream_chat(message), media_type="text/event-stream")
