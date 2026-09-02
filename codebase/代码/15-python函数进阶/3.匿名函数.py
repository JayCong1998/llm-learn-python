# 匿名函数: 是指不再使用def关键字声明的函数,使用lambda来创建函数

'''
特点:
1.lambda只是一个表达式,比普通函数简单
2.lambda一般只会书写一行,包含了参数 函数体和返回值
'''
def fn(n):
    return n**2
res = fn(3)
print(res)  # 9

# 使用匿名函数的方式实现上述的功能:
result = lambda n:n ** 2
print(result(3))  # 9

# 使用匿名函数计算两个数字的乘积:
fn2 = lambda x,y:x*y
print(fn2(12,4))  # 48

