# 编码和解码一般用于数据的网络传输
# encode() 编码
# decode() 解密

str1 = '你好Python'
# 编码
print(str1.encode('utf-8'))  # b'\xe4\xbd\xa0\xe5\xa5\xbdPython'
print(str1.encode('gbk'))    # b'\xc4\xe3\xba\xc3Python'

# 解码
str2 = b'\xe4\xbd\xa0\xe5\xa5\xbdPython'
str3 = b'\xc4\xe3\xba\xc3Python'
print(str2.decode('utf-8'))    # 你好Python
print(str3.decode('gbk'))      # 你好Python