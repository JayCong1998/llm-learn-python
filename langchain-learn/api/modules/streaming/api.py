"""纯文本和 SSE 流式 HTTP 路由。"""

# 导入异步取消异常类型。
import asyncio
# 导入异步迭代器类型。
from collections.abc import AsyncIterator
# 导入 JSON 编码工具。
import json

# 导入 FastAPI 路由和依赖工具。
from fastapi import APIRouter, Depends
# 导入流式响应类型。
from fastapi.responses import StreamingResponse

# 导入流式 service 依赖。
from api.core.dependencies import get_streaming_service
# 导入通用问题请求。
from api.core.schemas import QuestionRequest
# 导入流式 service 类型。
from api.modules.streaming.service import StreamingService

# 创建流式模块路由。
router = APIRouter(prefix="/api/v1/stream", tags=["streaming"])


# 过滤 service 可能返回的空文本。
async def _non_empty_tokens(
    service: StreamingService,
    question: str,
) -> AsyncIterator[str]:
    # 遍历 service 的所有文本分块。
    async for token in service.stream_tokens(question):
        # 跳过空字符串分块。
        if token:
            # 产出有效文本。
            yield token


# 将数据编码为标准 SSE 帧。
def encode_sse(event: str, data: dict[str, object]) -> str:
    # 以 JSON 编码事件数据并保留中文。
    payload = json.dumps(data, ensure_ascii=False)
    # 返回包含事件名和数据行的 SSE 文本。
    return f"event: {event}\ndata: {payload}\n\n"


# 将模型文本适配为 SSE 事件流。
async def _sse_events(
    service: StreamingService,
    question: str,
) -> AsyncIterator[str]:
    # 尝试消费模型分块。
    try:
        # 遍历所有非空 token。
        async for token in _non_empty_tokens(service, question):
            # 产出命名 token 事件。
            yield encode_sse("token", {"token": token})
        # 产出正常完成事件。
        yield encode_sse("done", {"status": "completed"})
    # 让客户端取消信号正常向上传播。
    except asyncio.CancelledError:
        # 重新抛出取消异常以停止上游消费。
        raise
    # 捕获其他模型流式异常。
    except Exception:
        # 产出不泄露内部详情的错误事件。
        yield encode_sse("error", {"message": "模型流式调用失败"})


# 注册纯文本分块端点。
@router.post("/text")
def stream_plain_text(
    payload: QuestionRequest,
    service: StreamingService = Depends(get_streaming_service),
) -> StreamingResponse:
    # 返回不缓冲的纯文本响应。
    return StreamingResponse(
        _non_empty_tokens(service, payload.question),
        media_type="text/plain",
    )


# 注册命名 SSE 事件端点。
@router.post("/sse")
def stream_server_sent_events(
    payload: QuestionRequest,
    service: StreamingService = Depends(get_streaming_service),
) -> StreamingResponse:
    # 返回服务端事件流响应。
    return StreamingResponse(
        _sse_events(service, payload.question),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
