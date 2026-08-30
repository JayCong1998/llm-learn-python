# 集合 set {value1,value2,value3.....}   是无序的
# 创建空集合
set1 = set()
# print(set1) # set()
# print(type(set1))  # <class 'set'>

# 创建包含元素的集合   元素可以是不同的数据类型
set2 = {'柠檬',23,65.43,True,False}
# print(set2)  # {False, 65.43, True, 23, '柠檬'}

# 集合中的元素不能使用下标访问
# print(set2[2])  # TypeError: 'set' object is not subscriptable

# 获取集合的长度 len()
# print(len(set2))  # 5

# 向集合中添加元素
# add() 添加单个元素
# print(set2)  # {False, 65.43, True, 23, '柠檬'}
# set2.add('浩南')
# print(set2)  # {False, 65.43, True, 23, '柠檬', '浩南'}

# update() 追加多个元素 (以列表的形式追加)
set2.update(['嘉豪','成康','琴琴'])
# print(set2)  # {False, 65.43, True, '琴琴', '成康', 23, '嘉豪', '柠檬'}

# 删除集合中的元素
set3 = {False, 65.43, True, '琴琴', '成康', 23, '嘉豪', '柠檬'}
# pop() 随机删除一个元素
# print(set3)
# set3.pop()
# print(set3)

# remove()删除指定的元素  传入的参数是要删除的元素, 如果删除的元素不存在,会报错
# set3.remove('恩惠')  # KeyError: '恩惠'
# set3.remove('嘉豪')
# print(set3)

# discard()删除指定的元素 传入的参数是要删除的元素  如果删除的元素不存在,不会报错
# print(set3)
# set3.discard('恩惠')
# print(set3)

# clear()清空集合
set3.clear()
# print(set3)  # set()
'''
# 遍历集合
set4 = {'橘子',98,43,56,True}
# i表示集合中每个元素
for i in set4:
    print(i)
'''
# 交集和并集
set5 = {12,34,56,78,5431,456}
set6 = {34,78,4357,85,32}

# 交集  &
print(set5 & set6)  # {34, 78}
# 并集  |
print(set5 | set6)  # {32, 34, 4357, 456, 12, 78, 85, 5431, 56}
# 差集 - set5为基准,
print(set5 - set6)  # {456, 56, 12, 5431}

# 判断set5是否包含set6
print(set5 > set6)  # False
# 判断set6是否包含set5
print(set5 < set6)  # False







