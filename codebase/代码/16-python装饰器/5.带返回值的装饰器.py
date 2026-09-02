# 带有返回值的装饰器

def outer(fn):
    def inner():
        print("你的爱好是什么?")   # 新增的功能
        return fn()    # 返回  调用原函数的结果
    return  inner # 返回内部函数

# 在原函数的基础上,新增一个功能, 输出: 你的爱好是什么?
# 原函数
@outer
def swim():
    return 'i like swimming.....'

print(swim())