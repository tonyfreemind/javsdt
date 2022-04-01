# -*- coding:utf-8 -*-
import re
from typing import List

from Classes.Static.Const import Const


def find_youma_car(file, list_suren_car: List[str]):
    """
    发现原视频文件名中的有码车牌

    Args:
        file: 全大写的文件名，例如: AVOP-127.MP4
        list_suren_car: 排除素人车牌，例如: ['LUXU', 'MIUM']

    Returns:
        车牌，例如：26ID-020，ABC-123，没找到则返回空
    """
    # (1)T28-123 (2)26ID-020 (3)一般车牌
    if carg := re.search(r'[^A-Z]?(T28)[-_ ]*(\d\d+)', file) \
            or re.search(r'[^\d]?(\d\dID)[-_ ]*(\d\d+)', file) \
            or re.search(r'([A-Z]+)[-_ ]*(\d\d+)', file):
        pref = carg.group(1)
        if pref in list_suren_car or pref in ['HEYZO', 'PONDO', 'CARIB', 'OKYOHOT']:
            return ''
        suf = carg.group(2)
        suf = cut_extra_zero(suf)   # 去掉太多的0
        return f'{pref}-{suf}'
    else:
        return ''


def find_wuma_car(file, list_suren_car):
    """
    发现原视频文件名中的无码车牌

    Args:
        file: 全大写的文件名，例如: CARID-123.MP4
        list_suren_car: 排除素人车牌，例如: ['LUXU', 'MIUM']

    Returns:
        车牌，例如ABC123ABC123，只要是字母数字，全拿着
    """
    # N12345
    if carg := re.search(r'[^A-Z]?(N)(\d\d+)', file):
        car_pref = carg.group(1)
        car_suf = carg.group(2)
    # 123-12345
    elif carg := re.search(r'(\d+)[-_ ](\d\d+)', file):
        car_pref = f'{carg.group(1)}-'
        car_suf = carg.group(2)
    # 只要是字母数字-_，全拿着
    elif carg := re.search(r'([A-Z0-9]+)([-_ ]*)([A-Z0-9]+)', file):
        car_pref = carg.group(1)
        if car_pref in list_suren_car:
            return ''
        car_pref = f'{car_pref}{carg.group(2)}'
        car_suf = carg.group(3)
    # 下面是处理和一般有码车牌差不多的无码车牌，拿到的往往是错误的，仅在1.0.4版本使用过，宁可不整理也不识别个错的
    else:
        return ''
    # 无码就不去0了，去了0和不去0，可能是不同结果
    return f'{car_pref}{car_suf}'


def find_car_suren(file, list_suren_car):
    """
    发现素人车牌，直接从已记录的list_suren_car中来对比

    Args:
        file: 大写后的视频文件名，例如: LUXU-123.MP4
        list_suren_car: 已知的素人车牌，例如['LUXU', 'MIUM']

    Returns:
        发现的车牌    示例: LUXU-123
    """
    if carg := re.search(r'([A-Z][A-Z]+)[-_ ]*(\d\d+)', file):
        car_pref = carg.group(1)
        # 如果用户把视频文件名指定为jav321上的网址，让该视频通过
        if car_pref not in list_suren_car and '三二一' not in file:
            return ''
        # 去掉太多的0，avop00127
        car_suf = cut_extra_zero(carg.group(2))
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


def cut_extra_zero(suf: str):
    """
    去掉太多的0

    Args:
        suf: 车尾

    Returns:
        avop00027 => avop-027
    """
    return f'{suf[:-3].lstrip("0")}{suf[-3:]}' if len(suf) > 3 else suf
