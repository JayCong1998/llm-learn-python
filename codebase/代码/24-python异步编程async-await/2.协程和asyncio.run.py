# 导入异步编程模块
import asyncio


# 使用 async def 定义协程函数
async def say_hello():
    # 输出协程中的问候语
    print("你好，async 和 await")


# 定义管理示例流程的主协程
async def main():
    # 调用异步函数会先得到协程对象
    coroutine = say_hello()
    # 显示协程对象的类型名称
    print(f"调用异步函数得到：{type(coroutine).__name__}")
    # 等待协程运行完成
    await coroutine


# 仅在直接运行本文件时启动事件循环
if __name__ == "__main__":
    # 创建事件循环并运行主协程
    asyncio.run(main())
