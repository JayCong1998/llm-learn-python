# 需求: 给已知函数 test()增加一个功能, 多输出一句话,"大家注意防护."
def test():
    print("多地公共机构减员严重 停办线下业务")
# test()

'''
第一种方式:重写函数
def test():
    print("多地公共机构减员严重 停办线下业务")
    print("大家注意防护.")
test()


# 第二种方式: 函数嵌套函数
def demo():
    test()
    print("大家注意防护.")
demo()

# 第三种方式: 装饰器

在代码的运行的期间,可以动态的给原函数增加功能,被称为装饰器(使用闭包函数实现)
好处:
在团队开发中,假如两个或者更多的同事使用了相同的功能,但是整体的效果又有一些细微的差别,这时候可以采用装饰器,互相不影响.代码简化

# 此处的outer()就是装饰器函数
def outer(fn):  # fn表示形参, 在装饰器函数调用的时候,传入的实际参数是 原函数
    def inner():
        fn()   # ===>test()  调用原函数test()
        print("大家注意防护.")  # 给原函数动态增加的功能,原则上添加的功能可以在原函数的上面也可以在原函数的下面.
    return inner
print("添加装饰器之前:", test.__name__)
test = outer(test)
print("添加装饰器之后:",test.__name__)
test()
'''

# 装饰器的简写方式:
'''
# 将装饰器函数放在原函数的上面会报错
@outer   # 等价于  demo = outer(demo)
def demo():
    print('today is a nice day')
'''
# 装饰器函数outer()
def outer(fn):
    def inner():
        fn()  # 表示调用原函数  demo()
        print("very good")  # 新增的功能
    return inner
# 原函数
# 装饰器的简写方式:  @ + 装饰器函数名
@outer   # 等价于  demo = outer(demo)
def demo():
    print('today is a nice day')
demo()
'''
总结:
1.装饰器函数的简写方式: @ + 装饰器函数名   比如 @outer   等价于 demo = outer(demo)
2.在使用装饰器的简写方式的时候,原函数必须放在装饰器函数的下面.
'''