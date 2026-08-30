# 定义字典
dict1 = {'name':'朱成康','age':25,'sex':'男','hobby':'把妹'}
# print(dict1)

# 1.访问字典中的元素   通过key访问
# print(dict1['name'])   # 朱成康
# print(dict1['hobby'])  # 把妹
# print(dict1['weight'])  # 访问不存在的属性会报错

# 通过get()函数访问字典中的元素
# print(dict1.get('name'))  # 朱成康
# print(dict1.get('height'))  # None  当访问的属性不存在时,返回None

# 2.获取字典的长度  len()
# print(len(dict1))  # 4

# 3.获取字典中的所有的key
# print(dict1.keys())  # dict_keys(['name', 'age', 'sex', 'hobby'])

# 4.获取字典中的所有的value
# print(dict1.values()) # dict_values(['朱成康', 25, '男', '把妹'])

# 5.获取字典中的key和value
# print(dict1.items())  # dict_items([('name', '朱成康'), ('age', 25), ('sex', '男'), ('hobby', '把妹')])

# 6.遍历字典中的元素
'''
# 第一种方式:  i表示字典中的key
for i in dict1:
    print(i)

# 第二种方式:  enumrate遍历字典中的key
for index,value in enumerate(dict1):
    print(index,value)

# 第三种方式:  遍历字典中的key和value  常用
for key,value in dict1.items():
    print(key,value)

# 第四种方式: 遍历字典中的值
for value in dict1.values():
    print(value)
'''
# 7.合并字典   update()
dict2 = {'name':'朱琴琴','age':25,'height':165}
dict3 = {'sex':'美女'}

# print(dict2,dict3)
# dict2.update(dict3)
# print(dict2)

# 8.新增数据
dict4 = {'name':'iPhone14','size':7.7,'price':9876}
# print(dict4)  # {'name': 'iPhone14', 'size': 7.7, 'price': 9876}
dict4['color'] = '土豪金'
# print(dict4)  # {'name': 'iPhone14', 'size': 7.7, 'price': 9876, 'color': '土豪金'}

# 修改数据
dict4['price'] = 6789
# print(dict4)  # {'name': 'iPhone14', 'size': 7.7, 'price': 6789, 'color': '土豪金'}

# 删除数据
# 第一种方式: pop('属性')
print(dict4)  # {'name': 'iPhone14', 'size': 7.7, 'price': 6789, 'color': '土豪金'}
# dict4.pop('size')
# print(dict4)  # {'name': 'iPhone14', 'price': 6789, 'color': '土豪金'}

# 第二种方式: popitem()
# print(dict4.popitem())  # ('color', '土豪金')

# 第三种方式:clear()
dict4.clear()
print(dict4)  # {}




