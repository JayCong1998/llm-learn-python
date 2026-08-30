# 1.字符串的访问
str1 = '刚刚闭幕的中央经济工作会议是党的二十大后党中央召开的一次非常重要的会议。'
# 通过下标的方式访问字符串
# print(str1[0])
# print(str1[11])

# 2.遍历字符串
'''
# 第一种方式:  i表示字符串中的每个字符
for i in str1:
    print(i)

# 第二种方式:  i表示字符串中字符的下标
for i in range(len(str1)):
    print(str1[i])

# 第三种方式:enumerate()  k表示下标  v表示值
for k,v in enumerate(str1):
    print(k,v)
'''

# 3.字符串的拼接: +   只能是字符串和字符串之间使用 + 拼接
str1 = 'welcome to'
str2 = ' 千锋'
num = 10
# (str1 + str2)
# print(str1 + num)  # 报错

# 4.重复输出字符串  *
# print(str2 * 3)  #  千锋 千锋 千锋

# 5.字符串的切片 字符串[开始下标:结束下标]  0 表示第一个  -1表示最后一个
str3 = 'good good study,day day up'
print(str3[1:5])  # ood
print(str3[1:])   # ood good study,day day up
print(str3[:6])   # good g
print(str3[::-1])  # pu yad yad,yduts doog doog

# 6.使用成员运算符判断字符是否在字符串中 in 和 not in
str4 = 'i love you forever'
print('love' in str4)  # True
print('love' not in str4)  # False