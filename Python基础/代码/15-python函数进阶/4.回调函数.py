def fn(n,m):
    print(n + m)
# fn(12,57)  # 69

# 函数调用的格式: 函数名() <=====> 变量名()
# 若把函数名赋值给了一个新的变量,那这个变量就具备了和函数一样的功能.
demo = fn
# demo(12,57)  # 69
# print(type(fn))   # <class 'function'>
# print(type(demo)) # <class 'function'>

# 回调函数: 把一个函数(a)作为一个参数传输到另一个函数(b)中去,那么函数a就是一个回调函数.

# 和
def add(a,b):
    print(a + b)
# 差
def cha(a,b):
    print(a - b)
# 乘积
def ji(a,b):
    print(a * b)
# 商
def shang(a,b):
    print(a / b)
# add(12,3)  # 15
# cha(12,3)  # 9
# ji(12,3)   # 36
# shang(12,3)  # 4.0
# 封装一个函数.实现加减乘除的操作
def common(a,b,func):
    func(a,b)
# 加法
common(12,3,add)    # 15
# 减法
common(12,3,cha)    # 9
# 乘积
common(12,3,ji)     # 36
# 商
common(12,3,shang)  # 4.0