# 导入 FastAPI 请求路由定义。
from fastapi import APIRouter
# 导入请求体参数解析工具。
from fastapi import Body
# 导入流式 HTTP 响应类型以逐段发送 Agent 输出。
from fastapi.responses import StreamingResponse
# 导入 JSON 序列化函数以编码结构化事件。
import json
# 导入执行 Agent 循环的调用函数。
from agents.react_agent import call
# 导入本地编程工具集合。
from agents.coding_tools import coding_tools

# 导入本地编程工具集合。
from agents.tools import weather_time_tools


# 创建聊天 API 路由。
router = APIRouter()

@router.post("/agent/chat")
# 从请求体读取消息并为本次请求创建带编程工具的 Agent。
def chat(request: str= Body(...)) -> str:
    # 使用本地编程工具处理用户提出的项目任务。
    return call(request, tools=coding_tools)

@router.post("/agent/stream")
# 从请求体读取消息并为本次请求创建带天气时间工具的 Agent。
def chat_stream(request: str = Body(...)) -> StreamingResponse:
    # 延迟导入流式生成器以便该路由明确使用文本分块响应。
    from agents.react_agent import stream

    # 将结构化事件逐条编码为服务端发送事件格式。
    def event_stream():
        # 遍历 Agent 事件并序列化为 UTF-8 JSON 数据。
        for event in stream(request, tools=weather_time_tools):
            # 按 SSE 约定输出事件名和 JSON 数据行。
            yield f"event: {event.type.value}\ndata: {json.dumps(event.model_dump(mode='json'), ensure_ascii=False)}\n\n"

    # 返回服务端发送事件响应。
    return StreamingResponse(event_stream(), media_type="text/event-stream; charset=utf-8")
