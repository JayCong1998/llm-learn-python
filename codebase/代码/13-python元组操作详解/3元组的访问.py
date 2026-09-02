#
tup1 =  (23,57,73,37,98,'hello',9.54,False)
# 1.访问元组中的元素,使用下标访问,下标默认从0开始
print(tup1[0])  # 23  下标为0表示第一个元素
print(tup1[-1])  # False  下标为-1表示最后一个元素

'''
# 2.元组中的元素的值,不能修改
print(tup1[2])
tup1[2] = '你好'
print(tup1)   # TypeError: 'tuple' object does not support item assignment
'''
# 3.删除元组  del
print(tup1)
del tup1
print(tup1)