# 导入异步事件循环运行工具。
import asyncio
# 导入 FastAPI 应用类。
from fastapi import FastAPI
# 导入流式聊天路由。
from streaming_demo.main import router as streaming_router
# 导入工具 Agent 路由。
from tool_agent_demo.main import router as tool_agent_router
# 导入 RAG 检索路由。
from rag.main import router as rag_router
# 导入 Uvicorn 服务运行器。
import uvicorn


# 创建唯一的 FastAPI 应用实例。
app = FastAPI(title="LangChain MiniMax Demos", debug=True)
# 挂载流式聊天路由。
app.include_router(streaming_router)
# 挂载工具 Agent 路由。
app.include_router(tool_agent_router)
# 挂载 RAG 检索路由。
app.include_router(rag_router)


# 提供统一的服务存活检查接口。
@app.get("/health")
async def health_check() -> dict[str, str]:
    # 返回固定的健康状态。
    return {"status": "ok"}


# 在直接执行脚本时启动单进程调试服务。
if __name__ == "__main__":
    # 创建不触发 Uvicorn 内部 asyncio 补丁冲突的服务配置。
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    # 创建采用该配置的 Uvicorn 服务实例。
    server = uvicorn.Server(config)
    # 在当前 PyCharm 调试进程的事件循环中运行服务。
    asyncio.run(server.serve())
