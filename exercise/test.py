import os
import sys

from base.base_box import DataHelper


def strS():
    # split() 拆分
    # str.strip()  # 去除字符串两边的空格
    # str.lstrip() # 去除字符串左边的空格
    # str.rstrip()  #去除字符串右边的空格
    str_01 = "You cannot count on anyone except yourself."
    a = str_01.split(" ")
    print(a)
    b = str_01.split(" ", 3)
    print(b)

def numberlist():
    number_list = [1, 2, 3, 45, 5, 87, 90, 23, 9, 0, 6, 7, 8, 4, 0, 98, -87]
    for i in range(len(number_list)):
        for j in range(len(number_list) - i - 1):
            if number_list[j] > number_list[j + 1]:
                number_list[j], number_list[j + 1] = number_list[j + 1], number_list[j]
    print(number_list)

    for i in range(len(number_list)):
        for j in range(1, len(number_list) - i):
            if number_list[j - 1] < number_list[j]:
                number_list[j - 1], number_list[j] = number_list[j], number_list[j - 1]
    print(number_list)

def file_test(file_name):
    with(open(file_name, mode="wb")) as f:
        print(f)

if __name__ == '__main__':
    pass
    # file_test(file_name = sys.stdout)
    # csv_data = DataHelper().csv_read_data_as_dict("../case/data/csv/zentao_test.csv")
    # print("csv_data = ", csv_data)
    print("hello,python")