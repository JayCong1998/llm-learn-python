'''
类属性一般使用类名访问和修改
对象属性一般使用对象访问和修改
'''
class Fish():
    # 类属性
    name = '蓝鳍金枪鱼'
    # 对象的属性  (构造函数)
    def __init__(self,weight):
        self.weight = weight
# 创建对象
fish = Fish(9876)
# 使用类名访问类属性
print(Fish.name)
# 使用对象访问对象的属性
print(fish.weight)
# 使用类名修改类属性
Fish.name = '斗鱼'
print(Fish.name)
# 使用对象修改对象的属性
fish.weight = 12345
print(fish.weight)
