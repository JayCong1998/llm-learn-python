# 随机数模块  random
import random  # 导入random模块
'''
# 1.从指定的列表中随机选择一个元素  random.choice()
num = random.choice([43,57,26,258,52])
print(num)   # 26

list1 = random.choice(range(5)) #  ===> (0,1,2,3,4)
print(list1)   # 1

# 从字符串中随机取一个元素
str1 = random.choice('hello')
print(str1)  # e
'''

# 2.生成指定范围内的随机数   random.randrange(start,end,step)
'''
start: 指定范围的开始值,默认是0
end: 指定范围的结束值
step: 步长
'''

# print(random.randrange(1,10,1))  # 生成1-10之间的随机数
# print(random.randrange(2,101,2)) # 生成2-100之间的随机偶数

# 3.random.random() 生成0-1之间的随机数
# print(random.random())

# 4.将列表中的元素随机排序  random.shuffle()
list1 = [1,2,3,4,5]
random.shuffle(list1)
print(list1)

# 5.随机生成一个指定范围内的实数 random.uniform()  返回的结果是一个浮点数
print(random.uniform(2,8))



