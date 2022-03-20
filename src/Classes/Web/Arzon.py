# -*- coding:utf-8 -*-
import re
import requests
from configparser import RawConfigParser
# from traceback import format_exc

from Classes.Enums import ScrapeStatusEnum
from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Const import Const
from Classes.Config import Ini


class Arzon(object):
    """
    arzon刮削工具

    获取简介
    """

    def __init__(self, settings: Ini):

        self._URL = 'https://www.arzon.jp'
        """arzon网址"""

        self._PROXIES = settings.proxy_arzon
        """arzon使用代理"""

        self._cookies = {'PHPSESSID': settings.arzon_phpsessid}
        """arzon通行证\n\n如果需要从arzon获取日语简介，需要先获得合法的arzon网站的cookies，用于通过成人验证。"""

    def scrape(self, jav_file: JavFile, jav_model: JavData):
        """
        获取简介

        Args:
            jav_file: jav视频文件对象
            jav_model: jav元数据对象

        Returns:
            刮削结果
        """

        # 在arzon搜索该车牌
        for _ in range(2):

            # 搜索结果页面
            html_search = self._search_html(jav_file.Car_search)

            # 搜索结果页面上的items <dt><a href="https://www.arzon.jp/item_1376110.html" title="限界集落 ～村民
            if items := re.findall(r'h2><a href="/item_(.+?)\.html" title=', html_search):

                # 依次搜寻简介，找到为止
                for item in items:
                    if plot := self._get_plot_from_item(item):
                        jav_model.Arzon = item
                        jav_model.Plot = plot
                        return ScrapeStatusEnum.success

                # 几个搜索结果查找完了，也没有找到简介
                jav_model.Plot = Const.ARZON_EXIST_BUT_NO_PLOT
                return ScrapeStatusEnum.arzon_exist_but_no_plot

            # 返回的页面实际是18岁验证，更新cookies，重新再来
            elif re.search(r'１８歳未満', html_search):
                self._update_cookies()
                # continue

            # 找不到
            else:
                jav_model.Plot = Const.ARZON_PLOT_NOT_FOUND
                return ScrapeStatusEnum.arzon_not_found

        input(f'>>请检查你的网络环境是否可以通过成人验证: {self._URL}')
        return ScrapeStatusEnum.interrupted

    def _update_cookies(self):
        """
        更新cookies

        更新实例变量cookies，重写ini中的arzon_phpsessid
        """
        print(f'\n正在尝试通过 {self._URL} 的成人验证...')
        # Todo 把%换成 /
        url_adult = f'{self._URL}/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https://www.arzon.jp/'
        for _ in range(10):
            try:
                session = requests.Session()
                if self._PROXIES:
                    session.get(url_adult, timeout=(12, 7), proxies=self._PROXIES)
                else:
                    session.get(url_adult, timeout=(12, 7))
                self._cookies = session.cookies.get_dict()
                self._write_new_phpsessid()
                print('通过arzon的成人验证！\n')
            except requests.exceptions.ProxyError:
                # print(format_exc())
                print('    >通过局部代理失败，重新尝试...')
                continue
            except:
                # print(format_exc())
                print('通过失败，重新尝试...')
        input('>>请检查你的网络环境是否可以打开: {self._URL}')

    def _get_html(self, url: str):
        """
        搜索arzon，或请求arzon上jav所在html

        Args:
            url: 目标网址

        Returns:
            html
        """
        for _ in range(10):
            try:
                if self._PROXIES:
                    rqs = requests.get(url, cookies=self._cookies, timeout=(12, 7), proxies=self._PROXIES)
                else:
                    rqs = requests.get(url, cookies=self._cookies, timeout=(12, 7))
            except requests.exceptions.ProxyError:
                # print(format_exc())
                print(Const.PROXY_ERROR_TRY_AGAIN)
                continue
            except:
                print(f'{Const.REQUEST_ERROR_TRY_AGAIN}{url}')
                continue
            rqs.encoding = 'utf-8'
            rqs_content = rqs.text
            if re.search(r'arzon', rqs_content):
                return rqs_content
            else:
                print(Const.HTML_NOT_TARGET_TRY_AGAIN)
        input(f'{Const.PLEASE_CHECK_URL}{url}')

    def _search_html(self, car: str):
        """
        搜索某个车牌的html

        Args:
            car: 当前处理的车牌

        Returns:
            目标html
        """
        url_search = f'{self._URL}/itemlist.html?t=&m=all&s=&q={car}'
        print('    >搜索arzon: ', url_search)
        return self._get_html(url_search)

    def _get_plot_from_item(self, item: str):
        """
        从一个item中搜寻plot

        Args:
            item: https://www.arzon.jp/item_1376110.html中的1376110

        Returns:
            plot
        """
        url_item = f'{self._URL}/item_{item}.html'  # https://www.arzon.jp/item_1663776.html
        print('    >获取简介: ', url_item)
        html_item = self._get_html(url_item)
        if plotg := re.search(r'h2>作品紹介</h2>([\s\S]*?)</div>', html_item):
            return self._remove_br(plotg.group(1))
        return ''

    @staticmethod
    def _remove_br(plot_with_br: str):
        """删除简介中的换行"""
        plot = ''
        for line in plot_with_br.split('<br />'):
            line = line.strip()
            plot = f'{plot}{line}'
        return plot

    def _write_new_phpsessid(self):
        """在ini中写入新的arzon的phpsessid"""
        conf = RawConfigParser()
        conf.read(Const.INI, encoding='utf-8-sig')
        conf.set(Const.NODE_OTHER, Const.ARZON_PHPSESSID, self._cookies['PHPSESSID'])
        conf.write(open(Const.INI, "w", encoding='utf-8-sig'))
        print(f'    >保存新的{Const.ARZON_PHPSESSID}至{Const.INI}成功！')
