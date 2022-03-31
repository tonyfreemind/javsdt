# -*- coding:utf-8 -*-
import re
from typing import List
from lxml import etree
# from traceback import format_exc

from Static.Config import Ini
from Static.Const import Const
from Enums import ScrapeStatusEnum
from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Web.JavWeb import JavWeb
from Functions.Metadata.Car import extract_suf
from Functions.Metadata.Genre import prefect_genres


class JavDb(JavWeb):
    """
    db刮削工具

    获取影片的绝大部分信息
    """

    def __init__(self, settings: Ini):
        appoint_symbol = '仓库'
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.198 Safari/537.36",
            "accept-encodin": "gzip, deflate, br",
        }
        super().__init__(settings, appoint_symbol, headers)

    # region 重写父类方法

    def _search(self, jav_file: JavFile):
        if html := self._find_in_code_pages(jav_file):
            return html

        # region 搜索该车牌，检查结果
        html_search = self._get_html('    >搜索javdb:', self._url_search(jav_file))

        # 检查搜索结果 <a class="movie-box" href="https://www.dmmsee.fun/ABP-991">
        list_results = re.findall(r'href="/v/(.+?)" class="box" title=".+?"[\s\S]*?uid">(.+?)</div>', html_search)
        if not list_results:
            return ''  # db找不到

        # 筛选 搜索结果中 和 当前车牌 基本符合的
        list_cars = [result[1] for result in list_results]
        # 筛选 搜索结果中 和 当前车牌 基本符合的
        list_fit_index = self._check_result_cars(jav_file, list_cars)
        if not list_fit_index:
            return ''  # bus找不到
        # endregion

        # region 确定目标所在html
        item = list_results[list_fit_index[0]]  # 默认用第一个搜索结果
        status = ScrapeStatusEnum.success if len(list_fit_index) == 1 else ScrapeStatusEnum.multiple_results
        self._update_item_status(item, status)
        return self._get_html('    >获取系列:', self._url_item(item))  # bus找到了
        # endregion

    def _url_item(self, item: str):
        return f'{self._URL}/v/{item}'

    def _url_search(self, jav_file: JavFile):
        return f'{self._URL}/search?q={jav_file.Car}&f=all'

    def _select_special(self, html: str, jav_data: JavData):

        # 车牌，标题 <title> ID-020 可愛すぎる魔法少女5人とパジャマで中出し性交 | JavDB 成人影片數據庫 </title>
        car_title = re.search(r'title> (.+) \| JavDB', html).group(1)
        jav_data.Car, jav_data.Title = car_title.split(' ', 1)

        # 带着主要信息的那一块 複製番號" data-clipboard-text="BKD-171">
        html = re.search(r'複製番號([\s\S]+?)存入清單', html, re.DOTALL).group(1)

        # 系列 "/series/RJmR">○○に欲望剥き出しでハメまくった中出し記録。</a>
        seriesg = re.search(r'series/.+?">(.+?)</a>', html)
        jav_data.Series = seriesg.group(1) if seriesg else ''

        # 上映日 e">2019-02-01<
        releaseg = re.search(r'(\d\d\d\d-\d\d-\d\d)', html)
        jav_data.Release = releaseg.group(1) if releaseg else '1970-01-01'

        # 片长 value">175 分鍾<
        runtimeg = re.search(r'value">(\d+) 分鍾<', html)
        jav_data.Runtime = int(runtimeg.group(1)) if runtimeg else 0

        # 导演 /directors/WZg">NABE<
        directorg = re.search(r'directors/.+?">(.+?)<', html)
        jav_data.Director = directorg.group(1) if directorg else ''

        # 制作商 e"><a href="/makers/
        studiog = re.search(r'makers/.+?">(.+?)<', html)
        jav_data.Studio = studiog.group(1) if studiog else ''

        # 发行商 /publishers/pkAb">AV OPEN 2018</a><
        publisherg = re.search(r'publishers.+?">(.+?)</a><', html)
        jav_data.Publisher = publisherg.group(1) if publisherg else ''

        # 评分 star gray"></i></span>&nbsp;3.75分
        scoreg = re.search(r'star gray"></i></span>&nbsp;(.+?)分', html)
        jav_data.Score = int(float(scoreg.group(1)) * 20) if scoreg else 0

        # 演员们 /actors/M0xA">上川星空</a>  actors/P9mN">希美まゆ</a><strong class="symbol female
        actors = re.findall(r'actors/.+?">(.+?)</a><strong class="symbol female', html)
        jav_data.Actors = [i.strip() for i in actors]
        str_actors = ' '.join(jav_data.Actors)

        # 去除末尾的标题 javdb上的演员不像javlibrary使用演员最熟知的名字
        if str_actors and jav_data.Title.endswith(str_actors):
            jav_data.Title = jav_data.Title[:-len(str_actors)].strip()

        # 特征 /tags?c7=8">精选、综合</a>
        genres = re.findall(r'tags.+?">(.+?)</a>', html)
        jav_data.Genres.extend(prefect_genres(self._DICT_GENRES, genres))

        #Todo 查找图片url

    @staticmethod
    def _confirm_normal_rsp(content: str):
        return bool(re.search(r'成人影片數據庫', content) or re.search(r'頁面未找到', content))

    @staticmethod
    def _confirm_not_found(html: str):
        return bool(re.search(r'頁面未找到', html))

    def _need_update_headers(self, html: str):
        return self._confirm_cloudflare(html)

    @staticmethod
    def _update_headers():
        # Todo 实现
        pass

    # endregion

    # region 特色方法

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

    def _find_suf_min_max_in_page(self, url_page: str):
        """
        查找该网页上的最小和最大车尾

        Args:
            url_page: 车头的某一页网址

        Returns:
            最小车尾，最大车尾
        """
        html_pref = self._get_html('', url_page)
        # Todo xpath直接取第一个和最后一个
        if list_cars := etree.HTML(html_pref).xpath(Const.XPATH_DB_CARS):
            suf_min = int(extract_suf(list_cars[-1]))
            suf_max = int(extract_suf(list_cars[0]))
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

        html_tree = etree.HTML(self._get_html('', url_page))
        list_cars = html_tree.xpath(Const.XPATH_DB_CARS)

        # 这一页已经没内容了
        if not list_cars:
            raise

        suf_min = int(extract_suf(list_cars[-1]))
        suf_max = int(extract_suf(list_cars[0]))
        if not suf_max >= suf >= suf_min:
            # 不在车尾范围内
            return ''  # 这一页找不到（希望程序去下一页）

        # 这一页中和当前车牌长得相似的车牌
        list_fit_index = self._check_cars_in_page(suf, list_cars)

        if not list_fit_index:
            # suf在该页面的车尾范围内，但找不到
            raise  # db找不到

        item = html_tree.xpath(f'//*[@id="videos"]/div/div[{list_fit_index[0]}]/a/@href')[0][3:]
        status = ScrapeStatusEnum.success if len(list_fit_index) == 1 else ScrapeStatusEnum.multiple_results
        self._update_item_status(item, status)
        return item  # db找到了

    @staticmethod
    def _check_cars_in_page(suf: int, list_cars: List[str]):
        """
        在当前网页上的所有车牌中查找相似的车牌

        Args:
            suf: 当前处理车牌的车尾
            list_cars: 某一网页上的车牌

        Returns:
            和当前车牌相似的车牌，在list_cars中的坐标
        """
        return [i + 1 for i, car in enumerate(list_cars) if int(extract_suf(car)) == suf]

    def _find_in_code_pages(self, jav_file: JavFile):
        """
        遍历video_codes网页，一个一个匹配

        Args:
            car: 车牌，ID-26020

        Returns:
            html.找不到则返回空
        """
        no_page = 1
        """当前车牌 预估在第几页"""

        # region 预估当前车牌在第几页
        # 首页的车尾
        tuple_temp = self._find_suf_min_max_in_page(self._url_page(jav_file.Pref, no_page))
        # javdb没有该车头的页面
        if not tuple_temp:
            return ''  # db找不到
        suf_min, suf_max = tuple_temp
        # 通过 当前车尾 和 首页的最小车尾 的差距，除以40一页，预估在第几页
        no_page = (suf_min - jav_file.Suf) // 40 + 2 if suf_min > jav_file.Suf else 1
        """当前处理的第几页"""
        # endregion

        # region 确认车牌在预估页面之前还是之后
        # 预估页面不是首页，访问预估页面，找到最小和最大车尾
        if no_page != 1:
            if tuple_temp := self._find_suf_min_max_in_page(self._url_page(jav_file.Pref, no_page)):
                suf_min, suf_max = tuple_temp
            # 预估的页面找不到数据，即已经超出范围，比如实际只有10页，预估到12页。
            else:
                # 防止预估的no_page太大，比如HODV-21301
                no_page = min(no_page, 60)
                # 往前推，直至找到最后有数据的那一页
                while True:
                    no_page -= 1
                    if tuple_temp := self._find_suf_min_max_in_page(self._url_page(jav_file.Pref, no_page)):
                        suf_min, suf_max = tuple_temp
                        break
        # 如果比 预估页面 的最小车尾 还小，往下一页找，否则往前一页找。
        one = 1 if jav_file.Suf < suf_min else -1
        # endregion

        # region 从预估页面开始，一页一页查找
        while True:

            # 比首页收录的最大车牌还大，找不到
            if no_page == 0:
                return ''  # code page找不到

            # 在当前页面查找item
            try:
                item = self._find_target_item_in_page(self._url_page(jav_file.Pref, no_page), jav_file.Suf)
            except RuntimeError:
                # 走到尾也找不到；虽然在页面车尾范围内，但也找不到。
                return ''  # code page找不到
            # 找到了
            if item:
                return self._get_html('    >查找信息:', self._url_item(item))  # db找到了

            # 页码往后(或往前）推一页
            no_page += one
        # endregion

    # endregion
