# 面向对象的特点: 封装   继承    多态.
# 狭义的封装: 更多体现在属性私有化和方法私有化
class Girl():
    # 构造函数
    def __init__(self,name,sex,height):
        self.name = name
        self.sex = sex
        self.height = height
        # 设置私有属性: 格式是在属性的前面添加两个下划线
        self.__age = 18
    def say(self):
        print('啦啦啦.....')
    # 在类的内部,定义一个方法,提供访问私有属性的接口
    def sayAge(self,boy):
        if boy == "胡文豹":
            print(f"{self.name}偷偷的告诉你,我今年{self.__age}岁了")
        else:
            print("女孩的年龄是秘密,不知道吗?活该你单身,傻狗....")


    # 私有方法: 格式是在方法的前面添加两个下划线
    def __kiss(self):
        print('一吻定终身....')

    # 在类的内部可以访问私有方法
    def love(self,relation):
        if relation == '情侣':
            self.__kiss()
        else:
            print('不能随便kiss,小心中毒....')

girl = Girl('小红','女',170)
print(girl.name)   # 小红
print(girl.sex)    # 女
print(girl.height)  # 170
# print(girl.age)   # AttributeError: 'Girl' object has no attribute 'age'   私有属性不能在类的外部直接访问.

# 通过定义的接口访问私有属性
girl.sayAge('胡文豹')   # 小红偷偷的告诉你,我今年18岁了
girl.sayAge('张武强')

# girl.__kiss()  # 在类的外部不能直接访问私有方法
girl.love('情侣')   # 一吻定终身....
girl.love('朋友')   # 不能随便kiss,小心中毒....

'''
私有属性:
    设置私有属性,格式是在属性的前面添加两个下划线
    特点: 不能在类的外部直接访问,只能在类的内部访问.一般情况下会在类的内部访问的时候会设置各种条件判断,满足条件之后才能访问私有属性,私有属性一般表示私密的信息
私有方法:
    设置私有方法,格式实在方法的前面添加两个下划线
    特点: 只能在类的内部访问,不能在类的外部访问. 私有方法一般在类的内部实现某些特殊的功能,对于类的外部来说没有什么实际意义.


'''