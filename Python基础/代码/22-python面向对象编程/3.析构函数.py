# 析构函数: 与构造函数正好相反,当对象被销毁的时候,会自动触发.
# 应用场景: 主要用于关闭数据库或者关闭文件.

class Fish():
    # 构造函数
    def __init__(self,color,weight):
        self.color = color
        self.weight = weight

    # 对象的方法
    def swim(self):
        print('我是一条鱼,游来游去.....')

    # 析构函数
    def __del__(self):
        print('我的触发时机是:当对象被销毁的时候,自动触发....')

fish = Fish("金色",123)
fish.swim()