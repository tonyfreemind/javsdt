# -*- coding:utf-8 -*-
import re
from lxml import etree
import requests
# from traceback import format_exc

from Classes.Config import Ini
from Classes.Enums import ScrapeStatusEnum
from Classes.Errors import SpecifiedUrlError, DbCodePageNothingError, InRangeButDbNotFoundError
from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Const import Const
from Functions.Metadata.Genre import better_dict_genres, prefect_genres
from Functions.Metadata.Car import get_suf_from_car


class JavDb(object):
    """
    db刮削工具

    获取所有所需内容
    """

    def __init__(self, settings: Ini):
        self._URL = settings.url_db
        """db网址"""

        self._PROXIES = settings.proxy_db
        """db使用代理"""

        self._DICT_GENRES = better_dict_genres("db", settings.to_language)
        """优化后的db genres"""

        self._HEADERS = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.198 Safari/537.36",
            "accept-encodin": "gzip, deflate, br",
        }
        """db的请求头\n\ndb会检查"""

        self._item = Const.CAR_DEFAULT
        """车牌在bus上的网址item\n\n例如ABC-123_2011-11-11，如果刮削成功则将它更新为正确值，交给jav_model"""

    def scrape(self, jav_file: JavFile, jav_data: JavData):

        javdb = self._find_target_item(jav_file.Name, jav_file.Car_id)

        # 得到 javdb
        url_jav_db = f'{self._URL}/v/{javdb}'
        print('    >前往javdb: ', url_jav_db)
        html_jav_db = self._get_html(url_jav_db)
        # <title> BKD-171 母子交尾 ～西会津路～ 中森いつき | JavDB 成人影片資料庫及磁鏈分享 </title>
        car_title = re.search(r'title> (.+) \| JavDB', html_jav_db).group(1)
        list_car_title = car_title.split(' ', 1)
        jav_data.Car = list_car_title[0]  # 围绕该jav的所有信息
        jav_data.Title = list_car_title[1]
        jav_data.JavDb = javdb
        # 带着主要信息的那一块 複製番號" data-clipboard-text="BKD-171">
        html_jav_db = re.search(r'複製番號([\s\S]+?)存入清單', html_jav_db, re.DOTALL).group(1)
        # 系列 "/series/RJmR">○○に欲望剥き出しでハメまくった中出し記録。</a>
        seriesg = re.search(r'series/.+?">(.+?)</a>', html_jav_db)
        jav_data.Series = seriesg.group(1) if seriesg else ''
        # 上映日 e">2019-02-01<
        releaseg = re.search(r'(\d\d\d\d-\d\d-\d\d)', html_jav_db)
        jav_data.Release = releaseg.group(1) if releaseg else '1970-01-01'
        # 片长 value">175 分鍾<
        runtimeg = re.search(r'value">(\d+) 分鍾<', html_jav_db)
        jav_data.Runtime = int(runtimeg.group(1)) if runtimeg else 0
        # 导演 /directors/WZg">NABE<
        directorg = re.search(r'directors/.+?">(.+?)<', html_jav_db)
        jav_data.Director = directorg.group(1) if directorg else ''
        # 制作商 e"><a href="/makers/
        studiog = re.search(r'makers/.+?">(.+?)<', html_jav_db)
        jav_data.Studio = studiog.group(1) if studiog else ''
        # 发行商 /publishers/pkAb">AV OPEN 2018</a><
        publisherg = re.search(r'publishers.+?">(.+?)</a><', html_jav_db)
        jav_data.Publisher = publisherg.group(1) if publisherg else ''
        # 评分 star gray"></i></span>&nbsp;3.75分
        scoreg = re.search(r'star gray"></i></span>&nbsp;(.+?)分', html_jav_db)
        jav_data.Score = int(float(scoreg.group(1)) * 20) if scoreg else 0
        # 演员们 /actors/M0xA">上川星空</a>  actors/P9mN">希美まゆ</a><strong class="symbol female
        actors = re.findall(r'actors/.+?">(.+?)</a><strong class="symbol female', html_jav_db)
        jav_data.Actors = [i.strip() for i in actors]
        str_actors = ' '.join(jav_data.Actors)
        # 去除末尾的标题 javdb上的演员不像javlibrary使用演员最熟知的名字
        if str_actors and jav_data.Title.endswith(str_actors):
            jav_data.Title = jav_data.Title[:-len(str_actors)].strip()
        # print('    >演员: ', actors)
        # 特征 /tags?c7=8">精选、综合</a>
        genres = re.findall(r'tags.+?">(.+?)</a>', html_jav_db)
        jav_data.Genres.append(prefect_genres(self._DICT_GENRES, genres))
        return ScrapeStatusEnum.success

    def _find_target_item(self, name: str, car: str):
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
            if '仓库' in name
            else self._iterate(car)
        )

    def _appoint(self, name: str):
        """
        从用户指定的网址中获取目标html

        用户将视频命名为“ABC-123仓库4d5E6.mp4"，即指定为”https://javdb36.com/v/4d5E6"。

        Args:
            name: 视频文件名

        Returns:
            目标html
        """
        item_appointg = re.search(r'仓库(\w+?)\.', name)
        if not item_appointg:
            raise SpecifiedUrlError(f'{Const.SPECIFIED_FORMAT_ERROR} {type(self).__name__} {name}')
        item_appoint = item_appointg.group(1)
        url_appoint = self._url_item(item_appoint)
        html_appoint = self._get_html(url_appoint)
        if re.search(r'頁面未找到', html_appoint):
            raise SpecifiedUrlError(f'{Const.SPECIFIED_URL_ERROR} {url_appoint}，')
        self._item = item_appoint
        return html_appoint

    def _iterate(self, pref: str, suf: int):
        """
        遍历video_codes网页找出目标html

        Args:
            pref: ABC-123z的ABC
            suf: ABC-123z的123

        Returns:
            成功找到，返回item，例如4d5E6；找不到，返回
        """

        # region 预估当前车牌在第几页
        # 先从首页开始
        no_page = 1
        """当前车牌 预估在第几页"""
        # 首页的车尾
        tuple_temp = self._find_suf_min_max_in_page(self._url_page(pref, no_page))
        # javdb没有该车头的页面
        if not tuple_temp:
            raise
        suf_min, suf_max = tuple_temp
        # 通过 当前车尾 和 首页的最小车尾 的差距，除以40一页，预估在第几页
        no_page = (suf_min - suf) // 40 + 2 if suf_min > suf else 1
        # endregion

        # region 确认车牌在预估页面之前还是之后
        # 预估页面不是首页，访问预估页面，找到最小和最大车尾
        if no_page != 1:
            if tuple_temp := self._find_suf_min_max_in_page(self._url_page(pref, no_page)):
                suf_min, suf_max = tuple_temp
            # 预估的页面找不到数据，即已经超出范围，比如实际只有10页，预估到12页。
            else:
                # 防止预估的no_page太大，比如HODV-21301
                no_page = min(no_page, 60)
                # 往前推，直至找到最后有数据的那一页
                while True:
                    no_page -= 1
                    if tuple_temp := self._find_suf_min_max_in_page(self._url_page(pref, no_page)):
                        suf_min, suf_max = tuple_temp
                        break
        # 如果比 预估页面 的最小车尾 还小，往下一页找，否则往前一页找。
        one = 1 if suf < suf_min else -1
        # endregion

        # region 从预估页面开始，一页一页查找
        while True:

            # 比首页收录的最大车牌还大，找不到
            if no_page == 0:
                return ''

            # 在当前页面查找item
            try:
                item = self._find_target_item_in_page(self._url_page(pref, no_page), suf)
            except RuntimeError:
                # 走到尾也找不到；虽然在页面车尾范围内，但也找不到。
                return ''

            # 找到了
            if item:
                return item

            # 页码往后(或往前）推一页
            no_page += one
        # endregion

    def _find_suf_min_max_in_page(self, url_page: str):
        """
        查找第no_page页上的最小和最大车尾

        Args:
            pref: 车头
            no_page: 第几页

        Returns:
            最小车尾，最大车尾
        """
        html_pref = self._get_html(url_page)
        # Todo xpath直接取第一个和最后一个
        if list_cars := etree.HTML(html_pref).xpath(Const.XPATH_DB_CARS):
            suf_min = int(get_suf_from_car(list_cars[-1]))
            suf_max = int(get_suf_from_car(list_cars[0]))
            return suf_min, suf_max
        else:
            return None

    def _find_target_item_in_page(self, url_page: str, suf: int):
        """
        在当前页面查找目标item

        Raises:
            当前页面无内容 || suf在车尾范围内但找不到 => javdb找不到

        Args:
            url_page: 车头的某一页网址
            suf: 当前处理的车牌的车尾，例如ABC-123z的123

        Returns:
            成功找到，返回item，例如4d5E6；不在车尾范围内（需要去下一页），返回空。
        """

        html_pref = self._get_html(url_page)
        html_tree = etree.HTML(html_pref)
        list_cars = html_tree.xpath(Const.XPATH_DB_CARS)

        # 这一页已经没内容了
        if not list_cars:
            raise

        suf_min = int(get_suf_from_car(list_cars[-1]))
        suf_max = int(get_suf_from_car(list_cars[0]))
        if not suf_max >= suf >= suf_min:
            # 不在车尾范围内（希望程序直接去下一页）
            return ''
        for i, car in enumerate(list_cars):
            if int(get_suf_from_car(car)) == suf:
                return html_tree.xpath(f'//*[@id="videos"]/div/div[{i + 1}]/a/@href')[0][3:]
        # suf在该页面的车尾范围内，但找不到
        raise

    def _url_page(self, pref: str, no_page: int):
        """
        车头的某一页网址

        Args:
            pref: 车头，例如ABC
            no_page: 第几页

        Returns:
            网址，例如“https://javdb36.com/video_codes/ABC?page=2”
        """
        return f'{self._URL}/video_codes/{pref}?page={no_page}'

    def _url_item(self, item: str):
        """
        一部jav在javdb上的网址

        Args:
            item: 影片在javdb上的代号，例如“4d5E6”

        Returns:
            网址，例如“https://javdb36.com/v/4d5E6”
        """
        return f'{self._URL}/v/{item}'

    @staticmethod
    def _confirm_rsp(content: str):
        """
        检查是否是预期响应

        Args:
            content: html

        Returns:
            是否是预期响应
        """
        return bool(re.search(r'成人影片數據庫', content) or re.search(r'頁面未找到', content))

    @staticmethod
    def _confirm_not_found(html: str):
        return bool(re.search(r'頁面未找到', html))
