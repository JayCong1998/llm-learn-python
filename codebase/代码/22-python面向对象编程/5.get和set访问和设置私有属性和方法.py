# get 函数 和 set 函数并不是系统的函数,而是自己定义的. 为了和封装的概念相吻合.一般会设置为 getXXX  和 setXXX
class Girl():
    # 构造函数
    def __init__(self,name,sex,age):
        self.name = name
        self.sex = sex
        # age为私有属性
        self.__age = age
    # 通过get函数访问私有属性,命名规则: get + 私有属性的名字(首字母大写)
    def getAge(self):
        return self.__age
    # 通过set函数设置私有属性,命名规则: set + 私有属性的名字(首字母大写)
    def setAge(self,age):
        self.__age = age
# 创建对象
girl = Girl('兰兰','女',23)
print(girl.name)
print(girl.sex)

# 访问私有属性
# print(girl.__age)
print(girl.getAge())   # 23

# 设置私有属性
girl.setAge(34)
print(girl.getAge())   # 34


