# -*- coding:utf-8 -*-
from os import sep
from configparser import RawConfigParser
from traceback import format_exc

from Classes.Static.Const import Const


class Ini(object):
    """
    ini配置

    读取【点我设置整理规则】.ini中的设置，用于其他class的依赖注入。
    """

    def __init__(self, pattern: str):
        """
        Args:
            pattern: 当前整理的模式，例如“有码”“无码”
        """
        self.pattern = pattern
        print('正在读取ini中的设置...', end='')
        try:
            conf = RawConfigParser()
            conf.read(Const.INI, encoding=Const.ENCODING_INI)
            dict_ini = self._tran_config_parser_to_dict(conf)

            # region ######################################## 1公式元素 ########################################
            self.need_actors_end_of_title = dict_ini[Const.NEED_ACTORS_END_OF_TITLE] == '是'
            """是否 去除 标题末尾 可能存在的演员姓名"""
            # endregion

            # region ######################################## 2nfo ########################################
            self.need_nfo = dict_ini[Const.NEED_NFO] == '是'
            """是否 收集nfo"""

            self.list_name_nfo_title = dict_ini[Const.NAME_NFO_TITLE_FORMULA].replace(Const.TITLE,
                                                                                      Const.COMPLETE_TITLE).split('+')
            """公式: nfo中title\n\n注意：程序中有两个标题，一个“完整标题”，一个“可能被删减的标题”。用户只需写“标题”，这里nfo实际采用“完整标题”"""

            self.need_zh_plot = dict_ini[Const.NEED_ZH_PLOT] == '是'
            """是否 在nfo中plot写入中文简介，否则写原日语简介"""

            extra_genres = dict_ini[Const.EXTRA_GENRES]
            list_extra_genres = extra_genres.split('、') if extra_genres else []
            # Todo emby对set的处理
            self.list_extra_genres = [i for i in list_extra_genres if i != Const.SERIES and i != Const.STUDIO]
            """公式: 额外添加进特征的元素\n\n允许用户将系列、片商等元素作为特征，因为emby不会直接在影片介绍页面上显示片商，也不会读取系列set"""

            self.need_series_as_genre = Const.SERIES in list_extra_genres
            """是否 将“系列”写入到特征中"""

            self.need_studio_as_genre = Const.STUDIO in list_extra_genres
            """是否 将“片商”写入到特征中"""

            self.need_nfo_genres = dict_ini[Const.NEED_NFO_GENRES] == '是'
            """是否 将特征保存到nfo的<genre>中"""

            self.need_nfo_tags = dict_ini[Const.NEED_NFO_TAGS] == '是'
            """是否 将特征保存到nfo的<tag>中"""
            # endregion

            # region ######################################## 3重命名 ########################################
            self.need_rename_video = dict_ini[Const.NEED_RENAME_VIDEO] == '是'
            """是否 重命名视频"""

            self.list_name_video = dict_ini[Const.NAME_VIDEO_FORMULA].split('+')
            """公式: 重命名视频"""

            self.need_rename_folder = dict_ini[Const.NEED_RENAME_FOLDER] == '是'
            """是否 重命名视频所在文件夹，或者为它创建独立文件夹"""

            self.list_name_folder = dict_ini[Const.NAME_FOLDER_FORMULA].split('+')
            """公式: 新文件夹名\n\n示例: '车牌', '【', '全部演员', '】'"""
            # endregion

            # region ######################################## 4归类 ########################################
            self.need_classify = dict_ini[Const.NEED_CLASSIFY] == '是'
            """是否 归类影片"""

            self.need_classify_folder = dict_ini[Const.NEED_CLASSIFY_FOLDER] == '文件夹'
            """是否 针对“文件夹”归类jav\n\n“否”即针对“文件”"""

            self.dir_custom_classify_root = dict_ini[Const.DIR_CUSTOM_CLASSIFY_TARGET]
            """路径: 用户自定义的归类的根目录\n\n用于判定出真实的归类根目录"""

            self._classify_formula = dict_ini[Const.CLASSIFY_FORMULA]
            """公式str: 影片按什么文件结构来归类\n\n比如: 影片类型\\\\全部演员”"""

            self.list_name_classify_dir = []
            """公式: 归类的目标文件夹的拼接\n\n由classify_formula切割得到"""
            # endregion

            # region ######################################## 5图片 ########################################
            self.need_fanart_poster = dict_ini[Const.NEED_DOWNLOAD_FANART] == '是'
            """是否 下载图片"""

            self.list_name_fanart = dict_ini[Const.NAME_FANART_FORMULA].split('+')
            """公式: 命名 大封面fanart"""

            self.list_name_poster = dict_ini[Const.NAME_POSTER_FORMULA].split('+')
            """公式: 命名 小海报poster"""

            self.need_subtitle_watermark = dict_ini[Const.NEED_SUBTITLE_WATERMARK] == '是'
            """是否 如果视频有“中字字幕”，给poster的左上角加上“中文字幕”的斜杠"""

            self.need_divulge_watermark = dict_ini[Const.NEED_DIVULGE_WATERMARK] == '是'
            """是否 如果视频是“无码流出”，给poster的右上角加上“无码流出”的斜杠"""
            # endregion

            # region ######################################## 6字幕 ########################################
            self.need_rename_subtitle = dict_ini[Const.NEED_RENAME_SUBTITLE] == '是'
            """是否 重命名用户已拥有的字幕"""
            # endregion

            # region ######################################## 7kodi ########################################
            self.need_actor_sculpture = dict_ini[Const.NEED_ACTOR_SCULPTURE] == '是'
            """是否 为kodi收集演员头像"""

            self.need_only_cd = dict_ini[Const.NEED_ONLY_CD] == '是'
            """是否 对于多cd的影片，只收集一份图片和nfo（kodi模式）"""
            # endregion

            # region ######################################## 8代理 ########################################
            proxy = dict_ini[Const.PROXY]  # 代理端口
            # 这里的写法会把https也用http，因为clash等代理实际不支持https
            proxys = {'http': f'http://{proxy}', 'https': f'http://{proxy}'} \
                if dict_ini[Const.NEED_HTTP_OR_SOCKS5] == 'http' \
                else {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'}
            need_proxy = dict_ini[Const.NEED_PROXY] == '是' and proxy  # 代理，如果为空则不使用

            self.proxy_library = proxys if dict_ini[Const.NEED_PROXY_LIBRARY] == '是' and need_proxy else {}
            """是否 代理javlibrary"""

            self.proxy_bus = proxys if dict_ini[Const.NEED_PROXY_BUS] == '是' and need_proxy else {}
            """是否 代理busb\n\n还有代理javbus上的图片cdnbus"""

            self.proxy_321 = proxys if dict_ini[Const.NEED_PROXY_321] == '是' and need_proxy else {}
            """是否 代理321"""

            self.proxy_db = proxys if dict_ini[Const.NEED_PROXY_DB] == '是' and need_proxy else {}
            """是否 代理db\n\n还有代理javdb上的图片"""

            self.proxy_arzon = proxys if dict_ini[Const.NEED_PROXY_ARZON] == '是' and need_proxy else {}
            """是否 代理arzon"""

            self.proxy_dmm = proxys if dict_ini[Const.NEED_PROXY_DMM] == '是' and need_proxy else {}
            """是否 代理dmm图片\n\njavlibrary和javdb上的有码图片几乎都是直接引用dmm"""
            # endregion

            # region ######################################## 9原影片文件的性质 ########################################
            if self.pattern != Const.WUMA:
                self.list_surplus_words = dict_ini[Const.SURPLUS_WORDS_IN_YOUMA_SUREN].upper().split('、')
                """字符集: 无视的字母数字\n\n去除影响搜索结果的字母数字，例如xhd1080、FHD-1080"""
            else:
                self.list_surplus_words = dict_ini[Const.SURPLUS_WORDS_IN_WUMA].upper().split('、')

            self.list_subtitle_symbol_words = dict_ini[Const.SUBTITLE_SYMBOL_WORDS].split('、')
            """字符集: 影片有字幕，体现在视频名称中包含这些字符"""

            self.subtitle_expression = dict_ini[Const.SUBTITLE_EXPRESSION]
            """是否中字 这个元素的表现形式"""

            self.list_divulge_symbol_words = dict_ini[Const.DIVULGE_SYMBOL_WORDS].split('、')
            """字符集: 影片是无码流出，体现在视频名称中包含这些字符"""

            self.divulge_expression = dict_ini[Const.DIVULGE_EXPRESSION]
            """是否流出 这个元素的表现形式"""

            self._av_type = dict_ini[self.pattern]
            """影片性质 这个元素的表现形式"""
            # endregion

            # region ######################################## 10其他设置 ########################################
            # Todo 支持繁体
            self.to_language = 'zh' if dict_ini[Const.LANGUAGE] == 'zh' else 'cht'
            """是否 使用简体中文\n\n标题、简介、特征翻译为“简体”还是“繁体”"""

            self.url_library = f'{dict_ini[Const.URL_LIBRARY].rstrip("/")}/cn'
            """网址 javlibrary"""

            self.url_bus = dict_ini[Const.URL_BUS].rstrip('/')
            """网址 javbus"""

            self.url_db = dict_ini[Const.URL_DB].rstrip('/')
            """网址 javdb"""

            self.db_cf_clearance = dict_ini[Const.DB_CF_CLEARANCE]
            """db cookies的一部分"""

            self.library_cf_clearance = dict_ini[Const.LIBRARY_CF_CLEARANCE]
            """library cookies的一部分"""

            self.arzon_phpsessid = dict_ini[Const.ARZON_PHPSESSID]
            """arzon cookies的一部分"""

            self.tuple_video_types = tuple(dict_ini[Const.TUPLE_VIDEO_TYPES].upper().split('、'))
            """集合:文件类型\n\n只有列举出的视频文件类型，才会被处理"""

            self.len_title_limit = int(dict_ini[Const.INT_TITLE_LEN])
            """命名公式中“标题”的长度\n\nwindows只允许255字符，所以限制长度，nfo中的标题不受此影响"""
            # endregion

            # region ######################################## 11百度翻译API ########################################
            self.tran_id = dict_ini[Const.TRAN_ID]
            """账户id 百度翻译api """
            self.tran_sk = dict_ini[Const.TRAN_SK]
            """账户sk 百度翻译api """
            # endregion

            # region ######################################## 12百度人体分析 ########################################
            self.need_face = dict_ini[Const.NEED_FACE] == '是'
            """是否 需要准确定位人脸的poster"""

            # 账户 百度人体分析
            self.ai_id = dict_ini[Const.AI_ID]
            """账户id 百度人体分析 """
            self.ai_ak = dict_ini[Const.AI_AK]
            """账户ak 百度人体分析 """
            self.ai_sk = dict_ini[Const.AI_SK]
            """账户sk 百度人体分析 """
            # endregion

            print('\n读取ini文件成功!\n')
        except:
            print(format_exc())
            input(f'\n无法读取ini文件，请修改它为正确格式，或者打开“{Const.EXE_CREATE_INI}”创建全新的ini！')

        self.dict_for_standard = self._get_dict_for_standard()
        """字典\n\n用于给用户自定义命名的各类元素包含其中"""

    def _get_dict_for_standard(self):
        """
        完善用于给用户命名的dict_for_standard

        1、如果用户自定义的各种命名公式中有dict_for_standard未包含的元素，则添加。
        2、得到归类路径的公式。
        """
        dict_for_standard = {Const.CAR: 'ABC-123',
                             Const.CAR_PREF: 'ABC',
                             Const.TITLE: f'{self.pattern}标题',
                             Const.COMPLETE_TITLE: f'完整{self.pattern}标题',
                             Const.DIRECTOR: f'{self.pattern}导演',
                             Const.STUDIO: f'{self.pattern}制作商',
                             Const.PUBLISHER: f'{self.pattern}发行商',
                             Const.SCORE: 0.0,
                             Const.RUNTIME: 0,
                             Const.SERIES: f'{self.pattern}系列',
                             Const.RELEASE: '1970-01-01',
                             Const.RELEASE_YEAR: '1970', Const.RELEASE_MONTH: '01', Const.RELEASE_DAY: '01',
                             Const.FIRST_ACTOR: f'{self.pattern}演员', Const.ALL_ACTORS: f'{self.pattern}演员',
                             Const.WHITESPACE: ' ',
                             '\\': sep, '/': sep,  # 文件路径分隔符
                             Const.BOOL_SUBTITLE: '',
                             Const.BOOL_DIVULGE: '',
                             Const.AV_TYPE: self._av_type,  # 自定义有码、无码、素人、FC2的对应称谓
                             Const.VIDEO: 'ABC-123',  # 当前及未来的视频文件名，不带ext
                             Const.ORIGIN_VIDEO: 'ABC-123', Const.ORIGIN_FOLDER: 'ABC-123', }
        if self.pattern == 'fc2':
            dict_for_standard[Const.CAR] = 'FC2-123'
            dict_for_standard[Const.CAR_PREF] = 'FC2'
            dict_for_standard[Const.VIDEO] = 'FC2-123'
            dict_for_standard[Const.ORIGIN_VIDEO] = 'FC2-123'
            dict_for_standard[Const.ORIGIN_FOLDER] = 'FC2-123'
        for i in self.list_extra_genres:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        for i in self.list_name_video:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        for i in self.list_name_folder:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        for i in self.list_name_nfo_title:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        for i in self.list_name_fanart:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        for i in self.list_name_poster:
            if i not in dict_for_standard:
                dict_for_standard[i] = i
        # 归类路径的组装公式
        for i in self._classify_formula.split('\\'):
            for j in i.split('+'):
                if j not in dict_for_standard:
                    dict_for_standard[j] = j
                self.list_name_classify_dir.append(j)
            self.list_name_classify_dir.append(sep)
        if self.list_name_classify_dir[-1] == sep:
            self.list_name_classify_dir.pop()
        return dict_for_standard

    @staticmethod
    def _tran_config_parser_to_dict(config: RawConfigParser):
        """
        将ini文件读取出来的内容转化为字典

        Args:
            config: 读取了ini文件的RawConfigParser

        Returns:
            ini中的内容

        Notes:
            请保证ini中的键唯一，否则会发生覆盖。
        """
        dict_dest = {}
        sections = config.sections()
        for section in sections:
            options = config.options(section)
            for option in options:
                dict_dest[option] = config.get(section, option)
        return dict_dest

    def web_url_proxy(self, website):
        """按模式返回网址"""
        if website == 'Arzon':
            return 'https://www.arzon.jp', self.proxy_arzon
        elif website == 'Dmm':
            return '', self.proxy_dmm
        elif website == 'Jav321':
            return f'https://www.jav321.com/{"cn" if self.to_language == "zh" else "tw"}', self.proxy_321
        elif website == 'JavBus':
            return self.url_bus, self.proxy_bus
        elif website == 'JavDb':
            return self.url_db, self.proxy_db
        elif website == 'JavLibrary':
            return self.url_library, self.proxy_library
        else:
            raise
