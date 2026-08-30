# 1.封装函数,计算1-100之间所有数字的和
def he():
    sum = 0
    for i in range(1,101):
        sum += i
    print(sum)
#he()

# 2.封装一个函数,将1-100之间个位数是3的数字返回
def demo():
    for i in range(1,101):
        if i % 10 == 3:
            # print(i)
            return i
print(demo())