import datetime

# 1.获取当前的日期对象
date = datetime.datetime.now()
print(date)   # 2022-12-30 10:15:32.163519

# 2.设置日期对象
date1 = datetime.datetime(year=2021,month=12,day=23,hour=12,minute=34,second=45)
print(date1)  # 2021-12-23 12:34:45

print(type(date1))  # <class 'datetime.datetime'>
# 查看年份,月份,日期
print(date1.year,date1.month,date1.day)  # 2021 12 23

# 查看小时,分钟,秒
print(date1.hour,date1.minute,date1.second)  # 12 34 45

# 将datetime类型转换为字符串类型
print(date1.strftime("%Y{}%m{}%d{}").format("年","月","日"))   # 2021年12月23日

# fromtimestamp() 将时间戳转换为日期对象
print(datetime.datetime.fromtimestamp(12346476889))   # 2361-03-31 08:54:49

# 时间差
d1 = datetime.datetime(2022,12,31)
d2 = datetime.datetime(2022,1,23)
print(d1 - d2)   # 342 days, 0:00:00
print(d2 - d1)  # -342 days, 0:00:00

# 设置时间差   timedelta
dt = datetime.timedelta(days=5,hours=4)
print(d1 + dt)   # 2023-01-05 04:00:00
print(d1 - dt)   # 2022-12-25 20:00:00

