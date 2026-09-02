# 语法:
'''
if 表达式1:
    if 表达式2:
        if 表达式3:
            语句

等同于:
if 表达式1 and 表达式2 and 表达式3:
    语句
'''
# 年龄小于等于30,房子大于120平,车子大于20w
age = int(input('请输入你的年龄:'))
house = int(input('请输入房子面积:'))
car = int(input('请输入车子的价格:'))
'''
if age <= 30:
    if house >= 120:
        if car >= 200000:
           print('感觉你还行,咱俩试试呗....')
'''
# 或者
if age <= 30 and house >= 120 and car >= 200000:
    print('感觉你还行,咱俩试试呗....')
else:
    print('我还有事,先走了,记得买单.....')
