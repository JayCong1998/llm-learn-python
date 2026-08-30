# 在python中,文件的读和写操作是通过打开的文件对象进行处理的.

# 读文件操作:
'''
1.open(文件的路径,打开文件的方式,字符集格式)   打开文件
    打开文件常用的方式:
        r表示read的简写: 读
        w表示write的简写: 写  每次都会重新书写文件中的所有的内容,会把原内容清空
        a表示append的简写: 追加写   在原有的内容的基础上往后追加内容
        b表示bytes的简写: 以字节方式显示文件
2.read()  读取文件内容
3.close() 关闭文件
'''
# 打开文件
# fp = open(r"C:\python2204\day14\代码\1错误和异常.py",mode='r',encoding='utf-8')

# print(fp)  # 表示的是一个文件资源对象

# 读取内容
# print(fp.read())    # 读取所有的内容
# print(fp.read(300))   # 读取前300个字符
# print(fp.readline())   # 表示按照行读取文件,默认读取的是第一行
# print(fp.readlines())    # 表示读取多行,以列表的形式显示
# 关闭文件
# fp.close()


# 写文件: 若文件路径不存在,会自动创建.
'''
操作步骤:
1.打开文件, open(文件的路径,打开文件的方式,字符集格式)
2.向文件中写入内容, write()
3.刷新管道,  flush()
4.关闭文件  close()

# 1.打开文件
# fp = open(r'C:\python2204\day14\代码\aa.txt',mode='w',encoding='utf-8')  # 使用w方式写入会把原内容清空
fp = open(r'C:\python2204\day14\代码\aa.txt',mode='a',encoding='utf-8')   # 经常用
# 2.向文件中写入内容
fp.write('苹果,梨,香蕉')
# 3.刷新管道(缓存)
fp.flush()
# 4.关闭文件资源对象
fp.close()
'''

# 自动关闭文件   with....as.....
with open(r'C:\python2204\day14\代码\1错误和异常.py',mode='r',encoding='utf-8') as fp:
    print(fp.read())




