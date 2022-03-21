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
from Functions.Metadata.Genre import better_dict_genres, prefect_genres
from Classes.Web.JavWeb import JavWeb


class JavBus(JavWeb):
    """
    javbus刮削工具

    获取网址、封面、系列、特征
    """

    def __init__(self, settings: Ini):
        headers = {'Cookie': 'existmag=all'}
        super().__init__(settings, headers)

    def scrape(self, jav_file: JavFile, jav_model: JavData):
        """
        获取网址、封面、系列、特征

        Args:
            jav_file: jav视频文件对象
            jav_model: jav元数据对象

        Returns:
            刮削结果
        """
        self._reset()

        html = self._find_target_html(jav_file.Name, jav_file.Car_id)
        """当前车牌所在的html"""
        if not html:
            return ScrapeStatusEnum.bus_not_found

        # 车牌在bus上的网址item
        jav_model.Javbus = self._item

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

        return ScrapeStatusEnum.success if self._is_only else ScrapeStatusEnum.bus_multiple_search_results

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
        return (
            self._appoint(name)
            if '公交车' in name
            else self._guess(car)
                 or self._search(car)
        )

    def _appoint(self, name: str):
        """
        从用户指定的网址中获取目标html

        用户将视频命名为“ABC-123公交车DEF-456_2011-11-11.mp4"，即指定为”https://www.buscdn.me/DEF-456_2011-11-11"。

        Args:
            name: 视频文件名

        Returns:
            目标html
        """
        item_appointg = re.search(r'公交车(.+?)\.', name)
        if not item_appointg:
            raise SpecifiedUrlError(f'{Const.SPECIFIED_FORMAT_ERROR} {type(self).__name__} {name}')
        item_appoint = item_appointg.group(1)
        url_appoint = self._url_item(item_appoint)
        html_appoint = self._get_html(url_appoint)
        if re.search(r'404 Page', html_appoint):
            raise SpecifiedUrlError(f'{Const.SPECIFIED_URL_ERROR} {url_appoint}，')
        self._item = item_appoint
        return html_appoint

    def _guess(self, car: str):
        """
        直接访问猜测的网址

        车牌为ABC-123，直接访问”https://www.buscdn.me/ABC-123"。

        Args:
            car: 当前处理的车牌

        Returns:
            目标html
        """
        # jav在javbus上的url，一般就是javbus网址/车牌
        url_guess = self._url_item(car)
        print('    >前往javbus: ', url_guess)
        # 获得影片在javbus上的html
        html_guess = self._get_html(url_guess)
        # 成功找到
        if not re.search(r'404 Page', html_guess):
            self._item = car
            return html_guess
        else:
            return ''

    def _search(self, car: str):
        """
        搜索车牌，获取目标html

        Args:
            car: 当前处理的车牌

        Returns:
            目标html
        """

        # region 搜索该车牌
        url_search = f'{self._URL}/search/{car.replace("-", "")}&type=1&parent=ce'
        print('    >搜索javbus: ', url_search)
        html_search = self._get_html(url_search)
        # endregion

        # region 检查搜索结果
        # <a class="movie-box" href="https://www.dmmsee.fun/ABP-991">
        list_items = re.findall(r'movie-box" href="(.+?)">', html_search)
        if not list_items:
            return ''
        # 筛选搜索结果中和当前车牌基本符合的
        list_fit = self._check_search(car, list_items)

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

    @staticmethod
    def _check_search(car: str, list_items: List[str]):
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
            car_bus = url_item.split('/')[-1].upper()  # 例如 ABC-123_2011-11-11
            suf_url = re.search(r'[-_](\d+)', car_bus).group(1).lstrip('0')  # 找出ABC-123_2011-11-11中的123
            pref_url = re.search(r'([A-Z]+2?8?)', car_bus).group(1).upper()  # 找出ABC-123_2011-11-11中的ABC
            if suf == suf_url and pref == pref_url:  # 车牌相同
                list_fit.append(url_item)
        return list_fit

    def _reset(self):
        """开始处理时，重置状态"""
        self._is_only = True
        self._item = Const.CAR_DEFAULT

    def _url_item(self, item: str):
        """
        一部jav在javbus上的网址

        Args:
            item: 影片在javdb上的代号，例如“4d5E6”

        Returns:
            网址，例如“https://javdb36.com/v/4d5E6”
        """
        return f'{self._URL}/{item}'

    @staticmethod
    def _confirm_rsp(content: str):
        """
        检查是否是预期响应

        Args:
            content: html

        Returns:
            是否是预期响应
        """
        return bool(re.search(r'JavBus', content))
