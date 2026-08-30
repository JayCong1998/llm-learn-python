# 需求: 输出100遍的hello world
'''
num = 0
while num <= 1000:
    print(num,'次','嘉豪跳桑巴舞')
    num += 1
'''

# while循环的基础语法:
'''
1.初始化的表达式
while 2.条件表达式:
    循环体(重复执行的程序)
    3.更新的表达式
    
注意: 初始化的表达式,在整个循环中只会在第一次循环时执行一次.
# 1. 使用循环输出1-10之间所有的数字 :  1 2 3 4 5 6 7 8 9 10
num = 1
while num <= 10:
    print(num)
    num += 1


# 2.使用while循环输出1-100之间所有的偶数
num = 1
while num <= 100:
    if num % 2 == 0:
        print(num)
    num += 1

# 3.使用while循环输出1-100之间所有的奇数
num = 1
while num <= 100:
    if num % 2 != 0:
        print(num)
    num += 1


# 4.使用循环的方式计算1-100之间所有的数字的和
# 定义一个变量表示1-100之间数字的和
sum = 0
num = 1
while num <= 100:
    sum = sum + num
    num += 1
print('1-100之间的数字的和是:',sum)

# 5.使用while循环计算1-100之间所有的偶数的和
sum = 0
num = 1
while num <= 100:
    if num % 2 == 0:
        sum = sum + num
    num += 1
print('1-100之间的所有的偶数的和是:',sum)


# 6.使用while循环计算1-100之间所有的奇数的和
sum = 0
num = 1
while num <= 100:
    if num % 2 != 0:
        sum = sum + num
    num += 1
print('1-100之间的所有的奇数的和是:',sum)

# 7.统计 1-1000之间能够被9整除的数字的个数
count = 0  # 定义变量,用于统计满足条件的数字的个数
num = 1
while num <= 1000:
    if num % 9 == 0:
        count += 1
    num += 1
print('1-1000之间能够被9整除的数字的个数是:',count)
'''
# 8.统计1-1000之间能够被9整除并且是偶数的个数
count = 0
num = 1
while num <= 1000:
    if num % 9 == 0 and num % 2 == 0:
        count += 1
    num += 1
print('1-1000之间能够被9整除并且是偶数的个数是:',count)