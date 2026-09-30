# 导入异步等待与同步计时工具。
import asyncio
from threading import current_thread
from time import perf_counter, sleep

# 导入 FastAPI 路由定义工具。
from fastapi import APIRouter

# 创建异步编程教学路由。
router = APIRouter()


# 提供最基础的异步接口作为学习入口。
@router.get("/async-demo/hello", tags=["async-demo"])
# 使用 async def 定义可由 FastAPI 异步调用的接口。
async def async_hello() -> dict[str, str]:
    # 异步等待两秒，等待时事件循环可以处理其他任务。
    await asyncio.sleep(2)
    # 等待结束后返回结果。
    return {"message": "你好，这是第一个异步接口"}


# 提供异步等待对照接口。
@router.get("/async-demo/async-wait", tags=["async-demo"])
# 用异步等待模拟两秒的 I/O 等待。
async def async_wait() -> dict[str, float | str]:
    # 记录当前请求开始处理的时间。
    started_at = perf_counter()
    # 异步等待时允许事件循环处理其他请求。
    await asyncio.sleep(2)
    # 返回等待说明与本次请求耗时。
    return {"kind": "异步等待", "seconds": round(perf_counter() - started_at, 3)}


# 提供同步阻塞对照接口。
@router.get("/async-demo/blocking-wait", tags=["async-demo"])
# 用同步等待演示阻塞事件循环的效果。
async def blocking_wait() -> dict[str, float | str]:
    # 记录当前请求开始处理的时间。
    started_at = perf_counter()
    # 同步休眠会占住事件循环所在的线程两秒。
    sleep(2)
    # 返回等待说明与本次请求耗时。
    return {"kind": "同步阻塞等待", "seconds": round(perf_counter() - started_at, 3)}


# 提供普通 def 路由的线程池对照接口。
@router.get("/async-demo/sync-route", tags=["async-demo"])
# 用普通 def 声明由 FastAPI 在线程池中调用的路由。
def sync_route() -> dict[str, float | str]:
    # 记录当前请求开始处理的时间。
    started_at = perf_counter()
    # 在当前工作线程中同步等待两秒。
    sleep(2)
    # 返回线程信息和同步等待耗时。
    return {
        "kind": "普通 def 路由",
        "thread": current_thread().name,
        "seconds": round(perf_counter() - started_at, 3),
    }




# 模拟一个异步的下游服务调用。
async def fetch_user_name() -> str:
    # 异步等待一秒模拟网络请求耗时。
    await asyncio.sleep(1)
    # 返回模拟的下游服务响应。
    return "小明"


# 演示使用 await 获取另一个异步函数的返回值。
@router.get("/async-demo/await-call", tags=["async-demo"])
# 定义等待下游异步服务的 API。
async def await_call() -> dict[str, str]:
    # await等待异步函数执行，并获取结果。 没有await，fetch_user_name函数是不会执行的
    user_name = await fetch_user_name()
    return {"message": f"你好，{user_name}"}


# 模拟获取订单信息的异步服务。
async def fetch_order_count() -> int:
    # 异步等待一秒模拟订单服务的网络等待。
    await asyncio.sleep(1)
    # 返回模拟的订单数量。
    return 3


# 演示并发等待两个独立的异步服务。
@router.get("/async-demo/gather", tags=["async-demo"])
# 同时等待用户服务和订单服务后返回结果。
async def gather_calls() -> dict[str, float | str | int]:
    # 记录并发调用的开始时刻。
    started_at = perf_counter()
    # 同时启动两个异步调用并等待两者都完成。
    user_name, order_count = await asyncio.gather(fetch_user_name(), fetch_order_count())
    # 返回两个服务的结果以及总耗时。
    return {
        "user_name": user_name,
        "order_count": order_count,
        "seconds": round(perf_counter() - started_at, 3),
    }
