# 导入子进程模块以运行课程脚本
import subprocess
# 导入系统环境模块以固定子进程编码
import os
# 导入系统模块以获取当前 Python 解释器
import sys
# 导入单元测试模块以组织课程测试
import unittest
# 导入路径工具以定位课程目录
from pathlib import Path

# 定位 Python 基础课程根目录
COURSE_ROOT = Path(__file__).resolve().parents[1]
# 定位 async 和 await 课程目录
LESSON_ROOT = COURSE_ROOT / "代码" / "24-python异步编程async-await"


# 定义运行课程脚本的辅助函数
def run_lesson(filename):
    # 复制当前环境变量以免影响测试进程
    child_environment = os.environ.copy()
    # 固定子进程标准输出为 UTF-8 编码
    child_environment["PYTHONIOENCODING"] = "utf-8"
    # 使用当前解释器运行指定课程脚本
    result = subprocess.run([sys.executable, str(LESSON_ROOT / filename)], capture_output=True, text=True, encoding="utf-8", env=child_environment, timeout=10)
    # 确认课程脚本能够正常结束
    assert result.returncode == 0, result.stderr
    # 返回脚本的标准输出供测试断言
    return result.stdout


# 定义 async 和 await 课程测试类
class AsyncAwaitLessonTest(unittest.TestCase):
    # 验证异步场景示例展示串行任务
    def test_why_async_example_runs_successfully(self):
        # 运行异步场景示例
        output = run_lesson("1.为什么需要异步.py")
        # 确认示例输出串行执行提示
        self.assertIn("串行任务执行完成", output)

    # 验证协程入口示例运行协程函数
    def test_coroutine_and_asyncio_run_example_runs_successfully(self):
        # 运行协程入口示例
        output = run_lesson("2.协程和asyncio.run.py")
        # 确认示例输出协程问候
        self.assertIn("你好，async 和 await", output)

    # 验证 await 示例按顺序完成早餐
    def test_await_example_runs_successfully(self):
        # 运行 await 示例
        output = run_lesson("3.await等待异步操作.py")
        # 确认示例先展示准备过程
        self.assertIn("开始烧水", output)
        # 确认示例最终完成早餐
        self.assertIn("早餐准备完成", output)

    # 验证任务示例体现并发优势
    def test_create_task_example_runs_successfully(self):
        # 运行任务并发示例
        output = run_lesson("4.create_task并发执行.py")
        # 确认示例比较并发与串行速度
        self.assertIn("并发执行更快", output)

    # 验证 gather 示例收集全部结果
    def test_gather_example_runs_successfully(self):
        # 运行 gather 示例
        output = run_lesson("5.gather收集任务结果.py")
        # 逐个检查三个任务的结果
        for name in ("文件A", "文件B", "文件C"):
            # 确认当前任务结果已输出
            self.assertIn(name, output)


# 仅在直接运行本文件时启动测试
if __name__ == "__main__":
    # 运行当前模块中的所有测试
    unittest.main()
