# -*- coding:utf-8 -*-
import os
import xlrd


# 功能: 得到优化的特征字典
# 参数: 用户在用哪个exe（对应要在表格中取哪一列） ，简繁中文to_language   示例: Javbus有码 ，zh
# 返回: 优化的特征字典
# 辅助: xlrd
def better_dict_genres(website, to_language):
    # 返回一个字典 {'伴侶': '招待小姐'}
    dict_genres = {}
    # 使用哪一个网站的特征原数据 0 javdb，1 javlibrary， 2 javbus
    if website == 'db':
        col = 0
    elif website == 'library':
        col = 1
    elif website == 'bus':
        col = 2
    else:
        col = 0
    # 简繁中文，3简体 4繁体
    col_chinese = 3 if to_language == 'zh' else 4
    # 打开Excel文件
    path_xlsx = '【特征对照表】.xlsx' if os.path.exists('StaticFiles/【特征对照表】.xlsx') else '../../【特征对照表】.xlsx'
    # xlsxPath = '【特征对照表】.xlsx'
    excel = xlrd.open_workbook(path_xlsx)
    sheet = excel.sheet_by_name('有码')  # excel中的某一sheet
    row = sheet.nrows  # 总行数
    for i in range(1, row):
        list_row = sheet.row_values(i)  # i行的list
        if list_row[col]:
            dict_genres[list_row[col]] = list_row[col_chinese]  # 原特征 和 优化后的中文特征 对应
    return dict_genres


def better_dict_youma_genres(to_language):
    return better_dict_genres("db", to_language), \
           better_dict_genres("library", to_language), \
           better_dict_genres("bus", to_language),


def prefect_genres(dict_genres: dict, genres: list):
    return [dict_genres[i] for i in genres
            if not i.startswith('AV OP')
            and not i.startswith('AVOP')
            and dict_genres[i] != '删除']

# test
# print(better_dict_genre('Javlibrary', 'cht'))
