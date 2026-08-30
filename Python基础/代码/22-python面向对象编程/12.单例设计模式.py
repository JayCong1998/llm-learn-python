# 单例设计模式: 单个对象   主要用于数据库的连接
# __new__() :创建对象的时候触发

class Person(object):
    # 构造函数
    def __init__(self,name):
        print("__init__")
        print(name)

    # 定义一个类属性    用于接收创建好的对象
    instance = None
    @classmethod
    def __new__(cls,*args,**kwargs):
        print('__new__')
        # 判断类属性是否为空,若为空,表示未创建过对象,这时候我们就创建对象,若不为空,表示已经创建过对象,则直接返回类属性
        if cls.instance == None:
            cls.instance = super().__new__(cls)
        # 表示已经创建过对象,直接返回类属性
        return cls.instance

# 创建对象
person = Person('琴琴')
person1 = Person('琴琴')
person2 = Person('琴琴')

print(person == person1 == person2)   # True
'''
__new__() : 是创建对象的时候自动触发
__init__() : 是创建完对象后,给对象赋值时触发.
'''


