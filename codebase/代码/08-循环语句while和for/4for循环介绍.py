# 语法:
'''
for 变量名 in 序列:
    循环体(重复执行的程序)
'''

'''
# 1.使用for循环输出1-1000之间的所有的数字
for i in range(1,1001):
    print(i)
'''
# 2.使用for循环输出1-1000之间所有的奇数
'''
for j in range(1,1001,2):
    print(j)
或者

for j in range(1,1001):
    if j % 2 != 0:
        print(j)

# 3.使用for循环输出1-1000之间所有的偶数
for j in range(2,1001,2):
    print(j)
'''
'''
# 4.使用for循环计算1-100之间所有的数字的和
sum = 0
for i in range(1,101):
    sum += i
print(sum)
'''
# 使用for循环遍历列表中的元素
stars = ['后羿','安吉拉','嫦娥','甄姬','老猪','孙悟空']
'''
print(stars)  # ['后羿', '安吉拉', '嫦娥', '甄姬', '老猪', '孙悟空']
# 访问列表中的元素,通过下标(索引)来访问.下标默认从0开始
print(stars[0])   # 后羿
print(stars[3])   # 甄姬
print(stars[-1])  # 孙悟空
print(stars[-2])  # 老猪

# len() 表示获取列表元素的长度
print(len(stars))  # 6
'''
# 使用for循环遍历列表中的元素
'''
# 第一种方式:   i表示列表中的每个元素
for i in stars:
    print(i)

# 第二种方式:  j表示列表中的每个元素对应的下标
for j in range(len(stars)):
    print(j,stars[j])
'''
# 第三种方式:enumrate()  k表示列表中每个元素的索引,v表示列表中每个元素的值
for k,v in enumerate(stars):
    print(k,v)



