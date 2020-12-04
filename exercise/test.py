# split()
# strip()
# str.strip()  # 去除字符串两边的空格
# str.lstrip() # 去除字符串左边的空格
# str.rstrip()  #去除字符串右边的空格
str_01 = "You cannot count on anyone except yourself."
a = str_01.split(" ")
print(a[-1])
b = str_01.split(" ", 3)
print(b[-1].strip("o"))

