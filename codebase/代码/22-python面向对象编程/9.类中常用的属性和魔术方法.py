'''
类中常用的属性:
    __name__ : 通过类名访问,获取类名字符串.不能通过对象获取,会报错

    __dict__ :获取类相关的信息(类方法\静态方法\成员方法等等) 返回的是一个字典,  通过对象访问获取的是该对象的信息,返回的是一个字典

    __base__ : 通过类名访问,获取的是该类的父类.   返回是一个元组
'''
class Ball():
    # 构造函数
    def __init__(self,name,weight):
        self.name = name
        self.weight = weight
# 创建对象
ball = Ball('篮球','0.5')

# 通过类名访问 __name__
# print(Ball.__name__)   # Ball
# 不能通过对象访问  __name__  会报错
# print(ball.__name__)

# 通过类名访问 __dict__  返回的是一个字典
# print(Ball.__dict__)

# 通过对象访问 __dict__ 返回的是一个字典
# print(ball.__dict__)   # {'name': '篮球', 'weight': '0.5'}

# 通过类名访问 __base__
# print(Ball.__base__)    # <class 'object'>

'''
类中常用的魔术方法: __str__() 和 __repr__()
__str__ 的触发时机是: 当打印对象的时候自动触发.一般是以字符串的形式返回相关的信息.必须使用return 关键字.
__repr__ 的作用和 __str__()类似.当两者都存在的时候,会触发 __str__
'''

class Person():
    # 构造函数
    def __init__(self,name,age):
        self.name = name
        self.age = age

    def swim(self):
        print('游泳的方法')
    '''
    def __str__(self):
        return f"姓名:{self.name},年龄:{self.age}"
    '''

    def __repr__(self):
        return f"姓名:{self.name},年龄:{self.age}"

# 创建对象
person = Person('三哥',23)
print(person)   # 姓名:三哥,年龄:23
