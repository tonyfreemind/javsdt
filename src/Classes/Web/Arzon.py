# -*- coding:utf-8 -*-
import re
from requests.exceptions import ProxyError
# from traceback import format_exc

from Static.Config import Ini
from Static.Const import Const
from Enums import ScrapeStatusEnum
from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Web.JavWeb import JavWeb
from Functions.Utils.LittleUtils import update_ini_file_value


class Arzon(JavWeb):
    """
    arzon刮削工具

    获取简介
    """

    def __init__(self, settings: Ini):
        appoint_symbol = '阿如'
        headers = {'Cookie': f'PHPSESSID={settings.arzon_phpsessid}'}
        """arzon通行证\n\n如果需要从arzon获取日语简介，需要先获得合法的arzon网站的cookies，用于通过成人验证。"""
        super().__init__(settings, appoint_symbol, headers)

        self._URL_ADULT = f'{self._URL}/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https://www.arzon.jp/'
        """打开该链接可得到合法的成人通行证"""

    # region 重写父类方法

    def _search(self, jav_file: JavFile):
        # 在arzon搜索该车牌
        html_search = self._get_html('    >搜索arzon:', self._url_search(jav_file))
        # 搜索结果页面上的items <dt><a href="https://www.arzon.jp/item_1376110.html" title="限界集落 ～村民
        if items := re.findall(r'h2><a href="/item_(.+?)\.html" title=', html_search):
            # 依次搜寻简介，找到为止。arzon上很可能有多个搜索结果，不是每个结果都有简介
            for item in items:
                html_item = self._get_html('    >获取plot:', self._url_item(item))
                if re.search(r'h2>作品紹介</h2>([\s\S]*?)</div>', html_item):
                    self._update_item_status(item, ScrapeStatusEnum.success)
                    return html_item  # arzon找到了
            # 有搜索结果，但找不到
            self._update_item_status(Const.CAR_DEFAULT, ScrapeStatusEnum.exist_but_no_want)
        return ''  # arzon没找到

    def _url_item(self, item: str):
        return f'{self._URL}/item_{item}.html'

    def _url_search(self, jav_file: JavFile):
        return f'{self._URL}/itemlist.html?t=&m=all&s=&q={jav_file.Car_search}'

    def _select_special(self, html: str, jav_data: JavData):
        plot = re.search(r'h2>作品紹介</h2>([\s\S]*?)</div>', html).group(1)
        jav_data.Plot = self._remove_br(plot)

    @staticmethod
    def _confirm_normal_rsp(content: str):
        return bool(re.search(r'arzon', content))

    @staticmethod
    def _confirm_not_found(html: str):
        return bool(re.search(r'404 Page', html))

    def _need_update_headers(self, html: str) -> bool:
        return self._confirm_cloudflare(html)

    def _update_headers(self):
        for _ in range(5):
            try:
                self._requests.get(self._URL_ADULT, timeout=(6, 7))
            except ProxyError:
                print(f'    >通过代理失败，重新尝试... {self._URL_ADULT}')
                continue
            except:
                print(f'    >打开网页失败，重新尝试... {self._URL_ADULT}')
                continue
            # 在ini中记录下这个新通行证
            phpsessid = self._requests.cookies.get_dict()['PHPSESSID']
            update_ini_file_value(Const.INI, Const.NODE_OTHER, Const.ARZON_PHPSESSID, phpsessid)
            print('通过arzon的成人验证！\n')
        input(f'    >打开网页失败，重新尝试... {self._URL_ADULT}')

    # endregion

    # region 特色方法

    @staticmethod
    def _confirm_adult_verify(html: str):
        """检查当前网页是不是成人验证的页面"""
        return bool(re.search(r'１８歳未満', html))

    @staticmethod
    def _remove_br(plot_with_br: str):
        """
        删除简介中的换行

        Args:
            plot_with_br: 原始plot

        Returns:
            去除换行的plot
        """
        plot = ''
        for line in plot_with_br.split('<br />'):
            line = line.strip()
            plot = f'{plot}{line}'
        return plot

    # endregion
