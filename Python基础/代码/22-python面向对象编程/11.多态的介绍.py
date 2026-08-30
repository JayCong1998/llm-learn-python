# 一个事物的多种体现方式,函数的重写其实就是多态的一种体现.
# 在python中多态指的是父类的引用指向子类的对象

# 父类
class Animal(object):
    def eat(self):
        print('吃饭的方法....')

# 子类
class Fish(Animal):
    def eat(self):
        print('大鱼吃小鱼,小鱼吃虾米.....')

class Dog(Animal):
    def eat(self):
        print('狼行千里吃肉,狗走万里吃粑粑....')

class Cat(Animal):
    def eat(self):
        print('猫爱偷腥.....')


# 1.简单的多态的体现
fish = Fish()
dog = Dog()
cat = Cat()
# 子类调用eat方法,执行的是属于子类自己的eat方法,这就是一种简单的多态的体现
fish.eat()
dog.eat()
cat.eat()

print(("========="))
# 2.严格意义上多态的体现
class Person():
    def feed(self,animal):
        animal.eat()

# 严格意义上多态的体现
Person().feed(fish)
Person().feed(dog)
Person().feed(cat)