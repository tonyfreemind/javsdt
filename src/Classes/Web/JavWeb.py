# -*- coding:utf-8 -*-
import re
import requests
from typing import Dict, List
from requests.exceptions import ProxyError, SSLError
from traceback import format_exc

from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Static.Const import Const
from Classes.Static.Config import Ini
from Classes.Static.Enums import ScrapeStatusEnum
from Classes.Static.Errors import SpecifiedUrlError
from Functions.Metadata.Genre import better_dict_genres
from Functions.Metadata.Picture import check_picture
from Functions.Metadata.Car import extract_pref, extract_suf


class JavWeb(object):
    """
    网站刮削工具父类

    Notes:
        刮削后，主程序依据 self.status 判断刮削的结果，刮削到的元数据保存在 jav_data 中

    Examples:
        javdb = JavDb(ini)\n
        javdb.scrape(jav_file, jav_data)\n
        if javdb.status == success:
            刮削成功且结果唯一\n
        elif javdb.status == multiple_results:
            刮削成功但结果不唯一，警告用户\n
        elif javdb.status == exist_but_no_want:
            刮削失败，虽然在网站上能搜索到车牌，但找不到想要的元数据\n
        elif javdb.status == not_found:
            刮削失败，网站上搜不到\n
    """

    def __init__(self, settings: Ini, appoint_symbol: str, headers: Dict[str, str]):
        if self.__class__ is JavWeb:
            raise Exception("<JavWeb>不能被实例化")

        website = self.__class__.__name__  # 当前类名，表示处理模式，例如“JavBus”
        tuple_temp: tuple[str, dict] = settings.web_url_proxy(website)

        self._URL: str = tuple_temp[0]
        """网址"""

        self._requests = self._create_session(tuple_temp[1], headers)
        """requests服务"""

        self._DICT_GENRES = better_dict_genres(website, settings.to_language)
        """优化后的genres"""

        self._APPOINT_SYMBOL = appoint_symbol
        """指定网址的标志\n\ndb是仓库，library是图书馆，bus是公交车。arzon是阿如。"""

        self._item = Const.CAR_DEFAULT
        """
        车牌在网站上的item
        
        例如“https://javdb35.com/v/JPx8”的JPx8，“https://www.javlibrary.com/cn/?v=javliadfy4”的javliadfy4，
        “https://www.seejav.men/SW-028_2011-05-07”的SW-028_2011-05-07，“https://www.arzon.jp/item_706193.html”的706193。
        如果刮削成功则更新它，最终交给jav_data。
        """

        self.status = ScrapeStatusEnum.not_found
        """刮削状态\n\n搜寻过程中，"""

    def scrape(self, jav_file: JavFile, jav_data: JavData):
        """
        获取网站上的内容

        Args:
            jav_file: jav视频文件对象
            jav_data: jav元数据对象
        """
        self._reset()

        html = self._find_target_html(jav_file)
        """当前车牌所在的html"""
        if html:
            self._select_normal(jav_data)
            self._select_special(html, jav_data)

    def _update_item_status(self, item: str, status: ScrapeStatusEnum):
        """（成功找到）更新item和status"""
        self._item = item
        self.status = status

    @staticmethod
    def _create_session(proxies: Dict[str, str], headers: Dict[str, str]):
        """
        初始化requests服务

        Args:
            proxies: 代理
            headers: 请求头

        Returns:
            为某个网站定制的requests.session
        """
        rqs = requests.Session()
        rqs.proxies = proxies
        rqs.headers = headers
        return rqs

    def _find_target_html(self, jav_file: JavFile):
        """
        获取车牌所在html

        两种方式直至成功找到html：(1)用户指定，则用指定网址；(2)搜索车牌。

        Args:
            jav_file: jav视频文件对象

        Returns:
            html
        """
        if self._APPOINT_SYMBOL in jav_file.Name:
            # 用户指定了网址
            return self._appoint(jav_file)
        else:
            return self._search(jav_file)

    def _appoint(self, jav_file: JavFile):
        """
        从用户指定的网址中获取目标html

        Examples:
            用户将视频文件命名为“sw-028仓库JPx8.图书馆javliadfy4.公交车SW-028_2011-05-07.阿如706193.mp4”，
            即将sw-028指定为“https://javdb35.com/v/JPx8”，“https://www.javlibrary.com/cn/?v=javliadfy4”，
            “https://www.seejav.men/SW-028_2011-05-07”，“https://www.arzon.jp/item_706193.html”。
            用户可以指定一个或多个。

        Raises:
            指定的格式不正确 || 指定的网页上没内容 => 主程序终止

        Args:
            jav_file: jav视频文件对象

        Returns:
            目标html
        """
        item_appointg = re.search(rf'{self._APPOINT_SYMBOL}(.+?)\.', jav_file.Name)
        if not item_appointg:
            # 指定的格式不正确
            raise SpecifiedUrlError(f'你指定的网址的格式有问题: {self.__class__.__name__} {jav_file.Name}')
        item_appoint = item_appointg.group(1)
        url_appoint = self._url_item(item_appoint)
        html_appoint = self._get_html('    >前往指定网址:', url_appoint)
        if self._confirm_not_found(html_appoint):
            # 指定的网页上没内容，报错
            raise SpecifiedUrlError(f'你指定的网址找不到jav: {url_appoint}，')
        # 用户指定正确，更新item
        self._update_item_status(item_appoint, ScrapeStatusEnum.success)
        return html_appoint

    def _request_url(self, url: str, allow_redirects=True):
        try:
            rsp = self._requests.get(url, timeout=(6, 7), allow_redirects=allow_redirects)
        except ProxyError:
            # 代理出错，用户可能想使用代理，但实际没开代理软件
            print(f'    >通过代理失败，重新尝试... {url}')
            return None
        except SSLError:
            # 2种情况（1）网址是https，requests也走https，但代理只支持http，导致证书验证不通过（2）用户的代理是公用代理，访问太频繁被拒绝
            print(f'    >打开网页失败，网站拒绝了你的请求，你可能在使用公共的代理...{url}')
            return None
        except:
            # 其他出错
            # print(format_exc())
            print(f'    >打开网页失败，重新尝试... {url}')
            return None
        return rsp

    def _get_html(self, aim: str, url: str):
        """
        获取html

        Args:
            aim: 目的描述
            url: 网址

        Returns:
            html
        """
        # library不需要跳转
        website = self.__class__.__name__
        allow_redirects = (website != 'JavLibrary')

        if aim:
            print(aim, url)

        for _ in range(3):
            rsp = self._request_url(url, allow_redirects)
            if rsp is None:
                continue
            rsp.encoding = 'utf-8'
            rsp_content = rsp.text
            # 响应内容是否正常
            if self._confirm_normal_rsp(rsp_content):
                # 正常响应
                return rsp_content
            elif self._need_update_headers(rsp_content):
                # 网站遇到某些特殊情况要更新headers，比如cloudflare、18岁验证
                print('    >打开网页失败，需要更新headers...')
                self._update_headers()
                continue
            elif self._confirm_ban(rsp_content):
                # 被网站封禁ip
                input(f'    >被{website}网站封禁: {rsp_content}')
            print('    >打开网页失败，空返回...重新尝试...')
        input(f'>>请检查你的网络环境是否可以打开: {url}')

    def download_picture(self, url: str, path: str):
        """下载图片"""
        website = self.__class__.__name__

        if not url:
            print(f'    >{website}没找到图片')
            return False

        if website == 'JavBus':
            url = f'{self._URL}/pics/cover/{url}'

        print(f'    >从{self.__class__.__name__}下载封面:', url)
        for _ in range(3):
            if not (rsp := self._request_url(url)):
                print('    >下载失败，重新下载....')
                continue
            with open(path, 'wb') as pic:
                for chunk in rsp:
                    pic.write(chunk)
            if not check_picture(path):
                print('    >下载失败，重新下载....')
                continue
            print('    >fanart.jpg下载成功')
            return True
        print(f'    >从{website}下载图片失败')
        return False

    def _select_normal(self, jav_data: JavData):
        """（找到目标网页后）更新信息"""
        # 更新网站对应的item
        setattr(jav_data, self.__class__.__name__, self._item)

    def _reset(self):
        """开始处理时，重置状态"""
        self._item = Const.CAR_DEFAULT
        self.status = ScrapeStatusEnum.not_found
        self._reset_special()

    @staticmethod
    def _confirm_cloudflare(html: str):
        return bool(re.search(r'Cloudflare', html, re.I))

    @staticmethod
    def _check_result_cars(jav_file: JavFile, list_cars: List[str]):
        """
        筛选 搜索结果 和 当前处理车牌 相同的 几个结果

        Args:
            jav_file: jav视频文件对象
            list_cars: （搜索结果页面上）车牌

        Returns:
            符合预期的items
        """
        return [
            index
            for index, car_temp in enumerate(list_cars)
            if extract_pref(car_temp) == jav_file.Pref
               and extract_suf(car_temp) == jav_file.Suf
        ]

    # region 被子类重写

    @staticmethod
    def _search(jav_file: JavFile) -> str:
        """
        在网站上查找车牌，得到目标html

        Returns:
            目标html，找不到则返回空
        """
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    @staticmethod
    def _url_item(item: str) -> str:
        """用item拼接出车牌所在网址"""
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    @staticmethod
    def _url_search(jav_file: JavFile) -> str:
        """搜索用的网址"""
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    @staticmethod
    def _select_special(html: str, jav_data: JavData) -> None:
        """
        从html中筛选出所需的各种信息

        Args:
            html: 网页
            jav_data: JavData

        Returns:
            刮削结果
        """
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    @staticmethod
    def _confirm_normal_rsp(content: str) -> bool:
        """
        检查是否是预期响应

        网站可能响应的是cloudflare检测，不是预期的jav网页。

        Returns:
            是否是预期响应
        """
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    @staticmethod
    def _confirm_not_found(html: str) -> bool:
        """
        确认是没内容的页面

        Args:
            html: 网页

        Returns:
            没内容 => True
        """
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    @staticmethod
    def _confirm_ban(html: str):
        """
        是否被网站封禁IP

        Args:
            html: 网页

        Returns:
            是否需要更新
        """
        return False

    @staticmethod
    def _need_update_headers(html: str) -> bool:
        """
        是否需要更新headers

        headers失效，需要更新，比如cloudflare通行证过期，arzon的成人通行证过期

        Args:
            html: 网页

        Returns:
            是否需要更新
        """
        return False

    @staticmethod
    def _update_headers() -> None:
        """更新headers"""
        pass

    @staticmethod
    def _reset_special():
        pass

    @staticmethod
    def _init_headers(cf_clearance: str, url: str = ''):
        """
        更新headers

        Args:
            cf_clearance: cloudflare通行证
            url: host
        """
        raise AttributeError(Const.NO_IMPLEMENT_ERROR)

    # endregion

    # Todo 测试方法
    def test(self, url: str):
        return self._get_html('测试:', url)

    def test_update_headers(self, headers: dict):
        self._requests.headers = headers
