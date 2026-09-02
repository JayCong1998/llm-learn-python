# 1.find(查找的内容,开始的位置,结束的位置)  查找字符在字符串中第一次出现的位置,返回的是下标. 若未找到返回-1
str1 = "1234567890qwertyuiopasqdfghjklQWERTYUIOPqASJDFGHJKqLqW"
# print(str1.find('q'))  # 10  未指定开始位置和结束位置,表示从整个字符串查找
# print(str1.find("W"))  # 31

# 指定范围查找
# print(str1.find('o',1,40))  # 18  表示从下标1的位置开始一直到下标为40的位置之间进行查找
# 不存在的情况,返回-1
# print(str1.find('z'))   # -1

# 2.rfind(查找的内容,开始的位置,结束的位置)  查找字符在字符串中最后一次出现的位置,返回的是下标. 若未找到返回-1
print(str1.rfind('q'))   # 52
print(str1.rfind('n'))   # -1

# 指定范围查找
print(str1.rfind('q',10,30))  # 22

# 3.index()功能和find()类似,区别是,若未找到字符串,则直接报错
# print(str1.index('m'))  # ValueError: substring not found
print(str1.index('q'))   # 10

# 4.按照ASCII值进行获取
# max()最大   min()最小
print(max(str1))   # y
print(min(str1))   # 0