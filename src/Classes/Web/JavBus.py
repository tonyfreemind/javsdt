# -*- coding:utf-8 -*-
import re
import requests
from typing import List
# from traceback import format_exc

from Classes.Enums import ScrapeStatusEnum
from Classes.Errors import SpecifiedUrlError
from Classes.Const import Const
from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Config import Ini
from Functions.Metadata.Genre import prefect_genres
from Classes.Web.JavWeb import JavWeb


class JavBus(JavWeb):
    """
    javbus刮削工具

    获取网址、封面、系列、特征
    """

    def __init__(self, settings: Ini):
        appoint_symbol = '公交车'
        headers = {'Cookie': 'existmag=all'}
        super().__init__(settings, appoint_symbol, headers)

    # region 重写父类方法

    def _search(self, car: str):
        """
        搜索车牌，获取目标html

        Args:
            car: 当前处理的车牌

        Returns:
            目标html
        """

        # region 尝试直接访问规则的网址
        # jav在javbus上的url，一般就是javbus网址/车牌
        url_guess = self._url_item(car)
        print('    >前往javbus: ', url_guess)
        html_guess = self._get_html(url_guess)
        # 成功找到
        if not re.search(r'404 Page', html_guess):
            self._item = car
            return html_guess
        # endregion

        # region 搜索该车牌
        url_search = f'{self._URL}/search/{car.replace("-", "")}&type=1&parent=ce'
        print('    >搜索javbus: ', url_search)
        html_search = self._get_html(url_search)

        # 检查搜索结果
        # <a class="movie-box" href="https://www.dmmsee.fun/ABP-991">
        list_items = re.findall(r'movie-box" href="(.+?)">', html_search)
        if not list_items:
            return ''
        # 筛选搜索结果中和当前车牌基本符合的
        list_fit = self._check_search_results(car, list_items)

        # 没找到
        if not list_fit:
            return ''

        # 有多个结果，警告一下用户
        self._is_only = len(list_fit) == 1
        # endregion

        # region 找到目标所在html
        url_target = list_fit[0]  # 默认用第一个搜索结果
        self._item = url_target.split('/')[-1].upper()  # 例如 ABC-123_2011-11-11
        print('    >获取系列: ', url_target)
        return self._get_html(url_target)
        # endregion

    def _url_item(self, item: str):
        """
        一部jav在javbus上的网址

        Args:
            item: 影片在javdb上的代号，例如“4d5E6”

        Returns:
            网址，例如“https://javdb36.com/v/4d5E6”
        """
        return f'{self._URL}/{item}'

    def _select_special(self, html: str, jav_model: JavData):

        # 封面
        if coverg := re.search(r'bigImage" href="/pics/cover/(.+?)"', html):
            jav_model.CoverBus = coverg.group(1)
        # 系列
        if not jav_model.Series:
            # 系列:</span> <a href="https://www.cdnbus.work/series/kpl">悪質シロウトナンパ</a>
            if seriesg := re.search(r'系列:</span> <a href=".+?">(.+?)</a>', html):
                jav_model.Series = seriesg.group(1)
        # 特征
        genres = re.findall(r'gr_sel" value="\d+"><a href=".+">(.+?)</a>', html)
        jav_model.Genres.append(prefect_genres(self._DICT_GENRES, genres))

        return ScrapeStatusEnum.success if self._is_only else ScrapeStatusEnum.multiple_results

    @staticmethod
    def _confirm_normal_rsp(content: str):
        """
        检查是否是预期响应

        Args:
            content: html

        Returns:
            是否是预期响应
        """
        return bool(re.search(r'JavBus', content))

    @staticmethod
    def _confirm_not_found(html: str):
        return bool(re.search(r'404 Page', html))

    # endregion

    @staticmethod
    def _check_search_results(car: str, list_items: List[str]):
        """
        筛选 搜索结果 和 当前处理车牌 相同的 几个结果

        Args:
            car: 当前处理的车牌
            list_items: movie-box搜索结果

        Returns:
            符合预期的items
        """
        pref = car.split('-')[0]  # 车牌的前缀字母，例如ABC
        suf = car.split('-')[-1].lstrip('0')  # 车牌的后缀数字 去除多余的0，例如123
        list_fit = []  # 存放，筛选出的结果
        for url_item in list_items:
            # Todo 正则单独作方法
            car_bus = url_item.split('/')[-1].upper()  # 例如 ABC-123_2011-11-11
            suf_url = re.search(r'[-_](\d+)', car_bus).group(1).lstrip('0')  # 找出ABC-123_2011-11-11中的123
            pref_url = re.search(r'([A-Z]+2?8?)', car_bus).group(1).upper()  # 找出ABC-123_2011-11-11中的ABC
            if suf == suf_url and pref == pref_url:  # 车牌相同
                list_fit.append(url_item)
        return list_fit
