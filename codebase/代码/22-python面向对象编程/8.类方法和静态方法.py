class Animal():
    # 类属性
    name = "牧羊犬"

    # 对象的属性 构造函数
    def __init__(self,name,sex):
        self.name = name
        self.sex = sex

    # 对象的方法
    def eat(self):
        print('吃饭的方法')

    '''
    类方法:
        1.通过@classmethod  装饰器修饰的方法就是类方法
        2.类方法可以使用类名或者对象名调用,但是一般情况下使用类名调用.(节省内存)
        3.参数中没有self,在类方法中不可以使用其他对象的属性和方法(包括私有属性和私有方法)
        4.可以调用类属性和其他类的方法,通过cls来调用
        5.cls是class的简写, 可以使用别的变量名代替,只不过是约定俗成的写法.
        6.cls表示的是当前类    
    '''
    @classmethod
    def run(cls):
        print('我是类方法')
        # 在类方法中访问类属性
        print(cls.name)
    '''
    静态方法:
        1.通过@staticmethod装饰器修饰的方法就是静态方法
        2.通过类名或者对象名可以调用静态方法,一般使用类名调用
        3.静态方法中,参数中没有cls,在静态方法中不建议调用(类属性\类方法\静态方法等等)
        4.静态方法一般是一个单独的方法,只是写在类中
    '''
    @staticmethod
    def drink():
        print('我是静态方法')

# 创建对象
animal = Animal('泰迪','公狗')
# 通过对象调用对象的方法
animal.eat()

# 通过类名调用类方法
# Animal.run()

# 通过对象调用类方法, 不推荐
animal.run()

# 通过类名调用静态方法
Animal.drink()

