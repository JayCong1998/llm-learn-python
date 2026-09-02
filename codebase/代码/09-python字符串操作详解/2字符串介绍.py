# 字符串可以使用一对单引号或者一对双引号或者一对三个单引号或者一对三个双引号包裹的文本
'''
# 创建字符串
str1 = '大力神杯'
str2 = "潘帕斯雄鹰"
print(str1,str2)
print(type(str1))  # <class 'str'>
print(type(str2))  # <class 'str'>

# 转义字符  \  让符号失去原有的意义
str3 = "各位宝子们"
str4 = "\"各位宝子们\""
print(str3)   # 各位宝子们
print(str4)  # "各位宝子们"

# 在字符串的前面加 r  可以去除转义字符
# \n表示换行  \t表示制表符
str5 = "大家注意防护\n不要阳了"
str6 = r"大家注意防护\n不要阳了"
print(str5)
"""
大家注意防护
不要阳了
"""
print(str6)  # 大家注意防护\n不要阳了

# 在定义字符串的时候,可以使用单双引号嵌套
str7 = '想死"你们"了'
print(str7)  # 想死"你们"了


# 在字符串的前面加 f 可以支持{}语法
name = '小红'
age = 18
height = 168
print('姓名:',name,'年龄:',age,'身高:',height)  # 姓名: 小红 年龄: 18 身高: 168
print(f"姓名:{name} 年龄:{age} 身高:{height}")  # 姓名:小红 年龄:18 身高:168

# 在字符串的前面加 b 表示该字符串的类型是bytes类型
str8 = "hello"
str9 = b"hello"
print(type(str8))  # <class 'str'>
print(type(str9))  # <class 'bytes'>
'''

# 在字符串前面加 u  表示后面的字符串以Unicode格式进行编码  一般将u加在中文字符串前面,防止源码因为存储格式的问题,导致再次使用时出现乱码
str10 = u'中国'
str11 = "中国"
print(str10)
print(str11)

