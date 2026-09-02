# 1.获取元组的长度  len()
tup1 = (12,45,78,53,True,'橘子')
# print(len(tup1))   # 6

# 2.获取元组中的最大值max()和最小值min()
tup2 = (12,43,67,853,89)
# print(max(tup2))   # 853
# print(min(tup2))   # 12

# 3.其他数据类型转换为元组  tuple()
list1 = [234,45,46,78]
# print(type(list1))  # <class 'list'>
# print(type(tuple(list1)))  # <class 'tuple'>

# 4.遍历元组
tup3 = ('梅西','姆巴佩','马丁内斯','恩佐','迪玛利亚')
# 第一种方式:  i表示元组中的每个元素
'''
for i in tup3:
    print(i)

# 第二种方式:  i表示元组中每个元素的下标
for i in range(len(tup3)):
    print(i,tup3[i])
'''

# 第三种方式: enumrate()  返回下标和元素  index表示下标  value表示值
for index,value in enumerate(tup3):
    print(index,value)


