# 第一种方式:
'''
占位符: %
整数:  %d
小数:  %f
字符串: %s
3位小数:  %.3f
2位小数: %.2f
'''
name = '清华'
age = 23
height = 170
money = 38.6435
print("姓名:%s,年龄:%d,身高:%d,财富:%.2f"%(name,age,height,money))

# 第二种方式: f"{变量名}"
print(f"姓名:{name},年龄:{age},身高:{height},财富:{round(money,2)}")
