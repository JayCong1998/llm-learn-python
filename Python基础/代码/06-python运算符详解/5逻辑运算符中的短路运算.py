# and 或者 or的短路运算
# print(12 and 43)   # 43
# print(43 and 12)   # 12
# print(43 and 0)    # 0
# print(0 and 43)    # 0    # 短路运算
'''
逻辑操作符and 和or 也称作短路操作符(short-circuitlogic)或者惰性求值(lazy evaluation)：它们的参数从左向右解析，一旦结果可以确定就停止。
因为and运算符必须所有的运算数都是True才会把所有的运算数都解析，并且返回最后一个变量.
而或逻辑(or)，即只要有一个是True，即停止解析运算数，返回最近为True的变量，
'''

print(12 or 43)   # 12
print(43 or 12)   # 43
print(43 or 0)    # 43
print(0 or 43)    # 43