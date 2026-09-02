# python中常见的数据类型: int  float  bool  string list  tuple  dict  set  None

# 可变数据类型:  当值发生改变的时候,内存地址不变, dict  list   set
# 不可变数据类型: 当值发生改变的时候,内存地址改变  string  int float  bool  None   tuple

# 可变数据类型:
'''
list1 = [23,43,5,5.4,55,True]
print(id(list1))   # 2387529689600
print(list1)
# 向列表中添加元素
list1.append('康康')
print(id(list1))    # 2387529689600
print(list1)


dict1 = {'name':'二狗','age':21,'height':180}
print(id(dict1))  # 2656375847744
print(dict1)
dict1['sex'] = '男'
print(id(dict1))  # 2656375847744
print(dict1)
'''

# 不可变数据类型:
'''
num = 12
print(id(num))  # 2383709798992
print(num)
num = 35
print(id(num))  # 2383709799728
print(num)


str1 = 'hello'
print(id(str1))  # 2822076939376
print(str1)
str1 = 'world'
print(id(str1))  # 2822076983088
print(str1)


bool1 = True
print(id(bool1))  # 140710792219496
print(bool1)
bool1 = False
print(id(bool1))  # 140710792219528
print(bool1) 
'''

tup1 = (12,43,5,78)
print(id(tup1))  # 1562281901440
print(tup1)
tup1 = (12,43,5,78,467)
print(id(tup1))  # 1562281080320
print(tup1)
