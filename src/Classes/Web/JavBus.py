# -*- coding:utf-8 -*-
import re
import requests
from typing import List

import Config
from Classes.Enums import ScrapeStatusEnum
# from traceback import format_exc

from Classes.Errors import SpecifiedUrlError
from Const import Const
from Genre import better_dict_genres, prefect_genres
from Classes.Model.JavData import JavData
from JavFile import JavFile


class JavBus(object):
    def __init__(self, settings: Config.Ini):
        self._url = settings.url_bus
        """bus网址"""

        self._proxies = settings.proxy_bus
        """bus使用代理"""

        self._dict_genres = better_dict_genres("bus", settings.to_language)
        """优化后的bus genres"""

        self._headers = {'Cookie': 'existmag=all'}
        """bus的请求头\n\n为了获得所有影片，而不是默认的有磁力的链接"""

        self._status = ScrapeStatusEnum.bus_not_found
        """刮削状态"""

    def scrape(self, jav_file: JavFile, jav_model: JavData):
        """
        去javbus搜寻系列、在javbus的封面链接

        系列名称，图片链接，状态码

        Args:
            jav_file: jav视频文件对象
            jav_model: jav元数据对象

        Returns:
            刮削结果
        """
        self._status = ScrapeStatusEnum.bus_not_found  # 重置状态

        if html_jav_bus:
            # DVD封面cover
            coverg = re.search(r'bigImage" href="/pics/cover/(.+?)"', html_jav_bus)
            if coverg:
                jav_model.CoverBus = coverg.group(1)
            # 系列:</span> <a href="https://www.cdnbus.work/series/kpl">悪質シロウトナンパ</a>
            seriesg = re.search(r'系列:</span> <a href=".+?">(.+?)</a>', html_jav_bus)
            if seriesg and not jav_model.Series:
                jav_model.Series = seriesg.group(1)
            # 特点
            genres = re.findall(r'gr_sel" value="\d+"><a href=".+">(.+?)</a>', html_jav_bus)
            jav_model.Genres.append(prefect_genres(self._dict_genres, genres))
        return status

    def _find_dest_html(self, jav_file: JavFile, jav_model: JavData):

        # 用户指定了网址，则直接得到jav所在网址
        if '公交车' in jav_file.Name:
            html_dest = self._get_appoint(jav_file, jav_model)
        # 用户没有指定网址，则去搜索
        else:
            html_dest = self._get_guess(jav_file, jav_model)

        # endregion

    def _get_bus_html(self, url):
        """
        搜索arzon，或请求arzon上jav所在网页

        Args:
            url: 目标网址

        Returns:
            网页html
        """
        for retry in range(10):
            try:
                if self._proxies:
                    rqs = requests.get(url, headers=self._headers, timeout=(6, 7), proxies=self._proxies)
                else:
                    rqs = requests.get(url, headers=self._headers, timeout=(6, 7))
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
            else:
                print(Const.HTML_NOT_TARGET_TRY_AGAIN)
                continue
        else:
            input(f'{Const.PLEASE_CHECK_URL}{url}')

    def _get_appoint(self, jav_file: JavFile, jav_model: JavData):
        carg = re.search(r'公交车(.+?)\.', jav_file.Name)
        if not carg:
            raise SpecifiedUrlError(f'你指定的javbus网址有错误: {jav_file.Name}')
        car = carg.group(1)
        url_appoint = f'{self._url}/{car}'
        html_appoint = self._get_bus_html(url_appoint)
        if re.search(r'404 Page', html_appoint):
            raise SpecifiedUrlError(f'你指定的javbus网址找不到jav: {url_appoint}，')
        jav_model.JavBus = car
        self._status = ScrapeStatusEnum.success
        return html_appoint

    def _get_guess(self, jav_file: JavFile, jav_model: JavData):
        # jav在javbus上的url，一般就是javbus网址/车牌
        url_guess = f'{self._url}/{jav_file.Car_id}'
        print('    >前往javbus: ', url_guess)
        # 获得影片在javbus上的网页
        html_guess = self._get_bus_html(url_guess)
        if not re.search(r'404 Page', html_guess):
            jav_model.JavBus = jav_file.Car_id
            self._status = ScrapeStatusEnum.success
            return html_guess
        else:
            return ''

    def _search(self, jav_file: JavFile, jav_model: JavData):
        """
        搜索车牌，寻找目标网页

        Returns:
            jav所在的网页html
        """

        # region 搜索该车牌
        url_search = f'{self._url}/search/{jav_file.Car_id.replace("-", "")}&type=1&parent=ce'
        print('    >搜索javbus: ', url_search)
        html_search = self._get_bus_html(url_search)
        # endregion

        # region 检查搜索结果
        # <a class="movie-box" href="https://www.dmmsee.fun/ABP-991">
        list_items = re.findall(r'movie-box" href="(.+?)">', html_search)  # 匹配处理“标题”
        if not list_items:
            return ''
        list_fit = self._check_search(jav_file, list_items)

        # 没找到
        if not list_fit:
            return ''

        # 有多个结果，警告一下用户
        self._status = (
            ScrapeStatusEnum.bus_multiple_search_results
            if len(list_fit) > 1
            else ScrapeStatusEnum.success
        )
        # endregion

        # region 找到目标所在网页
        url_dest = list_fit[0]  # 默认用第一个搜索结果
        jav_model.JavBus = url_dest.split('/')[-1].upper()  # 例如 ABC-123_2011-11-11
        print('    >获取系列: ', url_dest)
        return self._get_bus_html(url_dest)
        # endregion

    @staticmethod
    def _check_search(jav_file: JavFile, list_items: List[str]):
        """找出搜索结果中车牌相同的movie-box"""
        pref = jav_file.Car_id.split('-')[0]  # 车牌的前缀字母
        suf = jav_file.Car_id.split('-')[-1].lstrip('0')  # 车牌的后缀数字 去除多余的0
        list_fit = []  # 存放，车牌符合的结果
        for url_item in list_items:
            car_bus = url_item.split('/')[-1].upper()  # 例如 ABC-123_2011-11-11
            suf_url = re.search(r'[-_](\d+)', car_bus).group(1).lstrip('0')  # 找出ABC-123_2011-11-11中的123
            pref_url = re.search(r'([A-Z]+2?8?)', car_bus).group(1).upper()  # 找出ABC-123_2011-11-11中的ABC
            if suf == suf_url and pref == pref_url:  # 车牌相同
                list_fit.append(url_item)
        return list_fit
