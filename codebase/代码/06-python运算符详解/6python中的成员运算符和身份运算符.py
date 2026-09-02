# python中常见的数据类型: int(整型)  float(浮点型)  bool(布尔类型)  string(字符串类型)  list(列表类型) tuple(元组类型)  dict(字典类型)

'''

# 整型
num = 123
print(num)  # 123
print(type(num))  # <class 'int'>
# 浮点型
float1 = 2.34
print(float1)  # 2.34
print(type(float1))  # <class 'float'>
# 字符串类型
str1 = 'hello'
str2 = "world"
print(str1)  # hello
print(str2)  # world
print(type(str1))  # <class 'str'>
print(type(str2))  # <class 'str'>
# 列表类型  使用 [元素1,元素2,元素3,元素4......]
# 列表中的元素的类型可以不一致
print([])   # 空列表
print([12,43,4.56,'apple',True,56])  # [12, 43, 4.56, 'apple', True, 56]

# 字典类型  使用 {key1:value1,key2:value2,key3:value3......}
dict1 = {'name':'嘉豪','age':38,'height':165,'weight':180}
print(dict1)
print(type(dict1))  # <class 'dict'>

# 布尔类型:  值有两个. True和False
bool1 = True
bool2 = False
print(bool1)
print(bool2)

'''
# 成员运算符: in 和 not in
# print(12 in [13,43,6565,8.43,'banana'])  # False
# print(12 not in [13,43,6565,8.43,'banana'])  # True
# print('welcome' in 'welcome to shenzhen')  # True

# 判断输入的月份是否是31天
# month = int(input('请输入月份:'))
# print(month in [1,3,5,7,8,10,12])

# 身份运算符: is 和 is not 主要用于判断变量的内存地址是否相同  (了解)
# id() 获取变量的内存地址
x = 12
y = 12
print(x)
print(y)
print(id(x))
print(id(y))
print(x is y)  # True
print(x is not y) # False
