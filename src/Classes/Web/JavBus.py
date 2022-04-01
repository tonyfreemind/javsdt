# -*- coding:utf-8 -*-
import re
from typing import List
# from traceback import format_exc

from Static.Config import Ini
from Enums import ScrapeStatusEnum
from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Web.JavWeb import JavWeb
from Functions.Metadata.Genre import prefect_genres
from Functions.Metadata.Car import extract_suf, extract_pref


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

    def _search(self, jav_file: JavFile):

        # 尝试直接访问规则的网址
        if html := self._guess(jav_file):
            return html  # bus找到了

        # region 搜索该车牌，检查结果
        html_search = self._get_html('    >搜索javbus:', self._url_search(jav_file))

        # 检查搜索结果 <a class="movie-box" href="https://www.dmmsee.fun/ABP-991">
        list_items = re.findall(r'movie-box" href="(.+?)">', html_search)
        if not list_items:
            return ''  # bus找不到
        # 筛选 搜索结果中 和 当前车牌 基本符合的
        list_fit = self._check_result_items(jav_file, list_items)

        # 没找到
        if not list_fit:
            return ''  # bus找不到
        # endregion

        # region 确定目标所在html
        url_target = list_fit[0]  # 默认用第一个搜索结果
        item = url_target.split('/')[-1].upper()  # 例如 ABC-123_2011-11-11
        status = ScrapeStatusEnum.success if len(list_fit) == 1 else ScrapeStatusEnum.multiple_results
        self._update_item_status(item, status)
        return self._get_html('    >获取系列:', url_target)  # bus找到了
        # endregion

    def _url_item(self, item: str):
        return f'{self._URL}/{item}'

    def _url_search(self, jav_file: JavFile):
        return f'{self._URL}/search/{jav_file.Car_search}&type=1&parent=ce'

    def _select_special(self, html: str, jav_data: JavData):

        # 标题
        title = re.search(r'h3>(.+?)</h3', html, re.DOTALL).group(1)  # javbus上的标题可能占两行
        print('    >Bus标题:', title)

        # 封面
        if coverg := re.search(r'bigImage" href="/pics/cover/(.+?)"', html):
            jav_data.CoverBus = coverg.group(1)
        # 系列
        if not jav_data.Series:
            # 系列:</span> <a href="https://www.cdnbus.work/series/kpl">悪質シロウトナンパ</a>
            if seriesg := re.search(r'系列:</span> <a href=".+?">(.+?)</a>', html):
                jav_data.Series = seriesg.group(1)
        # 特征
        genres = re.findall(r'gr_sel" value="\d+"><a href=".+">(.+?)</a>', html)
        jav_data.Genres.extend(prefect_genres(self._DICT_GENRES, genres))

    @staticmethod
    def _confirm_normal_rsp(content: str):
        return bool(re.search(r'JavBus', content))

    @staticmethod
    def _confirm_not_found(html: str):
        return bool(re.search(r'404 Page', html))

    def _need_update_headers(self, html: str):
        return self._confirm_cloudflare(html)

    @staticmethod
    def _update_headers():
        # Todo 实现
        pass

    # endregion

    # region 特色方法

    def _guess(self, jav_file: JavFile):
        """
        直接访问猜测的网址，得到目标html

        Args:
            car: 车牌，例如26ID-020

        Returns:
            html，找不到则返回空
        """
        # jav在javbus上的url，一般就是javbus网址/车牌
        html_guess = self._get_html('    >前往javbus:', self._url_item(jav_file.Car))
        # 找不到
        if self._confirm_not_found(html_guess):
            return ''  # 指定网址无内容（希望接下来去搜索）
        self._update_item_status(jav_file.Car, ScrapeStatusEnum.success)
        return html_guess  # bus找到了

    @staticmethod
    def _check_result_items(jav_file: JavFile, list_items: List[str]):
        """
        筛选 搜索结果 和 当前处理车牌 相同的 几个结果

        Args:
            car: 当前处理的车牌
            list_items: movie-box搜索结果

        Returns:
            符合预期的items
        """
        list_fit = []  # 存放，筛选出的结果
        for url_item in list_items:
            car_bus = url_item.split('/')[-1].upper()  # 例如 ABC-123_2011-11-11
            suf = extract_suf(car_bus)  # 找出ABC-123_2011-11-11中的123
            pref = extract_pref(car_bus)  # 找出ABC-123_2011-11-11中的ABC
            if jav_file.Suf == suf and jav_file.Pref == pref:  # 车牌相同
                list_fit.append(url_item)
        return list_fit

    # endregion
