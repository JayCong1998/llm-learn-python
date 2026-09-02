# 关系运算符: 作用是 比较大小 得到的结果是布尔类型.[如果表达式成立,则返回True,如果不成立,返回False]
# > < >= <= ==(等于)  !=(不等于)

# 布尔类型的值有两个: True(表示真)  False(表示假)
a = 32
b = 14
c = 32

print(a > b)   # True
print(a < b)   # False
print(a >= b)  # True
print(a <= b)  # False
print(a == c)  # True
print(a != b)  # True

# 示例:
if a > b:
    print('a是一个大于b的数字')

