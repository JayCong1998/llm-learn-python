# 1.isupper() 检测字符串中的字母是否全部大写
str1 = "1234asdfgXCVBNM"
str2 = "SDFGH98765"
print(str1.isupper())  # False
print(str2.isupper())  # True

# 2.islower() 检测字符串中的字母是否全部小写
str3 = "rtyui9876"
str4 = "dfghjMNBVC3456"
print(str3.islower())   # True
print(str4.islower())   # False

# 3.isdigit() 检测字符串是否是全部是数字组成
str5 = '12345'
str6 = "dfghj98765FGHJ"
print(str5.isdigit())   # True
print(str6.isdigit())   # False

# 4.istitle() 检测字符串中的单词首字母是否大写
str7 = 'hello world'
str8 = 'Good Night'
print(str7.istitle())  # False
print(str8.istitle())  # True

# 5.isalpha()  检测字符串是否只有文字和字母组成
str9 = '你好everyone'
str10 = '中国876dfghjXCVB'
print(str9.isalpha())   # True
print(str10.isalpha()) # False