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


class JavBus(object):
    """
    javbus刮削工具

    获取网址、封面、系列、特征
    """

    def __init__(self, settings: Ini):
        self._URL = settings.url_bus
        """bus网址"""

        self._PROXIES = settings.proxy_bus
        """bus使用代理"""

        self._DICT_GENRES = better_dict_genres('bus', settings.to_language)
        """优化后的bus genres"""

        self._HEADERS = {'Cookie': 'existmag=all'}
        """bus的请求头\n\n为了获得所有影片，而不是默认的仅显示有磁力的链接"""

        self._is_only: bool = True
        """是否 刮削到唯一结果\n\n如果有多个结果，需警告用户"""

        self._item = Const.CAR_DEFAULT
        """车牌在bus上的网址item\n\n例如ABC-123_2011-11-11，如果刮削成功则将它更新为正确值，交给jav_model"""

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

    def _get_html(self, url):
        """获取html"""
        for _ in range(10):
            try:
                if self._PROXIES:
                    rqs = requests.get(url, headers=self._HEADERS, timeout=(6, 7), proxies=self._PROXIES)
                else:
                    rqs = requests.get(url, headers=self._HEADERS, timeout=(6, 7))
            except requests.exceptions.ProxyError:
                # print(format_exc())
                print(Const.PROXY_ERROR_TRY_AGAIN)
                continue
            except:
                # print(format_exc())
                print(f'{Const.REQUEST_ERROR_TRY_AGAIN}{url}')
                continue
            rqs.encoding = 'utf-8'
            rqs_content = rqs.text
            if re.search(r'JavBus', rqs_content):
                return rqs_content
            # Todo 很可能遇到cf
            # print(rqs_content)
            print(Const.HTML_NOT_TARGET_TRY_AGAIN)
        input(f'{Const.PLEASE_CHECK_URL}{url}')

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
        car_appointg = re.search(r'公交车(.+?)\.', name)
        if not car_appointg:
            raise SpecifiedUrlError(f'{Const.SPECIFIED_FORMAT_ERROR} {type(self).__name__} {name}')
        car_appoint = car_appointg.group(1)
        url_appoint = f'{self._URL}/{car_appoint}'
        html_appoint = self._get_html(url_appoint)
        if re.search(r'404 Page', html_appoint):
            raise SpecifiedUrlError(f'{Const.SPECIFIED_URL_ERROR} {url_appoint}，')
        self._item = car_appoint
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
        url_guess = f'{self._URL}/{car}'
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
