# 1.strip()  去除字符串两边的指定字符(默认去除的是空格)
str1 = " today is a nice day "
str2 = "** today is a nice day ***"

print(str1)
# print(str2)
# 去除字符串两边的空格
# print(str1.strip())

# 去除指定的字符  *
# print(str2)
# print(str2.strip('*'))

# 2.lstrip() 去除左边的指定字符(默认去除的是空格)
# print(str1.lstrip())
# print(str2)
# print(str2.lstrip('*'))

# 3.rstrip() 去除右边的指定字符(默认去除的是空格)
print(str1.rstrip())
print(str2)
print(str2.rstrip('*'))