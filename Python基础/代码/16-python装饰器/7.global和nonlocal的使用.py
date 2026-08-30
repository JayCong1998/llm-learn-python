#
num = 11  # 全局变量

def fn():
    num = 98
    print(num)

# fn()   # 98

# print(num)  # 11

'''
1.当函数的内部和函数的外部出现了名字一样的变量,在函数中使用的是函数内部的变量.
2.在函数的内部定义了和函数的外部名字一样的变量,不会修改函数外部变量的值.
'''

# 1. 若想在函数的内部对全局变量进行修改,需要使用global关键字
cc = 123
def demo():
    global cc  # 表示将函数内部的变量声明成了全局变量
    cc = 987
    print(cc)

# demo()   # 987
# print(cc)  # 987

# 2.nonlocal主要用于闭包函数中
x = 15   # 全局变量
def outer():
    x = 87
    def inner():
        # global x
        nonlocal x
        x += 1
        print('inner:',x)
    return inner

func1 = outer()
# 在闭包函数中使用global
# func1()   # inner: 16
# func1()   # inner: 17


# 在闭包函数中使用nonlocal  用于外部函数的变量
func1()    # inner: 88
func1()    # inner: 89
func1()    # inner: 90
