# 字典: 语法: {key1:value1,key2:value2,key3:value3......}

# 定义字典:
#1. 空字典
dict1 = {}
print(dict1)

# 2.定义非空字典
# 第一种方式: 最常用
dict2 = {'name':'梅西','age':35,'height':170,'weight':140}
print(dict2)

# 第二种方式:
dict3 = dict(color='粉色',size='2XL',price=999)
print(dict3)  # {'color': '粉色', 'size': '2XL', 'price': 999}

# 第三种方式: dict(zip([key1,key2,key3....],[value1,value2,value3.....]))
# 注意:当key的数量和value的数量不一致时,以数量少的为基准
dict4 = dict(zip(['name','love','province'],['于谦','抽烟','北京市']))
print(dict4)
dict5 = dict(zip(['name','love','province','sex'],['于谦','抽烟','北京市']))
print(dict5)

# 第四种方式:
dict6 = dict([('name','C罗'),('country','葡萄牙'),('age',37),('sex','猛男')])
print(dict6)