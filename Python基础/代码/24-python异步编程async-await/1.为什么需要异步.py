# 导入时间模块以模拟同步等待
import time

# 异步适合网络请求、文件读写和数据库访问等等待较多的任务
# 异步不等于多线程，也不适合直接替代计算量很大的任务


# 定义一个使用同步等待的任务
def handle_task(name, delay):
    # 显示当前任务已经开始
    print(f"{name}开始")
    # 阻塞当前程序以模拟等待外部数据
    time.sleep(delay)
    # 显示当前任务已经结束
    print(f"{name}结束")


# 定义程序入口函数
def main():
    # 记录串行任务开始时间
    start_time = time.perf_counter()
    # 先执行第一个同步任务
    handle_task("读取文件", 0.2)
    # 再执行第二个同步任务
    handle_task("请求接口", 0.2)
    # 计算两个任务的总耗时
    elapsed_time = time.perf_counter() - start_time
    # 输出串行执行的结果
    print(f"串行任务执行完成，共耗时 {elapsed_time:.2f} 秒")
    # 提示后续可以利用异步减少等待时间
    print("如果任务主要在等待，可以使用异步让等待时间重叠。")


# 仅在直接运行本文件时执行示例
if __name__ == "__main__":
    # 调用程序入口函数
    main()
