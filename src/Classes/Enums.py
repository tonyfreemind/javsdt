# -*- coding: UTF-8 -*-
from enum import IntEnum


class ScrapeStatusEnum(IntEnum):
    """执行刮削的结果"""

    interrupted = 0
    """终止"""
    success = 1
    """成功"""

    db_multiple_search_results = 2
    """db存在多个搜索结果"""
    db_not_found = 3
    """db没找到"""

    library_multiple_search_results = 4
    """library存在多个搜索结果"""
    library_not_found = 5
    """library没找到"""

    bus_multiple_search_results = 6
    """bus存在多个搜索结果"""
    bus_not_found = 7
    """bus没找到"""

    arzon_exist_but_no_plot = 8
    """arzon存在搜索结果但页面上没有简介"""
    arzon_not_found = 9
    """arzon没找到"""


class CompletionStatusEnum(IntEnum):
    """刮削完成度\n\n在哪几个网站拿到了数据"""

    unknown = 0
    """未知\n\n默认状态"""

    only_db = 1,
    only_library = 2
    only_bus = 3

    db_library = 4
    db_bus = 5
    db_library_bus = 6

    library_bus = 7


class CutTypeEnum(IntEnum):
    """fanart切割为poster的规则"""

    unknown = 0
    left = 1
    middle = 2
    right = 3
    custom = 4


class PatternEnum():
    """暂时没用"""
    youma = 1
    wuma = 2
    suren = 3


class ExcelColEnum(IntEnum):
    """执行刮削的结果"""

    JavDb = 0
    """A列 db特征"""

    JavLibrary = 1
    """B列 library特征"""

    JavBus = 2
    """C列 bus特征"""

    Zh = 3
    """D列 简体中文"""

    Cht = 4
    """F列 繁体中文"""

    def get_state(value: int):
        for member in ExcelColEnum:
            if value == member.value:
                print(member)

if __name__ == '__main__':
    ExcelColEnum.get_state(1)