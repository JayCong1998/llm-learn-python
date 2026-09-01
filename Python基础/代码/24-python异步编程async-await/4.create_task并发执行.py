# 导入异步编程模块
import asyncio
# 导入时间模块以比较执行耗时
import time


# 定义模拟获取数据的协程
async def fetch_data(name, delay):
    # 显示当前请求已经开始
    print(f"开始获取{name}")
    # 模拟等待外部数据的过程
    await asyncio.sleep(delay)
    # 显示当前请求已经完成
    print(f"完成获取{name}")


# 定义串行执行示例
async def run_sequentially():
    # 记录串行执行开始时间
    start_time = time.perf_counter()
    # 等待第一个任务完成
    await fetch_data("用户信息", 0.2)
    # 等待第二个任务完成
    await fetch_data("订单信息", 0.2)
    # 返回串行执行耗时
    return time.perf_counter() - start_time


# 定义并发执行示例
async def run_concurrently():
    # 记录并发执行开始时间
    start_time = time.perf_counter()
    # 创建第一个并发任务
    user_task = asyncio.create_task(fetch_data("用户信息", 0.2))
    # 创建第二个并发任务
    order_task = asyncio.create_task(fetch_data("订单信息", 0.2))
    # 等待第一个任务完成
    await user_task
    # 等待第二个任务完成
    await order_task
    # 返回并发执行耗时
    return time.perf_counter() - start_time


# 定义比较两种执行方式的主协程
async def main():
    # 获取串行执行耗时
    sequential_time = await run_sequentially()
    # 获取并发执行耗时
    concurrent_time = await run_concurrently()
    # 输出串行执行耗时
    print(f"串行执行耗时：{sequential_time:.2f} 秒")
    # 输出并发执行耗时
    print(f"并发执行耗时：{concurrent_time:.2f} 秒")
    # 根据实测耗时输出比较结果
    if concurrent_time < sequential_time:
        # 说明并发任务减少了总等待时间
        print("并发执行更快，因为两个任务的等待时间发生了重叠。")


# 仅在直接运行本文件时启动事件循环
if __name__ == "__main__":
    # 运行比较执行方式的主协程
    asyncio.run(main())
