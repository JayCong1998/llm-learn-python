# 定义装饰器  同一个装饰器可以修饰多个函数
def jisuan(fn):
    def inner(*args):
        print('数学运算的结果是:',end="")
        fn(*args)
    return inner

# 需求: 给下面三个函数增加功能,输出 "数学运算的结果是:"

@jisuan
def add(a,b):
    print(a + b)
@jisuan
def cha(x,y,z):
    print(x - y - z)
@jisuan
def ji(c,d,e,f):
    print(c * d * e * f)

add(12,5)
cha(34,21,2)
ji(12,46,3,4)