import csv

# 读取csv文件
def read_csv():
    # 打开csv格式的文件
    fp = open(r'C:\python2204\day15\代码\text.csv',mode='r',encoding='utf-8')
    # 读取csv文件中的内容
    reader_info = csv.reader(fp)
    # print(reader_info)
    # 将读取到的内容转换为列表
    print(list(reader_info))
    # 关闭文件
    fp.close()

# read_csv()

# 向csv格式的文件中写入内容
def write_csv():
    fp = open(r'C:\python2204\day15\代码\text.csv',mode='a',encoding='utf-8')
    # 创建写入csv文件的对象
    writer = csv.writer(fp)
    # 1.一次写入一行数据
    # writer.writerow(['浩南',123456,25,'义乌'])
    # 2.一次写入多行数据
    writer.writerows(
        [
            ['钟远平',987654,26,'深圳'],
            ['石宏海',456789,22,'江西'],
            ['刘家豪',765432,25,'东京']
        ]
    )
    # 关闭文件
    fp.close()
write_csv()