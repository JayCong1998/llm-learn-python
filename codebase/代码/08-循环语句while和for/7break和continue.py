# break的作用: 跳出整个循环
num = 1
while num <= 10:
    if num == 3:
        num += 1
        break
    print(num)
    num += 1
'''
1
2
'''
print('+++++++++++++++')
# continue的作用: 用于跳出当前循环
num1 = 1
while num1 <= 10:
    if num1 == 3:
        num1 += 1
        continue
    print(num1)
    num1+=1
'''
1
2
4
5
6
7
8
9
10


'''
