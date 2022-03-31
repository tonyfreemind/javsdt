# -*- coding:utf-8 -*-
from Datetime import time_now
from Enums import CompletionStatusEnum, CutTypeEnum
from Functions.Metadata.Car import extract_pref


class JavData(object):
    """
    一部影片的元数据

    在整理流程中逐渐从各大网站充实数据，最终以json格式写到本地

    Args:
        **kwargs (dict): 用于初始化成员变量的字典
    """

    def __init__(self, **kwargs):
        self.Car = ''
        """1 车牌"""

        self.CarOrigin = ''
        """2 原始车牌\n\ndmm上记录的车牌"""

        self.Series = ''
        """3 系列"""

        self.Title = ''
        """4 原标题"""

        self.TitleZh = ''
        """5 简中标题"""

        self.Plot = ''
        """6 剧情概述"""

        self.PlotZh = ''
        """7 简中剧情"""

        self.Review = ''
        """8 剧评"""

        self.Release = '1970-01-01'
        """9 发行日期"""

        self.Runtime = 0
        """10 时长"""

        self.Director = ''
        """11 导演"""

        self.Studio = ''
        """12 制造商"""

        self.Publisher = ''
        """13 发行商"""

        self.Score = 0.0
        """14 评分\n\n10分制"""

        self.CoverDb = ''
        """15 封面Db"""

        self.CoverLibrary = ''
        """16 封面Library"""

        self.CoverBus = ''
        """17 封面Bus"""

        self.CoverDmm = ''
        """18 封面Dmm"""

        self.CutType = CutTypeEnum.left.value
        """19 裁剪方式"""

        self.JavDb = ''
        """20 db编号"""

        self.JavLibrary = ''
        """21 library编号"""

        self.JavBus = ''
        """22 bus编号"""

        self.Arzon = ''
        """23 arzon编号"""

        self.CompletionStatus = CompletionStatusEnum.unknown.value
        """24 完成度，三大网站为全部"""

        self.Version = 1
        """25 版本"""

        self.Genres = []
        """26 类型"""

        self.Actors = []
        """27 演员们"""

        self.Modify = time_now()
        """28 修改时间"""

        self.__dict__.update(kwargs)

    # Todo 这个pref会不会被放进json里?
    @property
    def Pref(self):
        """车牌前缀，车尾\n\n例如IPZ"""
        return extract_pref(self.Car)

    def prefect_completion_status(self):
        # sourcery skip: assign-if-exp, merge-else-if-into-elif
        """
        更新一下整理的完成度

        这部影片成功收集到哪几个网站的数据，在整理流程的末尾更新一下标志
        """
        if self.JavDb:
            if self.JavLibrary:
                if self.JavBus:
                    completion = CompletionStatusEnum.db_library_bus.value  # 三个网站全部收集整理
                else:
                    completion = CompletionStatusEnum.db_library.value
            else:
                if self.JavBus:
                    completion = CompletionStatusEnum.db_bus.value
                else:
                    completion = CompletionStatusEnum.only_db.value
        else:
            if self.JavLibrary:
                if self.JavBus:
                    completion = CompletionStatusEnum.library_bus.value
                else:
                    completion = CompletionStatusEnum.only_library.value
            else:
                if self.JavBus:
                    completion = CompletionStatusEnum.only_bus.value
                else:
                    completion = CompletionStatusEnum.unknown.value
        self.CompletionStatus = completion
