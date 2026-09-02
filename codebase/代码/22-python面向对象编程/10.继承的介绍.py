# 面向对象的三大特性: 封装  继承   多态

# 继承: 如果两个或者两个以上的类具有相同的属性和方法,我们可以抽取出一个类,在抽取的类中声明公共的部分,被抽取出来的类叫做父类.基类 根类.   两个或者两个以上的类叫做子类或者派生类.

'''
注意:
1.object 是所有类的父类. 如果一个类没有明确告知他的父类 ,则默认是object类.
2.简化代码,提高代码的复用性.
'''

# 1.单继承: 一个子类只有一个父类
# 没有构造函数的继承
# 父类
class Person(object):
    def say(self):
        print('说话的方法')


# 子类
class Boy(Person):  # 将父类的名称传递到参数中,就实现了子类继承父类
    def eat(self):
        print('子类自己的吃饭的方法.....')

# 创建子类对象
boy = Boy()
# 子类调用自己的方法
# boy.eat()
# 子类调用父类的方法
# boy.say()

# 2.有构造函数的继承
# 父类
class Animal(object):
    # 构造函数
    def __init__(self,name,sex):
        self.name = name
        self.sex = sex

    def eat(self):
        print('所有动物都有捕食的技能')

# 子类
class Cat(Animal):
    # 构造函数
    def __init__(self,name,sex,tail):
        # 第一种方式: 继承父类的构造函数(经典的写法)
        # Animal.__init__(self,name,sex)   # 继承父类的构造函数

        # 第二种方式: 隐式继承父类的构造函数
        super(Cat,self).__init__(name,sex)

        # 定义子类自己的属性
        self.tail = tail

    def skill(self):
        print('猫科动物会爬树....')

# 创建子类对象
cat = Cat('波斯猫','母猫','揪尾巴')
# 通过对象访问属性
#print(cat.name)
#print(cat.sex)
#print(cat.tail)
# 通过对象访问父类的方法
#cat.eat()
# 通过对象访问自己的方法
#cat.skill()

'''
总结:
1.子类对象可以访问父类中的非私有化属性.
2.子类对象可以访问父类中的非私有化方法.
3.父类不能调用子类对象中的任意内容
'''
'''
继承的优缺点:
优点:
1.简化代码,减少代码的冗余
2.提高代码的复用性
3.提高代码的可维护性
4.继承是多态的前提

缺点:
1.在项目中通常使用耦合度来表示代码的质量,耦合度越低,代码质量越高.
'''

# 3.多继承:一个子类可以继承多个父类
'''
语法:
class 子类类名(父类1,父类2,父类3.....):
    类体
'''

# 父亲类
class Father(object):
    def __init__(self,surname):
        self.surname = surname

    def make_money(self):
        print('钱难挣,粑粑难吃......')

# 母亲类
class Mother(object):
    def __init__(self,height):
        self.height = height

    def eat(self):
        print('干饭人,干饭魂......')

# 子类, 子类同时继承父亲类和母亲类
class Son(Father,Mother):
    def __init__(self,surname,height,weight):
        # 子类继承父类的构造函数
        Father.__init__(self,surname)
        Mother.__init__(self,height)

        # 子类定义自己的属性
        self.weight = weight

    def play(self):
        print('就是这么飞倍爽.....')

# 创建子类对象
son = Son('朱',175,145)
# 子类对象访问继承的父类的属性
print(son.surname)
print(son.height)

# 子类对象访问自己的属性
print(son.weight)


# 子类访问父亲类的方法
son.make_money()

# 子类访问母亲类的方法
son.eat()

# 子类对象访问自己的方法
son.play()









