# 普通函数和异步函数

最直接的区别是：普通 def 调用时会直接执行函数；
async def 调用时会先得到一个“等待执行的对象”（协程），需要用 await 才会执行它。

```
def normal():
    return "普通函数的结果"

async def async_func():
    return "异步函数的结果"

normal_result = normal()        # 立刻执行，得到字符串
async_result = async_func()     # 得到协程对象，还没有执行函数体
```
await 表示“这里需要等结果，但等待期间可以让出执行机会，让其他异步任务先运行”。

# 案例1

这课要观察的是：await asyncio.sleep(2) 等待时会让出执行机会；sleep(2) 会占住事件循环所在的线程。
启动服务后，同时打开下面两个地址：
- http://127.0.0.1:8000/async-demo/async-wait
- http://127.0.0.1:8000/async-demo/blocking-wait
两个接口各自都会等待约 2 秒。为了观察差异，可以在一个请求还没返回时，再打开另一个；异步等待期间服务器还能处理其他工作，同步等待期间事件循环会被卡住。单独访问时，两者看起来可能差不多。

# 案例2

这节课可以这样对比：
- /async-demo/blocking-wait 是 async def，却直接调用了同步 sleep(2)，会卡住事件循环线程。
- /async-demo/sync-route 是普通 def。FastAPI 会把它放到线程池中运行，所以它的同步等待不会直接堵住事件循环；线程池中的工作线程会被占用两秒。
试法：先打开 /async-demo/blocking-wait，再立刻打开 /async-demo/async-wait，后一个请求可能被前一个拖住。换成先打开 /async-demo/sync-route，再打开 /async-demo/async-wait，异步接口通常不必等同步路由睡完。

# 案例3