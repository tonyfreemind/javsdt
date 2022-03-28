# -*- coding: UTF-8 -*-
from enum import IntEnum


class ScrapeStatusEnum(IntEnum):
    """执行刮削的结果"""

    not_found = 0
    """没找到"""

    success = 1
    """成功"""

    multiple_results = 2
    """存在多个搜索结果"""

    exist_but_no_want = 3
    """
    有搜索结果，但结果页面上没有想要的内容
    
    比如arzon找得到车牌，但页面上没有简介
    """


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

    zh = 3
    """D列 简体中文"""

    cht = 4
    """F列 繁体中文"""
