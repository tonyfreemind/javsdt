# -*- coding:utf-8 -*-
import re
import requests
from configparser import RawConfigParser
# from traceback import format_exc

from Classes import Config
from Classes.Enums import ScrapeStatusEnum
from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Const import Const


class Arzon(object):
    def __init__(self, settings: Config.Ini):

        self._url = 'https://www.arzon.jp'
        """arzon网址"""

        self._proxies = settings.proxy_arzon
        """arzon使用代理"""

        self._cookies = {'PHPSESSID': settings.arzon_phpsessid}
        """arzon通行证\n\n如果需要从arzon获取日语简介，需要先获得合法的arzon网站的cookies，用于通过成人验证。"""

    def scrape(self, jav_file: JavFile, jav_model: JavData):
        """
        从arzon上查找简介

        Args:
            jav_file: jav视频文件对象
            jav_model: jav元数据对象

        Returns:
            刮削完成度
        """
        for retry in range(2):

            # 在arzon搜索该车牌
            url_search = f'{self._url}/itemlist.html?t=&m=all&s=&q={jav_file.Car_id.replace("-", "")}'
            print('    >搜索arzon: ', url_search)
            html_search = self._get_arzon_html(url_search)

            # <dt><a href="https://www.arzon.jp/item_1376110.html" title="限界集落 ～村民"><img src=
            items = re.findall(r'h2><a href="/item_(.+?)\.html" title=', html_search)  # 所有搜索结果链接
            # 搜索结果为N个AV的界面
            if items:  # arzon有搜索结果
                for item in items:
                    url_jav = f'{self._url}/item_{item}.html'  # 第i+1个链接
                    print('    >获取简介: ', url_jav)
                    # 打开arzon上每一个搜索结果的页面
                    html_jav_arzon = self._get_arzon_html(url_jav)
                    # 在该url_jav网页上查找简介
                    plotg = re.search(r'h2>作品紹介</h2>([\s\S]*?)</div>', html_jav_arzon)
                    # 成功找到plot
                    if plotg:
                        plot_br = plotg.group(1)
                        plot = ''
                        for line in plot_br.split('<br />'):
                            line = line.strip()
                            plot = f'{plot}{line}'
                        jav_model.Arzon = item
                        jav_model.Plot = plot
                        return ScrapeStatusEnum.success
                # 几个搜索结果查找完了，也没有找到简介
                jav_model.Plot = '【arzon有该影片，但找不到简介】'
                return ScrapeStatusEnum.arzon_exist_but_no_plot
            # 没有搜索结果
            else:
                # arzon返回的页面实际是18岁验证
                adultg = re.search(r'１８歳未満', html_search)
                if adultg:
                    self._steal_arzon_cookies()
                    continue
                # 不是成人验证，也没有简介
                else:
                    jav_model.Plot = '【影片下架，暂无简介】'
                    return ScrapeStatusEnum.arzon_not_found
        input(f'>>请检查你的网络环境是否可以通过成人验证: {self._url}')
        return ScrapeStatusEnum.interrupted

    def _steal_arzon_cookies(self):
        """
        获取一个arzon_cookie

        借此通过arzon的成人验证
        """
        print(f'\n正在尝试通过 {self._url} 的成人验证...')
        #Todo 把%换成 /
        url_adult = f'{self._url}/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https%3A%2F%2Fwww' \
                    f'.arzon.jp%2F '
        for retry in range(10):
            try:
                session = requests.Session()
                if self._proxies:
                    session.get(url_adult, timeout=(12, 7), proxies=self._proxies)
                else:
                    session.get(url_adult, timeout=(12, 7))
                self._cookies = session.cookies.get_dict()
                print('通过arzon的成人验证！\n')
                self._write_new_arzon_phpsessid()
            except requests.exceptions.ProxyError:
                # print(format_exc())
                print('    >通过局部代理失败，重新尝试...')
                continue
            except:
                # print(format_exc())
                print('通过失败，重新尝试...')
                continue
        else:
            input('>>请检查你的网络环境是否可以打开: {self._url}')

    def _get_arzon_html(self, url: str):
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
                    rqs = requests.get(url, cookies=self._cookies, timeout=(12, 7), proxies=self._proxies)
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
                continue
        else:
            input(f'{Const.PLEASE_CHECK_URL}{url}')

    def _write_new_arzon_phpsessid(self):
        """在ini中写入新的arzon的phpsessid"""
        conf = RawConfigParser()
        conf.read(Const.INI, encoding='utf-8-sig')
        conf.set(Const.NODE_OTHER, Const.ARZON_PHPSESSID, self._cookies['PHPSESSID'])
        conf.write(open(Const.INI, "w", encoding='utf-8-sig'))
        print(f'    >保存新的{Const.ARZON_PHPSESSID}至{Const.INI}成功！')
