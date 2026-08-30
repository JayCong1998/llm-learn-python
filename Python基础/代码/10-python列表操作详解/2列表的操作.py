# 1.列表元素的组合
'''
list1 = [2,345,7,63,57]
list2 = ['荔枝','龙岩','火龙果','芒果','橙子']
print(list1,list2)
# 通过  +  实现列表的合并
list3 = list1 + list2
print(list3)  # [2, 345, 7, 63, 57, '荔枝', '龙岩', '火龙果', '芒果', '橙子']
'''
'''
# 2.列表元素重复  通过  *  号实现
list1 = [1,2,3]
print(list1)
list2 = list1 * 4
print(list2)

# 3.判断元素是否在列表中   使用成员运算符  in和 not in
list1 = ['apple','banana','boy',12,True]
print('boy' in list1)   # True
print('girl' in list1)  # False
print('boy' not in list1) # False
'''
# 4.列表的切片
list1 = [12,34,6,8,855,683,57]
# 语法: 列表名[开始下标:结束下标]  特点: 包含开始下标对应的元素   不包含结束下标对应的元素
print(list1[1:5])  # [34, 6, 8, 855]
print(list1[:4])   # [12, 34, 6, 8]    在切片时,若未写开始下标,默认从第一个元素开始截取
print(list1[1:])   # [34, 6, 8, 855, 683, 57]   在切片时,若未写结束下标,从开始下表的位置一直截取到最后
print(list1[:])    # [12, 34, 6, 8, 855, 683, 57]
print(list1[-2:])  # [683, 57]
print(list1[::-1])  # [57, 683, 855, 8, 6, 34, 12]    # 翻转列表
