# -*- coding:utf-8 -*-
from openpyxl import load_workbook

from Static.Const import Const
from Enums import ExcelColEnum


def better_dict_genres(website, to_language):
    """
    得到优化的特征字典

    Args:
        website: 哪个网站
        to_language: 简zh/繁cht

    Returns:
        {'伴侶': '招待小姐', ...}
    """
    if website in ['Arzon', 'Dmm', 'Jav321']:
        return {}

    # 使用哪一个网站的特征原数据， 0 db，1 library，2 bus，
    col_jp = ExcelColEnum[website].value
    # 简繁中文，3简体 4繁体
    col_chs = ExcelColEnum[to_language].value

    # 获取Excel文件中的一个sheet中的每一行内容
    rows = load_workbook(filename=Const.EXCEL_GENRE, read_only=True)[Const.YOUMA].rows
    # 原特征 和 优化后的中文特征 对应
    return {row[col_jp].value: row[col_chs].value for row in rows if row[col_jp].value}


# Todo优化
def prefect_genres(dict_genres: dict, genres: list):
    return [dict_genres[i] for i in genres
            if not i.startswith('AV OP')
            and not i.startswith('AVOP')
            and dict_genres[i] != '删除']
