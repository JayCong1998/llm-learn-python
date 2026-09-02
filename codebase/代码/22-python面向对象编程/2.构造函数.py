# 构造函数:
class GirlFriend():
    '''
    类属性    不推荐这种写法
    name = '苍井空'
    age = 43
    '''
    # 构造函数 __init__()  参数是对象相关的属性
    def __init__(self,name,age):
        # 对象的属性
        self.name = name
        self.age = age
        print('构造函数的触发时机是:当创建完对象后,给对象传输属性时自动触发')
    # 对象的方法
    def say(self):
        print(self.name,'喊文豹,来啊来啊.......')

    def sing(self):
        print('唱歌给豹哥听......')
# 创建对象
girl = GirlFriend("小红",18)
girl1 = GirlFriend('小兰',22)
print(girl.name)
print(girl.age)

print(girl1.name)
print(girl1.age)

# 应用场景:
'''
一般用于连接数据库操作
'''