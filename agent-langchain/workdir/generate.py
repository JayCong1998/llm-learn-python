# 导入异步队列和异步任务所需的模块。
import asyncio
# 导入随机数工具以生成数量和内容不固定的数据。
from random import choice, randint

# 定义生产函数，模拟大模型逐步生成一个回答片段。
async def produce_piece():
    # 准备可供随机生成回答的数据片段。
    pieces = ["你好，", "这是异步生成器，", "生产者正在输出，", "消费者会逐块读取。"]
    # 等待一段时间以模拟模型生成耗时。
    await asyncio.sleep(0.5)
    # 返回本次随机生成的文本片段。
    return choice(pieces)

# 定义异步生成器，反复调用生产函数并交付生成的数据。
async def fake_model_stream():
    # 随机确定本次回答需要产生的片段数量。
    piece_count = randint(3, 8)
    # 按确定的数量持续生成回答片段。
    for _ in range(piece_count):
        # 调用生产函数获取一段新数据。
        piece = await produce_piece()
        # 将新数据交给读取方，并在此暂停等待下一次读取。
        yield piece
    # 产出结束标记，告知读取方生成已经完成。
    yield None

# 定义读取函数，持续消费异步生成器交付的数据。
async def consume_stream():
    # 打印消费者开始读取的提示。
    print("消费者开始读取：", end="", flush=True)
    # 使用异步迭代逐个读取生成器产出的数据。
    async for piece in fake_model_stream():
        # 遇到结束标记时停止消费。
        if piece is None:
            # 打印生产完成提示并退出读取循环。
            print("\n生产者已结束。")
            return
        # 立即显示当前数据，体现边生成边读取。
        print(piece, end="", flush=True)
    # 当异步生成器自然结束时显示消费完成提示。
    print("\n消费者读取完成。")

# 定义异步程序入口。
async def main():
    # 启动消费者读取异步生成的数据流。
    await consume_stream()

# 运行异步程序入口并等待生产和消费流程完成。
asyncio.run(main())
