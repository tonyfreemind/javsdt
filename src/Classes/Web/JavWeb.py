# -*- coding:utf-8 -*-
import re
from builtins import function

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

    def __init__(self, settings: Ini, headers: Dict[str:str]):
        pattern = type(self).__name__  # 当前类名，表示处理模式，例如“Javdb”
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

    def _get_html(self, url: str):
        """获取html"""
        for _ in range(10):
            try:
                if self._PROXIES:
                    rsp = requests.get(url, headers=self._HEADERS, timeout=(6, 7), proxies=self._PROXIES)
                else:
                    rsp = requests.get(url, headers=self._HEADERS, timeout=(6, 7))
            except requests.exceptions.ProxyError:
                # print(format_exc())
                print(Const.PROXY_ERROR_TRY_AGAIN)
                continue
            except:
                # print(format_exc())
                print(f'{Const.REQUEST_ERROR_TRY_AGAIN}{url}')
                continue
            rsp.encoding = 'utf-8'
            rsp_content = rsp.text
            # 响应内容是否正常
            if self._confirm_rsp(rsp_content):
                return rsp_content
            # Todo 很可能遇到cf
            # print(rsp_content)
            print(Const.HTML_NOT_TARGET_TRY_AGAIN)
        input(f'{Const.PLEASE_CHECK_URL}{url}')

    @staticmethod
    def _confirm_rsp(content: str):
        """
        检查是否是预期响应

        网站可能响应的是cloudflare检测，不是预期的jav网页。

        Returns:
            是否是预期响应
        """
        raise AttributeError(Const.NO_ATTRIBUTE_ERROR)

    def test(self, url: str):
        return self._get_html(url)
