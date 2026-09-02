# 创建元组
tuple1 = ()  # 空元组
print(tuple1)  # ()
print(type(tuple1))  # <class 'tuple'>

# 创建包含元素的元组
tuple2 = (12,43,567)
print(tuple2)   # (12, 43, 567)

# 创建包含元素的元组时,若只有一个元素,元素的后面一定要加上逗号    特别注意
tuple3 = (45,)
tuple4 = ('hello',)
print(tuple3)   # (45,)
print(tuple4)   # ('hello',)
print(type(tuple3))  # <class 'tuple'>
print(type(tuple4))  # <class 'tuple'>

# 创建元组时,里面的元素的类型可以是多个
tuple5 = (23,43,9.43,True,False,'apple')
print(tuple5)   # (23, 43, 9.43, True, False, 'apple')


