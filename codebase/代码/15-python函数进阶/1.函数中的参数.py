# 1.参数列表: 如果函数需要实现的功能中涉及到一些未知项的数据,此时就可以将未知项设置为参数.
# 格式: 参数1,参数2,....
# 分类:
'''
形式参数: 声明函数的时候,写在函数名后面的小括号内的.本质上就是一个变量,用于接收实际参数的值.
实际参数: 在函数调用的时候,实际参与运算的数据,用于替换形式参数.
传参: 实际参数替换形式参数的过程.
'''

# 封装一个函数,传入两个数字,输出较大的一个数字
def get_max(num1,num2):  # num1和num2是形式参数
    if num1 > num2:
        print('较大的数字是:',num1)
    else:
        print('较大的数字是:',num2)

# get_max(32,47)   # 32和47是实际参数

'''
1.一般情况下,形式参数的数量和实际参数的数量保持一致.
2.在函数中,形参的名字和实参的名字可以一样.(本质上是在程序中开辟了不同的内存空间)
'''
# 参数的类型:
# a.必须参数: 调用函数的时候,必须以正确的顺序传参,实参的数量和形参的数量保持一致.
def demo(name,age):
    print("我的姓名是:%s,年龄是:%d"%(name,age))
# demo('成康',23)
# demo(23,'成康')   # TypeError: %d format: a real number is required, not str


# b.关键字参数: 允许函数调用的时候的实际参数和定义的时候的形式参数顺序不一致,使用关键字进行自动匹配.
# demo(age = 23,name = '安恩慧')

# c.默认参数: 在定义函数的时候,给形式参数直接赋值.
'''
注意:
1.函数调用的时候,若没有传递参数,会直接使用默认参数,若传递了参数,则使用传递的参数
2.默认参数一般写在参数列表的最后面.
'''
def he(num1,num2 = 23):  # num2 = 23表示默认参数
    print('num1和num2两个数字的和是:',num1 + num2)

# 未使用默认参数
# he(10,50)  # 60
# 使用了默认参数
# he(82)  # 105

# 把默认参数放在参数列表的前面会报错
'''
def cha(num1 = 23,num2):  # SyntaxError: non-default argument follows default argument
    print('num1和num2两个数字的差是:',num1 - num2)
'''


# d.不定长参数(可变参数):可以处理比声明时更多的参数.  *args  **kwargs
'''
*args: 用来接收多个位置参数,得到的是元组.   是arguments的简写
**kwargs: 用来接收多个关键字参数,得到的是一个字典.  是 keyword arguments的简写
'''
def fn(*args):
    print(args)

# fn(12,34)   # (12, 34)
# fn(87,45,67)  # (87, 45, 67)
# fn(82,48,246,52)  # (82, 48, 246, 52)

'''
# 注意: 当 *args 和普通参数放在一起的时候,需要将*args放在参数列表的后面.
def say(name,*args):
    print(name,args)
say('嘉琪',170,100)   # 嘉琪 (170, 100)

# 会报错
def demo(*args,name):
    print(args,name)
demo(170,100,'嘉琪')  # TypeError: demo() missing 1 required keyword-only argument: 'name'
'''

# **kwargs 表示关键字参数,传输的数据格式:key=value
# 注意: **kwargs若和普通参数放在一起,必须将**kwargs放在参数列表的后面,否则会报错.
def say1(**kwargs):
    print(kwargs)
say1(name='张强',age = 22,height=175)  # {'name': '张强', 'age': 22, 'height': 175}

def say2(name,**kwargs):
    print(name,kwargs)
say2('宏海',age = 24,weight = 140)  # 宏海 {'age': 24, 'weight': 140}

# 会报错.
'''
def say3(**kwargs,name):
    print(name,kwargs)
'''