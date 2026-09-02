# 1.int(): 将其他数据类型转换为整型
num1 = "32"
print(num1)
num2 = int(num1)
print(num2)

# type() 表示检测变量的数据类型
print(type(num1)) # <class 'str'>
print(type(num2)) # <class 'int'>

# 2 str(): 将其他数据类型转换为字符串
num = 12
num1 = 87
print(num1 + num) # 99
print(type(num)) # <class 'int'> # print(type(num1)) # <class 'int'>
str1 = str(num)
str2 = str(num1)
print(type(str1)) # print(type(str1)) # print(type(str2)) # <class 'str'>
print(str1 + str2) # 1287

# 3.float(): 将其他数据类型转换为浮点型
float1 = "12.34"
print(type(float1)) #
print(type(float(float1))) # <class 'float'>
float2 = "hello123" # 不能转换为浮点型
print(float(float2)) # 报错

# 4.bool() : 用于将给定参数转换为布尔类型.如果没有参数,返回False

# 布尔类型: True 和 False
# bool(): 将其他数据类型转换为布尔类型
print(bool(100)) # True
print(bool(3.12)) # True
print(bool(0)) # False
print(bool("hello")) # True
print(bool('')) # False
print(bool("")) # False
print(bool(' ')) # True
print(bool([12,34,7])) # True
print(bool([])) # False
print(bool((32,45,67))) # True
print(bool({"name":"三哥","age":18})) # True
print(bool(())) #False
print(bool({})) # False
print(bool(None)) # False
# 数字0,空字符串""或者'',空列表[],空元组(),空字典{},空集合set(),None这些数据转换为bool类型 时是False.

#5.list() : 用于将其他数据类型转换为列表.
tup = (12,34,678,9)
print(tup)
print(type(tup)) # <class 'tuple'>
print(type(list(tup))) # <class 'list'>
list1 = list(tup)
print(list1) # [12, 34, 678, 9]
str = "hello"
list2 = list(str)
print(list2) # ['h', 'e', 'l', 'l', 'o'] num = 12
print(list(num)) # 报错
# 注意: 一般情况下,是字符串和元组类型的数据转换为列表类型居多.

# 6.tuple() : 用于将其他类型的数据转换为元组
# tuple() 将其他数据类型转换为元组
lis1 = [12.45, 678, 9, True, False, 87]
print(type(lis1))  # <class 'list'> print(type(tuple(lis1))) # <class 'tuple'>
string1 = "123"
print(type(string1))  # <class 'str'>
# print(type(tuple(string1))) # <class 'tuple'>
# print(tuple(string1)) # ('1', '2', '3')
# 注意: 一般情况下, 是字符串和列表类型的数据转换为元组类型居多.
