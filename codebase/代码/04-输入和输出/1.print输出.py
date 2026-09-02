# print()
# 简单来说,就是将程序的运行结果显示出来. 在python中使用print() 函数实现, 至于什么是函数,后面会详 细的讲解.
'''
print(self, *args, sep=' ', end='\n', file=None) 参数分别有:
1.self:表示类名,一般指当前类
2. *args 表示可变参数,可以多个,一般表示我们要输出的数据
3.sep 表示输出多个数据时,多个数据之间的间隔 默认值是空格 4. end 表示print()函数执行完毕后,以什么结尾 默认值是换行
5.file 表示文件名称   默认值是None(空)

'''
# 示例:
num = 123
num1 = 4.12
name = "吴京"
love = "打篮球"
print(num,end=" ")
print(num1,name,sep="****")
print(num1,name,love)

