import os  # 导入os模块

# 1.listdir()   查看指定目录下面所有的文件和文件夹
# print(os.listdir('C:\python2204\day10'))

# 2.curdir   查看当前目录
'''
dos命令行中:
. 表示当前目录
.. 表示上级目录
'''

# print(os.curdir)   # .

# 3.getcwd()  查看当前路径
# print(os.getcwd())   # C:\python2204\day11\代码

# 4. mkdir()  创建文件夹(不能创建已经存在的文件夹)
# os.mkdir(r'C:\python2204\day11\岑石')

# 5.makedirs()  递归式的创建文件夹
# os.makedirs(r'C:\python2204\day11\a\b\c')

# 6.rmdir()  删除文件夹(只能删除空文件夹)
# os.rmdir(r'C:\python2204\day11\test')
# os.rmdir(r'C:\python2204\day11\a')  # OSError: [WinError 145] 目录不是空的。: 'C:\\python2204\\day11\\a'

# 7. rename('原文件名','新文件名')         重命名文件或者文件夹
# os.rename(r'C:\python2204\day11\a',r'C:\python2204\day11\包含子文件夹')
# os.rename(r'C:\python2204\day11\test.txt',r'C:\python2204\day11\测试重命名.txt')

# 8. remove()  删除文件
# os.remove(r'C:\python2204\day11\demo.txt')

# 9.os.path.join()  拼接路径
# print(os.path.join('C:\python2204\day11','拼接路径.py'))   # C:\python2204\day11\拼接路径.py

# 10.os.path.split()  拆分路径(拆分目录和文件)
# print(os.path.split('C:\python2204\day11\测试重命名.txt'))   # ('C:\\python2204\\day11', '测试重命名.txt')

# 11.os.path.splittext()   拆分文件名和扩展名
# print(os.path.splitext('C:\python2204\day11\笔记\Day11笔记.md'))    # ('C:\\python2204\\day11\\笔记\\Day11笔记', '.md')

# 12. os.path.abspath()            获取绝对路径
# print(os.path.abspath('1栈.py'))    # C:\python2204\day11\代码\1栈.py


# 13.os.path.getsize()             获取文件的大小
# print(os.path.getsize(r'C:\python2204\day11\代码\1栈.py'))   # 587

# 14. os.path.isfile()          判断是否是文件,若是返回True,若不是,返回False.
# print(os.path.isfile(r'C:\python2204\day11\代码\1栈.py'))   # True
# print(os.path.isfile(r'C:\python2204\day11\代码'))   # False

# 15.os.path.isdir()   判断是否是文件夹,若是返回True,若不是返回False
# print(os.path.isdir(r'C:\python2204\day11\代码\1栈.py'))   # False
# print(os.path.isdir(r'C:\python2204\day11\代码'))    # True

# 16. os.path.exists()  判断文件或者文件夹是否存在,若存在返回True,若不存在返回False
# print(os.path.exists('1栈.py'))  # True
# print(os.path.exists('demo.py'))  # False

# 17.os.path.dirname  获取路径的文件夹部分
# print(os.path.dirname(r'C:\python2204\day11\代码\1栈.py'))   # C:\python2204\day11\代码

# 18.os.path.basename  获取路径的文件名部分
print(os.path.basename(r'C:\python2204\day11\代码\1栈.py'))   # 1栈.py





