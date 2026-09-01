# 导入异步编程模块
import asyncio


# 定义模拟烧水过程的协程
async def prepare_tea():
    # 显示异步操作已经开始
    print("开始烧水")
    # 暂停当前协程并把控制权交还事件循环
    await asyncio.sleep(0.2)
    # 显示异步操作已经完成
    print("水烧好了")
    # 返回烧水结果
    return "热茶"


# 定义准备早餐的主协程
async def make_breakfast():
    # 等待烧水协程完成并接收返回值
    drink = await prepare_tea()
    # 输出早餐和饮品结果
    print(f"早餐准备完成，饮品是{drink}")


# await 只能写在使用 async def 定义的异步函数内部
# 仅在直接运行本文件时启动事件循环
if __name__ == "__main__":
    # 运行准备早餐的主协程
    asyncio.run(make_breakfast())
