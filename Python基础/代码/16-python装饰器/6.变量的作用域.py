# 变量的作用域: 是指变量能够被访问的范围
# 程序中的变量不是在任意位置都是可以被访问的,访问的权限取决于这个变量的位置.

# 在python中,分支语句 if...else,  if.... 和 for循环 和 while循环中不存在作用域的问题.

if 5 > 3:
    a = 987

# print(a)

for i in range(10):
    b = 23

# print(b)

# 注意: 在函数内部定义的变量,在函数外部不可以使用.
def demo():
    c = 31

# print(c)   # NameError: name 'c' is not defined

# 作用域的分类:
'''
1.局部作用域: L
2.函数作用域:E  将变量定义在闭包外的函数中(外部函数中)
3.全局作用域:G
4.内建作用域: B
'''

# 1.局部作用域: 将变量定义在函数的内部
def test():
    xingmig = '嘉琪'
# print(xingming)   # NameError: name 'xingming' is not defined

# 2.全局作用域: 在函数的内部和外部可以直接访问,(在文件的任意位置可以访问)
num1 = 123
def add():
    num2 = 65
    print(num1)

add()   # 123  在函数内部可以访问外部的变量

print(num1)  # 123  在函数的外部可以访问外部的变量

# 3.函数作用域
def outer():
    cc = 76   # 函数作用域
    def inner():
        print(cc)
    return inner

test = outer()
test()  # 76

# 4.内建作用域:
nn = int("986")   # 在python的内置函数中,python解释器自己定义的作用域
print(nn)