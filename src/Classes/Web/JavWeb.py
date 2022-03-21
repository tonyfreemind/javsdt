# -*- coding:utf-8 -*-
import re
import requests
from typing import List, Dict
# from traceback import format_exc

from Classes.Enums import ScrapeStatusEnum
from Classes.Errors import SpecifiedUrlError
from Classes.Const import Const
from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Config import Ini
from Functions.Metadata.Genre import better_dict_genres, prefect_genres


class JavWeb(object):
    """网站刮削工具父类"""

    def __init__(self, settings: Ini, pattern: str, headers: Dict[str:str]):
        tuple_temp: tuple[str, dict] = settings.web_url_proxy(pattern)

        self._URL: str = tuple_temp[0]
        """网址"""

        self._PROXIES: dict[str:str] = tuple_temp[1]
        """代理"""

        self._DICT_GENRES = better_dict_genres(pattern, settings.to_language)
        """优化后的genres"""

        self._HEADERS = headers
        """请求头\n\n不同网站会有不同要求"""

        self._is_only: bool = True
        """是否 刮削到唯一结果\n\n如果有多个结果，需警告用户"""

        self._item = Const.CAR_DEFAULT
        """车牌在网站上item\n\n例如ABC-123_2011-11-11，如果刮削成功则将它更新为正确值，交给jav_model"""
