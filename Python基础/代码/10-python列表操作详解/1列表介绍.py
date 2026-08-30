# 1.创建列表
'''
语法:
变量名 = [数据1,数据2,数据3......]

pyhton中使用 [] 表示列表
列表中的元素使用数字进行了编号,编号又叫做下标或者索引. 下标默认从0开始
'''
# 空列表
list1 = []
# print(list1)  # []

# 带有元素的列表, 列表中的元素可以是不同的类型
list2 = ['劳斯莱斯','迈巴赫','兰博基尼','G63','MODEL-Y','秦',123,True,9.54]
# print(list2)

# 列表的访问
'''
# 获取元素
print(list2[0])  # 劳斯莱斯     0 表示第一个元素
print(list2[-1]) # 9.54       -1 表示最后一个元素
# len() 表示获取元素的个数
print(len(list2))   # 9
print(list2[2])   # 兰博基尼
print(list2[-4])  # 秦
'''
'''
# 修改元素
# 语法: 列表名[索引] = 值
print(list2)  # ['劳斯莱斯', '迈巴赫', '兰博基尼', 'G63', 'MODEL-Y', '秦', 123, True, 9.54]
list2[3] = '奔驰G63'
print(list2)
'''

# 遍历列表
'''
# 第一种方式:
for i in list2:
    print(i)

# 第二种方式:
for i in range(len(list2)):
    print(list2[i])

# 第三种方式: enumerate() 同时遍历索引和元素
for k,v in enumerate(list2):  # k表示索引  v表示值
    print(k,v)
'''

