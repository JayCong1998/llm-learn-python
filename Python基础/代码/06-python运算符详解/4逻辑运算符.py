# 逻辑运算符主要是有三个: and(与)  or(或)  not(非)
# and: 只有当表达式两边为真,则整个表达式为真
'''
print(True and True)   # True
print(True and False)  # False
print(False and True)  # False
print(False and False) # False

# or: 只要有一个表达式为真,则整个表达式为真
print(True or True)   # True
print(True or False)  # True
print(False or True)  # True
print(False or False) # False
'''
# not: 表示对原来的结果取反
print(not True)  # False
print(not False) # True
# 在python中有几种特殊的数据转换为布尔类型为False.  比如: [] '' "" 0 ()  None 0.0  {}
'''
[] 表示空列表  
() 表示空元祖
{} 表示空字典
'' 或者 "" 表示空字符串
None 表示空
'''
print(not [])  # True
print(not ())  # True
print(not '')  # True
print(not "")  # True
print(not 0)   # True
print(not 0.0) # True
print(not None) # True
print(not {})   # True