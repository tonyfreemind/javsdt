# -*- coding:utf-8 -*-
import re
import ssl

import requests
from typing import Dict
from traceback import format_exc

from requests.adapters import HTTPAdapter

from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Const import Const
from Classes.Config import Ini
from Enums import ScrapeStatusEnum
from Errors import SpecifiedUrlError
from Functions.Metadata.Genre import better_dict_genres, prefect_genres


class JavWeb(object):
    """网站刮削工具父类"""

    def __init__(self, settings: Ini, appoint_symbol: str, headers: Dict[str, str]):
        if type(self) is JavWeb:
            raise Exception("<JavWeb>不能被实例化")

        pattern = self.__class__.__name__  # 当前类名，表示处理模式，例如“JavBus”
        tuple_temp: tuple[str, dict] = settings.web_url_proxy(pattern)

        self._URL: str = tuple_temp[0]
        """网址"""

        self._requests = self._create_session(tuple_temp[1], headers)
        """requests服务"""

        self._DICT_GENRES = better_dict_genres(pattern, settings.to_language)
        """优化后的genres"""

        self._HEADERS = headers
        """请求头\n\n不同网站会有不同要求"""

        self._APPOINT_SYMBOL = appoint_symbol
        """
        指定网址的标志
        
        比如
        """

        self._is_only: bool = True
        """是否 刮削到唯一结果\n\n如果有多个结果，需警告用户"""

        self._item = Const.CAR_DEFAULT
        """
        车牌在网站上的item
        
        例如ABC-123_2011-11-11
        如果刮削成功则将它更新为正确值，交给jav_model。
        """

    def scrape(self, jav_file: JavFile, jav_data: JavData):
        """
        获取网站上的内容

        Args:
            jav_file: jav视频文件对象
            jav_data: jav元数据对象

        Returns:
            刮削结果
        """
        # region 1重置状态
        self._reset()
        # endregion

        # region 2找到网页
        html = self._find_target_html(jav_file.Name, jav_file.Car)
        """当前车牌所在的html"""
        if not html:
            return ScrapeStatusEnum.not_found
        # endregion

        # region 3摘取信息
        self._select_normal(jav_data)
        return self._select_special(html, jav_data)
        # endregion

    @staticmethod
    def _create_session(proxies: Dict[str, str], headers: Dict[str, str]):
        rqs = requests.Session()
        rqs.proxies = proxies
        rqs.headers = headers
        return rqs

    def _find_target_html(self, name: str, car: str):
        """
        获取车牌所在html

        三种方式直至成功找到html：(1)用户指定，则用指定网址；(2)直接访问 网址+车牌；（3）搜索车牌。

        Args:
            name: 视频文件名
            car: 当前处理的车牌

        Returns:
            html
        """
        if self._APPOINT_SYMBOL in name:
            return self._appoint(name)
        else:
            return self._search(car)

    def _appoint(self, name: str):
        """
        从用户指定的网址中获取目标html

        用户将视频命名为“ABC-123公交车DEF-456_2011-11-11.mp4"，即指定为”https://www.buscdn.me/DEF-456_2011-11-11"。

        Args:
            name: 视频文件名

        Returns:
            目标html
        """
        item_appointg = re.search(rf'{self._APPOINT_SYMBOL}(.+?)\.', name)
        if not item_appointg:
            raise SpecifiedUrlError(f'{Const.SPECIFIED_FORMAT_ERROR} {self.__class__.__name__} {name}')
        item_appoint = item_appointg.group(1)
        url_appoint = self._url_item(item_appoint)
        html_appoint = self._get_html(url_appoint)
        if self._confirm_not_found(html_appoint):
            raise SpecifiedUrlError(f'{Const.SPECIFIED_URL_ERROR} {url_appoint}，')
        self._item = item_appoint
        return html_appoint

    def _get_html(self, url: str):
        """获取html"""
        for _ in range(1):
            try:
                rsp = self._requests.get(url, timeout=(6, 7))
            except requests.exceptions.ProxyError:
                print(format_exc())
                print(Const.PROXY_ERROR_TRY_AGAIN)
                continue
            except requests.exceptions.SSLError:
                print(format_exc())
                print(f'{Const.REQUEST_MAX_TRY}{url}')
                continue
            except:
                print(format_exc())
                print(f'{Const.REQUEST_ERROR_TRY_AGAIN}{url}')
                continue
            rsp.encoding = 'utf-8'
            rsp_content = rsp.text
            # 响应内容是否正常
            if self._confirm_normal_rsp(rsp_content):
                return rsp_content
            # Todo 很可能遇到cf
            # print(rsp_content)
            print(Const.HTML_NOT_TARGET_TRY_AGAIN)
        input(f'{Const.PLEASE_CHECK_URL}{url}')

    def _select_normal(self, jav_model: JavData):
        # 更新网站对应的item，例如javdb的item是"3d4E5"
        setattr(jav_model, self.__class__.__name__, self._item)

    def _reset(self):
        """开始处理时，重置状态"""
        self._is_only = True
        self._item = Const.CAR_DEFAULT

    # region 必须被子类重写

    @staticmethod
    def _search(car: str) -> str:
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    @staticmethod
    def _url_item(item: str) -> str:
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    @staticmethod
    def _select_special(html: str, jav_data: JavData) -> ScrapeStatusEnum:
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    @staticmethod
    def _confirm_normal_rsp(content: str) -> bool:
        """
        检查是否是预期响应

        网站可能响应的是cloudflare检测，不是预期的jav网页。

        Returns:
            是否是预期响应
        """
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    @staticmethod
    def _confirm_not_found(html: str) -> bool:
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    # endregion

    # Todo 测试方法
    def test(self, url: str):
        return self._get_html(url)
