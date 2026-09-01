# 导入异步编程模块
import asyncio


# 定义模拟下载文件的协程
async def download_file(name, delay):
    # 显示当前下载任务已经开始
    print(f"开始下载{name}")
    # 模拟等待文件数据的过程
    await asyncio.sleep(delay)
    # 返回当前下载任务的结果
    return f"{name}下载完成"


# 定义汇总多个结果的主协程
async def main():
    # 并发运行三个协程并按传入顺序收集返回值
    results = await asyncio.gather(download_file("文件A", 0.3), download_file("文件B", 0.2), download_file("文件C", 0.1))
    # 遍历所有任务的返回值
    for result in results:
        # 输出当前任务的结果
        print(result)


# 仅在直接运行本文件时启动事件循环
if __name__ == "__main__":
    # 运行汇总结果的主协程
    asyncio.run(main())
