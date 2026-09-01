# Python async/await 入门课程实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增第 24 课，通过五个独立、可运行的示例讲清 `async`、`await`、任务并发与结果汇总。

**Architecture:** 每个 Python 文件只讲一个知识点，并通过标准输出展示运行过程。一个 pytest 文件以子进程运行所有示例，验证脚本能够成功退出且输出包含对应知识点的关键结果。

**Tech Stack:** Python 标准库 `asyncio`、`time`、`unittest`

---

## 文件结构

- `Python基础/代码/24-python异步编程async-await/1.为什么需要异步.py`：串行等待示例与适用场景说明。
- `Python基础/代码/24-python异步编程async-await/2.协程和asyncio.run.py`：协程定义及程序入口。
- `Python基础/代码/24-python异步编程async-await/3.await等待异步操作.py`：协程间的顺序等待。
- `Python基础/代码/24-python异步编程async-await/4.create_task并发执行.py`：创建任务并对比串行、并发耗时。
- `Python基础/代码/24-python异步编程async-await/5.gather收集任务结果.py`：并发收集多个返回值。
- `Python基础/tests/test_async_await_lesson.py`：使用标准库 `unittest` 以黑盒方式验证五个脚本。

### Task 1: 建立课程行为测试

**Files:**
- Create: `Python基础/tests/test_async_await_lesson.py`

- [ ] **Step 1: 写入失败测试**

测试通过 `subprocess.run()` 执行五个预期脚本，分别断言退出码为 0，并检查以下关键输出：串行任务、协程问候、准备与完成、并发更快、三个任务结果。

- [ ] **Step 2: 验证测试因课程文件缺失而失败**

Run: `python "Python基础/tests/test_async_await_lesson.py" -v`

Expected: FAIL，错误指出第 24 课脚本不存在。

- [ ] **Step 3: 提交测试**

Run: `git add -- "Python基础/tests/test_async_await_lesson.py" && git commit -m "test: define async await lesson behavior"`

### Task 2: 介绍异步场景与协程入口

**Files:**
- Create: `Python基础/代码/24-python异步编程async-await/1.为什么需要异步.py`
- Create: `Python基础/代码/24-python异步编程async-await/2.协程和asyncio.run.py`

- [ ] **Step 1: 实现串行等待示例**

定义 `handle_task(name, delay)`，使用 `time.sleep()` 模拟两个依次执行的 I/O 等待任务，并打印开始、结束和总耗时。注释说明异步适用于网络、文件、数据库等等待较多的操作，不等同于多线程，也不适合替代 CPU 密集计算。

- [ ] **Step 2: 实现最小协程示例**

定义 `async def say_hello()` 并在其中打印问候；定义 `main()`，先创建协程对象并显示其类型，再 `await` 它；通过 `asyncio.run(main())` 启动事件循环。

- [ ] **Step 3: 运行针对两个脚本的测试**

Run: `python "Python基础/tests/test_async_await_lesson.py" -v`

Expected: 前两个用例 PASS，其余用例仍因脚本缺失而 FAIL。

- [ ] **Step 4: 提交两个入门示例**

Run: `git add -- "Python基础/代码/24-python异步编程async-await" && git commit -m "feat: introduce Python coroutines"`

### Task 3: 演示 await 顺序协作

**Files:**
- Create: `Python基础/代码/24-python异步编程async-await/3.await等待异步操作.py`

- [ ] **Step 1: 实现 await 示例**

定义 `prepare_tea()` 与 `make_breakfast()` 两个协程。前者使用 `await asyncio.sleep()` 模拟等待并返回结果；后者等待前者完成后再打印早餐完成，说明 `await` 只能出现在异步函数中，并会把控制权交还事件循环。

- [ ] **Step 2: 运行测试**

Run: `python "Python基础/tests/test_async_await_lesson.py" -v`

Expected: 前三个用例 PASS，后两个用例仍因脚本缺失而 FAIL。

- [ ] **Step 3: 提交 await 示例**

Run: `git add -- "Python基础/代码/24-python异步编程async-await/3.await等待异步操作.py" && git commit -m "feat: explain awaiting coroutines"`

### Task 4: 演示 create_task 并发执行

**Files:**
- Create: `Python基础/代码/24-python异步编程async-await/4.create_task并发执行.py`

- [ ] **Step 1: 实现串行与并发对比**

定义 `fetch_data(name, delay)`；在 `run_sequentially()` 中依次 `await` 两次，在 `run_concurrently()` 中先用 `asyncio.create_task()` 创建两个任务，再等待两个任务；使用 `time.perf_counter()` 分别计时并打印“并发执行更快”。

- [ ] **Step 2: 运行测试**

Run: `python "Python基础/tests/test_async_await_lesson.py" -v`

Expected: 前四个用例 PASS，最后一个用例仍因脚本缺失而 FAIL。

- [ ] **Step 3: 提交并发示例**

Run: `git add -- "Python基础/代码/24-python异步编程async-await/4.create_task并发执行.py" && git commit -m "feat: demonstrate concurrent asyncio tasks"`

### Task 5: 演示 gather 汇总结果并完成验证

**Files:**
- Create: `Python基础/代码/24-python异步编程async-await/5.gather收集任务结果.py`

- [ ] **Step 1: 实现结果汇总示例**

定义 `download_file(name, delay)`，等待后返回完成信息；在 `main()` 中把三个协程传给 `asyncio.gather()`，遍历结果并打印，确保所有任务均被等待完成。

- [ ] **Step 2: 运行完整行为测试**

Run: `python "Python基础/tests/test_async_await_lesson.py" -v`

Expected: 5 passed。

- [ ] **Step 3: 逐个编译课程脚本**

Run: `python -m compileall -q "Python基础/代码/24-python异步编程async-await"`

Expected: 退出码 0，无语法错误。

- [ ] **Step 4: 检查仓库注释规则**

逐行检查六个新增 Python 文件，确认每条有效代码语句前都有准确、简短的中文独立行注释；空行、注释和文档字符串不重复注释。

- [ ] **Step 5: 提交最终示例**

Run: `git add -- "Python基础/代码/24-python异步编程async-await/5.gather收集任务结果.py" && git commit -m "feat: explain gathering async results"`
