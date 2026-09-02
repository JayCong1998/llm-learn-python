# 1.split()  以指定字符对目标字符串进行分割(默认是空格)
str1 = "this is a string example...."
str2 = "this*is*a*string*example...."
# 使用空格分割
# print(str1.split())  # ['this', 'is', 'a', 'string', 'example....']
# 使用指定字符切割
# print(str2.split('*'))  # ['this', 'is', 'a', 'string', 'example....']

# 2.splitlines() 按照行分割
str3 = """
悟道休言天命,
修行务取真经.
一悲一喜一枯荣,
哪个前生注定.
"""
# print(str3)
# print(str3.splitlines())  # ['', '悟道休言天命,', '修行务取真经.', '一悲一喜一枯荣,', '哪个前生注定.']

# 3.合并  join()  以指定字符合并字符串
ss1 = '-'
list1 = ['hello','everybody','nice','to','meet','you']
print(ss1.join(list1))  # hello-everybody-nice-to-meet-you





