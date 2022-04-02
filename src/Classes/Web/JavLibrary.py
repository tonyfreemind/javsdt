# -*- coding:utf-8 -*-
import re
# from traceback import format_exc

from Static.Config import Ini
from Enums import ScrapeStatusEnum
from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Web.JavWeb import JavWeb
from Static.Const import Const
from Functions.Metadata.Genre import prefect_genres
from Functions.Utils.LittleUtils import update_ini_file_value
from Functions.Utils.FileUtils import replace_line_break


class JavLibrary(JavWeb):
    """
    javlibrary刮削工具

    获取影片的大部分信息，与javdb互补
    """

    def __init__(self, settings: Ini):
        appoint_symbol = '图书馆'
        headers = {
            'Cookie': f'cf_clearance={settings.library_cf_clearance};',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                          '/86.0.4240.198 Safari/537.36',
            'Host': 'www.javlibrary.com'
        }
        super().__init__(settings, appoint_symbol, headers)

    # region 重写父类方法

    def _search(self, jav_file: JavFile):
        # sourcery skip: extract-method, hoist-statement-from-if, remove-unnecessary-else, swap-if-else-branches

        # 用postman get一下【https://www.javlibrary.com/cn/vl_searchbyid.php?keyword=SSNI-580】，不要跳转，看一下返回的是啥
        html_search = self._get_html('    >搜索javlibrary:', self._url_search(jav_file))

        if itemg := re.search(r'URL=./\?v=(\w+?)"', html_search):
            # self._get_html()，不跳转，唯一搜索结果 <META HTTP-EQUIV=REFRESH CONTENT="0;URL=./?v=javlijtzru">
            item = itemg.group(1)
            self._update_item_status(item, ScrapeStatusEnum.success)
            return self._get_html('    >获取信息:', self._url_item(item))  # library找到了
        else:
            # 找“可能是多个结果的网页”上的所有items，这个正则表达式可以忽略avop-00127bod，它是近几年重置的，信息冗余
            list_results = re.findall(r'v=(jav.+?)" title="(.+?-\d+?[a-z]? .+?)"', html_search)
            if not list_results:
                return ''  # library找不到

            item1, title1 = list_results[0]  # 第1个搜索结果的item和title
            item2, title2 = list_results[1]  # 第2个搜索结果的item和title
            if title1.endswith('ク）'):
                # 在javlibrary上搜素一下SSNI-589，就能看懂这个if，第1个的是蓝光重置版
                self._update_item_status(item2, ScrapeStatusEnum.success)
                return self._get_html('    >获取信息:', self._url_item(item2))  # library找到了

            if title2.endswith('ク）'):
                # 在javlibrary上搜素一下SNIS-459，就能看懂这个if，第2个的是蓝光重置版
                self._update_item_status(item1, ScrapeStatusEnum.success)
                return self._get_html('    >获取信息:', self._url_item(item1))  # library找到了

            # 在javlibrary上搜素一下ssni58，一堆结果，如何筛选出ssni-058？
            list_cars = [title.split(' ', 1)[0] for title in [result[1] for result in list_results]]
            # 筛选 搜索结果中 和 当前车牌 基本符合的
            list_fit_index = self._check_result_cars(jav_file, list_cars)
            if not list_fit_index:
                return ''  # library找不到

            # 默认使用第一个结果
            item = list_results[list_fit_index[0]][0]
            status = ScrapeStatusEnum.success if len(list_fit_index) == 1 else ScrapeStatusEnum.multiple_results
            self._update_item_status(item, status)
            return self._get_html('    >获取信息:', self._url_item(item))  # library找到了

    def _url_item(self, item: str):
        return f'{self._URL}/?v={item}'

    def _url_search(self, jav_file: JavFile):
        return f'{self._URL}/vl_searchbyid.php?keyword={jav_file.Car}'

    def _select_special(self, html: str, jav_data: JavData):

        # 标题
        title = re.search(r'title>([A-Z].+?) - JAVLibrary</title>', html).group(1)
        print('    >Library标题:', title)
        if not jav_data.Title:
            jav_data.Title = title

        # 车牌
        if not jav_data.JavDb:
            # javdb没找到（没从javdb更新数据），Car需要更新为正确的车牌，
            car = jav_data.Title.split(' ', 1)[0]
            # 在javlibrary中，T-28 和 ID 的车牌很奇特。javlibrary是T-28XXX，而其他网站是T28-XXX；ID-20XXX，而其他网站是20ID-XXX。
            if 'T-28' in car:
                car = car.replace('T-28', 'T28-', 1)
            jav_data.Car = car

        # 精彩影评
        jav_data.Review = self._find_review(html)

        # 有大部分信息的html
        html = re.search(r'video_title"([\s\S]*?)favorite_edit', html, re.DOTALL).group(1)

        # 图片
        if coverg := re.search(r'src="(.+?)" width="600', html):
            cover_library = coverg.group(1)
            if not cover_library.startswith('http'):
                cover_library = f'http:{cover_library}'
                jav_data.CoverLibrary = cover_library
            else:
                jav_data.CoverDmm = cover_library
            jav_data.CarOrigin = cover_library.split('/')[-2]  # library上图片是dmm的，切割一下，是车牌在dmm的id

        # 发行日期
        if jav_data.Release == '1970-01-01':
            premieredg = re.search(r'(\d\d\d\d-\d\d-\d\d)', html)
            jav_data.Release = premieredg.group(1) if premieredg else '1970-01-01'

        # 片长 <td><span class="text">150</span> 分钟</td>
        if jav_data.Runtime == 0:
            runtimeg = re.search(r'span class="text">(\d+?)</span>', html)
            jav_data.Runtime = runtimeg.group(1) if runtimeg else 0

        # 导演
        if not jav_data.Director:
            directorg = re.search(r'director\.php.+?>(.+?)<', html)
            jav_data.Director = directorg.group(1) if directorg else ''

        # 制作商
        if not jav_data.Studio:
            studiog = re.search(r'maker\.php.+?>(.+?)<', html)
            jav_data.Studio = studiog.group(1) if studiog else ''

        # 发行商
        if not jav_data.Publisher:
            publisherg = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="label_', html)
            jav_data.Publisher = publisherg.group(1) if publisherg else ''

        # 演员
        if actors := re.findall(r'star\.php.+?>(.+?)<', html):
            jav_data.Actors = actors
            # 去除末尾的标题 javdb上的演员不像javlibrary使用演员最熟知的名字
            str_actors = ' '.join(jav_data.Actors)
            if str_actors and jav_data.Title.endswith(str_actors):
                jav_data.Title = jav_data.Title[:-len(str_actors)].strip()

        # 评分
        if jav_data.Score == 0:
            if scoreg := re.search(r'score">\((.+?)\)<', html):
                jav_data.Score = int(float(scoreg.group(1)) * 10)

        # 特点风格
        genres = re.findall(r'category tag">(.+?)<', html)
        jav_data.Genres.extend(prefect_genres(self._DICT_GENRES, genres))

    @staticmethod
    def _confirm_normal_rsp(content: str):
        return bool(re.search(r'JAVLibrary', content)) or bool(re.search(r'URL=./\?v', content))

    @staticmethod
    def _confirm_not_found(html: str):
        return bool(re.search(r'无法找到', html))

    def _need_update_headers(self, html: str):
        return self._confirm_cloudflare(html)

    def _update_headers(self):
        new = input('    >请输入新的javlibrary cf_clearance: ')
        self._requests.headers = self._init_headers(new)
        update_ini_file_value(Const.INI, Const.NODE_OTHER, Const.LIBRARY_CF_CLEARANCE, new)

    # endregion

    # region 特色方法

    @staticmethod
    def _find_review(html: str):
        review = ''
        if list_all_reviews := re.findall(
                r'(textarea style="display: none;" class="hidden">[\s\S]*?scoreup">\d\d+)',
                html,
                re.DOTALL,
        ):
            # 18年写的，看不懂了   (.+?\s*.*?\s*.*?\s*.*?) 下面的匹配可能很奇怪，没办法，就这么奇怪
            for rev in list_all_reviews:
                if list_reviews := re.findall(r'hidden">([\s\S]*?)</textarea>', rev, re.DOTALL):
                    review = f'{review}//{list_reviews[-1]}//'
            review = replace_line_break(review)
        if review:
            review = f'//{review}'
        return review

    @staticmethod
    def _init_headers(cf_clearance: str):
        return {
            'Cookie': f'cf_clearance={cf_clearance};',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                          '86.0.4240.198 Safari/537.36',
            'Host': 'www.javlibrary.com'
        }

    # endregion
