# -*- coding:utf-8 -*-
import re
from typing import List

from Const import Const


def find_car_youma(file, list_suren_car: List[str]):
    """
    发现原视频文件名中的有码车牌

    Args:
        file: 全大写的文件名，例如: AVOP-127.MP4
        list_suren_car: 要排除的素人车牌，例如: ['LUXU', 'MIUM']

    Returns:
        车牌，例如：ID-26020，没找到则返回空
    """
    # car_pref 车牌前缀 ABP-，带横杠；car_suf，车牌后缀 123。
    # 处理T28-
    if re.search(r'[^A-Z]?T28[-_ ]*\d\d+', file):
        car_pref = 'T28-'
        car_suf = re.search(r'T28[-_ ]*(\d\d+)', file).group(1)
    # 处理20ID-020
    elif re.search(r'[^\d]?\d\dID[-_ ]*\d\d+', file):
        carg = re.search(r'(\d\dID)[-_ ]*(\d\d+)', file)
        car_pref = f'{carg.group(1)}-'
        car_suf = carg.group(2)
    # 一般车牌
    elif re.search(r'[A-Z]+[-_ ]*\d\d+', file):
        carg = re.search(r'([A-Z]+)[-_ ]*(\d\d+)', file)
        pref = carg.group(1)
        if pref in list_suren_car or pref in ['HEYZO', 'PONDO', 'CARIB', 'OKYOHOT']:
            return ''
        car_pref = f'{pref}-'
        car_suf = carg.group(2)
    else:
        return ''
    # 去掉太多的0，avop00027 => avop-027
    if len(car_suf) > 3:
        car_suf = f'{car_suf[:-3].lstrip("0")}{car_suf[-3:]}'
    return f'{car_pref}{car_suf}'


# 功能: 发现原视频文件名中的无码车牌
# 参数: 被大写后的视频文件名，素人车牌list_suren_car    示例: ABC123ABC123.MP4    ['LUXU', 'MIUM']
# 返回: 发现的车牌    示例: ABC123ABC123，只要是字母数字，全拿着
# 辅助: re.search
def find_car_wuma(file, list_suren_car):
    # N12345
    if re.search(r'[^A-Z]?N\d\d+', file):
        car_pref = 'N'
        car_suf = re.search(r'N(\d\d+)', file).group(1)
    # 123-12345
    elif re.search(r'\d+[-_ ]\d\d+', file):
        carg = re.search(r'(\d+)[-_ ](\d\d+)', file)
        car_pref = f'{carg.group(1)}-'
        car_suf = carg.group(2)
    # 只要是字母数字-_，全拿着
    elif re.search(r'[A-Z0-9]+[-_ ]?[A-Z0-9]+', file):
        carg = re.search(r'([A-Z0-9]+)([-_ ]*)([A-Z0-9]+)', file)
        car_pref = carg.group(1)
        # print(car_pref)
        if car_pref in list_suren_car:
            return ''
        car_pref = f'{car_pref}{carg.group(2)}'
        car_suf = carg.group(3)
    # 下面是处理和一般有码车牌差不多的无码车牌，拿到的往往是错误的，仅在1.0.4版本使用过，宁可不整理也不识别个错的
    # elif search(r'[A-Z]+[-_ ]?\d+', file):
    #     carg = search(r'([A-Z]+)([-_ ]?)(\d+)', file)
    #     car_pref = carg.group(1)
    #     if car_pref in list_suren_car:
    #         return ''
    #     car_pref = f'{car_pref}{carg.group(2)}'
    #     car_suf = carg.group(3)
    else:
        return ''
    # 无码就不去0了，去了0和不去0，可能是不同结果
    # if len(car_suf) > 3:
    #     car_suf = f'{car_suf[:-3].lstrip("0")}{car_suf[-3:]}'
    return f'{car_pref}{car_suf}'


# 功能: 发现素人车牌，直接从已记录的list_suren_car中来对比
# 参数: 大写后的视频文件名，素人车牌list_suren_car    示例: LUXU-123.MP4    ['LUXU', 'MIUM']
# 返回: 发现的车牌    示例: LUXU-123
# 辅助: re.search
def find_car_suren(file, list_suren_car):
    carg = re.search(r'([A-Z][A-Z]+)[-_ ]*(\d\d+)', file)  # 匹配字幕车牌
    if carg:
        car_pref = carg.group(1)
        # 如果用户把视频文件名指定为jav321上的网址，让该视频通过
        if car_pref not in list_suren_car and '三二一' not in file:
            return ''
        car_suf = carg.group(2)
        # 去掉太多的0，avop00127
        if len(car_suf) > 3:
            car_suf = f'{car_suf[:-3].lstrip("0")}{car_suf[-3:]}'
        return f'{car_pref}-{car_suf}'
    else:
        return ''


def find_car_fc2(file):
    subtitle_carg = re.search(r'FC2[^\d]*(\d+)', file)  # 匹配字幕车牌
    return f'FC2-{subtitle_carg.group(1)}' if subtitle_carg else ''


def get_suren_cars():
    """
    得到素人车牌集合

    Returns:
        list 素人车牌
    """
    try:
        with open(Const.TXT_SUREN_CARS, 'r', encoding="utf-8") as f:
            list_suren_cars = list(f)
    except:
        input(f'“{Const.TXT_SUREN_CARS}”读取失败！')
    list_suren_cars = [i.strip().upper() for i in list_suren_cars if i != '\n']
    return list_suren_cars


def tran_car_same_with_bus_arzon(car: str):
    """
    车牌转换

    ID这一个类的车牌在不同网站的表现形式不一样，将library和db上的车牌转换为适用于bus和arzon的车牌。

    Args:
        car: ID-26123

    Returns:
        26ID-123
    """
    if carg := re.search(r'ID-(\d\d)(\d+)', car):
        return f'{carg.group(1)}ID-{carg.group(2)}'
    else:
        return car


def tran_car_for_search_bus_arzon(car: str):
    """
    车牌转换

    ID这一个类的车牌在不同网站的表现形式不一样，将library和db上的车牌转换为适用于在bus和arzon搜索的车牌。

    Args:
        car: ID-26123

    Returns:
        26ID123
    """
    return tran_car_same_with_bus_arzon(car).replace("-", "")


def extract_pref(car: str):
    """
    从车牌中提取前缀(车头)

    Args:
        car: ABC-123

    Returns:
        ABC
    """
    return car.split('-')[0].upper() \
        if '-' in car \
        else re.search(r'(.+?)\d', car).group(1).upper()


def extract_suf(car):
    """
    从车牌中提取后缀数字（车尾）

    Args:
        car: ID-26012

    Returns:
        ID-26012 => 26123 ABC-012 => 12
    """
    if '-' in car:
        return int(re.search(r'-(\d+)\w*', car).group(1))
    else:
        return int(re.search(r'(\d+)\w*', car).group(1))
