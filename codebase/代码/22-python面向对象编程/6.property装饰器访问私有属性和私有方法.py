class Girl():
    # 构造函数
    def __init__(self,name,age):
        self.name = name
        # 私有属性
        self.__age = age

    '''
    访问私有属性
    def getAge(self):
        return self.__age
    设置私有属性
    def setAge(self):
        self.__age = age
    '''
    # 通过装饰器的方式访问私有属性  相当于 getAge
    @property
    def age(self):
        return self.__age
    
    # 通过装饰器设置私有属性   语法:@ + 私有属性名 + setter    相当于 setAge
    @age.setter
    def age(self,age):
        self.__age = age
# 创建对象
girl = Girl('花花',25)
# 通过装饰器的方式在类的外部直接访问私有属性
print(girl.age)

# 通过装饰器的方式在类的外部设置私有属性
girl.age = 34
print(girl.age)