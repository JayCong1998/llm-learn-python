'''
1.按照函数是否需要自己定义:
    内置函数: python 语言内部定义好的,可以直接使用的. print() int() float()  str()  input()
    自定义函数: 根据自己的需求定义的函数,叫做自定义函数

2.根据函数中有没有参数分为:
    有参数的函数: 定义函数,传入的参数叫做形式参数,   函数调用时传入的参数叫做实际参数
    没有参数的函数:

3.根据有没有函数名:
    有名字的函数:
        def 函数名():
            函数体
    匿名函数: 通过lambda表达式进行定义

4.根据函数中是否有返回值:
    有返回值的函数: 通过return 将数据返回
    没有返回值的函数:
'''

# 无参数的函数
def say():
    print('年少不知软饭香.....')
# say()

# 有参数的函数:
def cha(a,b):
    print(a - b)
# cha(12,34)  # -22

# 无返回值的函数
def demo():
    print('没有返回值')
# demo()



'''
注意:
1.return后面可以返回一个或者多个数据,返回的数据以元组的形式展示
2.return 后面的程序不会执行
3.return 后面没有返回任何数据,默认返回的是None
4.若函数中没有return,函数执行完毕后,print() 输出的结果也是None
'''
# 有返回值的函数
def test():
    return 'hello world',123,'apple'
    print(324)
# test() 有返回值的函数,直接调用函数不能查看返回的内容
# print(test())   # ('hello world', 123, 'apple')

# return后面没有返回任何内容
def test1():
    return
print(test1())  # None

# 若函数中没有return,函数执行完毕后,print() 输出的结果也是None
def test2():
    print('梨也卖脱销了...')
print(test2())  # None