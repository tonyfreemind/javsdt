# -*- coding:utf-8 -*-
import time

from Classes.Enums import CompletionStatusEnum, CutTypeEnum


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
        """2 原始车牌"""

        self.Series = ''
        """3 系列"""

        self.Title = ''
        """4 原标题"""

        self.TitleZh = ''
        """5 简体中文标题"""

        self.Plot = ''
        """6 剧情概述"""

        self.PlotZh = ''
        """7 简体剧情"""

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

        self.Score = 0
        """14 评分"""

        self.CoverDb = ''
        """15 封面Db"""

        self.CoverLibrary = ''
        """16 封面Library"""

        self.CoverBus = ''
        """17 封面Bus"""

        self.CutType = CutTypeEnum.left.value
        """18 裁剪方式"""

        self.Javdb = ''
        """19 db编号"""

        self.Javlibrary = ''
        """20 library编号"""

        self.Javbus = ''
        """21 bus编号"""

        self.Arzon = ''
        """22 arzon编号"""

        self.CompletionStatus = CompletionStatusEnum.unknown.value
        """23 完成度，三大网站为全部"""

        self.Version = 1
        """24 版本"""

        self.Genres = []
        """24 类型"""

        self.Actors = []
        """25 演员们"""

        self.Modify = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        """26 修改时间"""

        self.__dict__.update(kwargs)

    def prefect_completion_status(self):
        """
        更新一下整理的完成度

        整理流程的末尾，更新一下这部影片成功收集到哪几个网站的数据
        """
        if self.Javdb:
            if self.Javlibrary:
                if self.Javbus:
                    completion = CompletionStatusEnum.db_library_bus.value  # 三个网站全部收集整理
                else:
                    completion = CompletionStatusEnum.db_library.value
            else:
                if self.Javbus:
                    completion = CompletionStatusEnum.db_bus.value
                else:
                    completion = CompletionStatusEnum.only_db.value
        else:
            if self.Javlibrary:
                if self.Javbus:
                    completion = CompletionStatusEnum.library_bus.value
                else:
                    completion = CompletionStatusEnum.only_library.value
            else:
                if self.Javbus:
                    completion = CompletionStatusEnum.only_bus.value
                else:
                    completion = CompletionStatusEnum.unknown.value
        self.CompletionStatus = completion
