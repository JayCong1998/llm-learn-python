# 自己定义一个模块 名字叫做 module.py
'''
# 第一种:
# 1.通过import 导入自己定义的模块
import module

# 2.使用自定义模块中的变量和函数等等
print(module.name)  # 印度阿三
print(module.age)   # 18

module.say()
module.register()

# 第二种:
# 通过from.... import .... 的方式导入自定义模块,(* 表示模块中的所有的内容,不推荐使用* 导入)
from module import *
print(name)
print(age)
say()
login()

# 第三种:
# 通过from....import.... 精确导入(推荐使用此方式)
from module import name,age
print(name)
print(age)
'''
# 第四: 通过  as  给模块起别名
import module as m
print(m.name)
print(m.age)
