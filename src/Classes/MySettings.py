from configparser import RawConfigParser
from traceback import format_exc

from Classes.MyConst import Const


# 从ini读取到的设置
class Settings(object):
    def __init__(self, pattern):
        self._pattern = pattern
        print('正在读取ini中的设置...', end='')
        try:
            conf = RawConfigParser()
            conf.read(Const.ini, encoding=Const.encoding_ini)
            # ###################################################### 公式元素 ##############################################
            # 是否 去除 标题末尾 可能存在的演员姓名
            self.need_actors_end_of_title = conf.get(Const.node_formula, Const.need_actors_end_of_title) == '是'
            # ###################################################### nfo ##################################################
            # 是否 收集nfo
            self.need_nfo = conf.get(Const.node_nfo, Const.need_nfo) == '是'
            # 自定义 nfo中title的公式，注意：程序中有两个标题，一个“完整标题”，一个可能被删减的“标题”。用户只需写“标题”，这里nfo实际采用“完整标题”
            self.list_name_nfo_title = conf.get(Const.node_nfo, Const.name_nfo_title_formula).replace(Const.title, Const.complete_title).split('+')
            # 是否 在nfo中plot写入中文简介，否则写原日语简介
            self.need_zh_plot = conf.get(Const.node_nfo, Const.need_zh_plot) == '是'
            # 自定义 将系列、片商等元素作为特征，因为emby不会直接在影片介绍页面上显示片商，也不会读取系列set
            extra_genres = conf.get(Const.node_nfo, Const.extra_genres)
            list_extra_genres = extra_genres.split('、') if extra_genres else []
            # 自定义 将系列、片商等元素作为特征，因为emby不会直接在影片介绍页面上显示片商，也不会读取系列set
            self.list_extra_genres = [i for i in list_extra_genres if i != Const.series and i != Const.studio]
            # 是否 将“系列”写入到特征中
            self.need_series_as_genre = True if Const.series in list_extra_genres else False
            # 是否 将“片商”写入到特征中
            self.need_studio_as_genre = True if Const.studio in list_extra_genres else False
            # 是否 将特征保存到nfo的<genre>中
            self.need_nfo_genres = conf.get(Const.node_nfo, Const.need_nfo_genres) == '是'
            # 是否 将特征保存到nfo的<tag>中
            self.need_nfo_tags = conf.get(Const.node_nfo, Const.need_nfo_tags) == '是'
            # ###################################################### 重命名 ################################################
            # 是否 重命名 视频
            self.need_rename_video = conf.get(Const.node_video, Const.need_rename_video) == '是'
            # 自定义 重命名 视频
            self.list_name_video = conf.get(Const.node_video, Const.name_video_formula).split('+')
            # 是否 重命名视频所在文件夹，或者为它创建独立文件夹
            self.need_rename_folder = conf.get(Const.node_folder, Const.need_rename_folder) == '是'
            # 自定义 新的文件夹名  示例: ['车牌', '【', '全部演员', '】']
            self.list_name_folder = conf.get(Const.node_folder, Const.name_folder_formula).split('+')
            # ######################################################### 归类 ###############################################
            # 是否 归类jav
            self.need_classify = conf.get(Const.node_classify, Const.need_classify) == '是'
            # 是否 针对“文件夹”归类jav，“否”即针对“文件”
            self.need_classify_folder = conf.get(Const.node_classify, Const.need_classify_folder) == '文件夹'
            # 自定义 路径 归类的jav放到哪个根目录
            self.dir_custom_classify_target = conf.get(Const.node_classify, Const.dir_custom_classify_target)
            # 自定义 jav按什么类别标准来归类 比如: 影片类型\全部演员
            self.classify_formula = conf.get(Const.node_classify, Const.classify_formula)
            # 归类的目标文件夹的拼接公式
            self.list_name_dir_classify = []
            # ####################################################### 图片 ################################################
            # 是否 下载图片
            self.need_download_fanart = conf.get(Const.node_fanart, Const.need_download_fanart) == '是'
            # 自定义 命名 大封面fanart
            self.list_name_fanart = conf.get(Const.node_fanart, Const.name_fanart_formula).split('+')
            # 自定义 命名 小海报poster
            self.list_name_poster = conf.get(Const.node_fanart, Const.name_poster_formula).split('+')
            # 是否 如果视频有“中字”，给poster的左上角加上“中文字幕”的斜杠
            self.need_subtitle_watermark = conf.get(Const.node_fanart, Const.need_subtitle_watermark) == '是'
            # 是否 如果视频是“无码流出”，给poster的右上角加上“无码流出”的斜杠
            self.need_divulge_watermark = conf.get(Const.node_fanart, Const.need_divulge_watermark) == '是'
            # ##################################################### 字幕 ###################################################
            # 是否 重命名用户已拥有的字幕
            self.need_rename_subtitle = conf.get(Const.node_subtitle, Const.need_rename_subtitle) == '是'
            # ##################################################### kodi ##################################################
            # 是否 收集演员头像
            self.need_actor_sculpture = conf.get(Const.node_kodi, Const.need_actor_sculpture) == '是'
            # 是否 对于多cd的影片，kodi只需要一份图片和nfo
            self.need_only_cd = conf.get(Const.node_kodi, Const.need_only_cd) == '是'
            # ##################################################### 代理 ##################################################
            # 代理端口
            proxy = conf.get(Const.node_proxy, Const.proxy)
            # 代理，如果为空则效果为不使用
            proxys = {'http': f'http://{proxy}', 'https': f'https://{proxy}'} \
                if conf.get(Const.node_proxy, Const.need_http_or_socks5) == 'http' \
                else {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'}
            # 是否 使用局部代理
            need_proxy = conf.get(Const.node_proxy, Const.need_proxy) == '是' and proxy
            # 是否 代理javlibrary
            self.proxy_library = proxys if conf.get(Const.node_proxy, Const.need_proxy_library) == '是' and need_proxy else {}
            # 是否 代理bus，还有代理javbus上的图片cdnbus
            self.proxy_bus = proxys if conf.get(Const.node_proxy, Const.need_proxy_bus) == '是' and need_proxy else {}
            # 是否 代理321，还有代理javbus上的图片cdnbus
            self.proxy_321 = proxys if conf.get(Const.node_proxy, Const.need_proxy_321) == '是' and need_proxy else {}
            # 是否 代理db，还有代理javdb上的图片
            self.proxy_db = proxys if conf.get(Const.node_proxy, Const.need_proxy_db) == '是' and need_proxy else {}
            # 是否 代理arzon
            self.proxy_arzon = proxys if conf.get(Const.node_proxy, Const.need_proxy_arzon) == '是' and need_proxy else {}
            # 是否 代理dmm图片，javlibrary和javdb上的有码图片几乎都是直接引用dmm
            self.proxy_dmm = proxys if conf.get(Const.node_proxy, Const.need_proxy_dmm) == '是' and need_proxy else {}
            # ################################################### 原影片文件的性质 ##########################################
            # 自定义 无视的字母数字 去除影响搜索结果的字母数字 xhd1080、FHD-1080
            if self._pattern != Const.wuma:
                self.list_surplus_words = conf.get(Const.node_file, Const.surplus_words_in_youma_suren).upper().split('、')
            else:
                self.list_surplus_words = conf.get(Const.node_file, Const.surplus_words_in_wuma).upper().split('、')
            # 自定义 原影片性质 影片有中文，体现在视频名称中包含这些字符
            self.list_subtitle_symbol_words = conf.get(Const.node_file, Const.subtitle_symbol_words).split('、')
            # 自定义 是否中字 这个元素的表现形式
            self.subtitle_expression = conf.get(Const.node_file, Const.subtitle_expression)
            # 自定义 原影片性质 影片是无码流出片，体现在视频名称中包含这些字符
            self.list_divulge_symbol_words = conf.get(Const.node_file, Const.divulge_symbol_words).split('、')
            # 自定义 是否流出 这个元素的表现形式
            self.divulge_expression = conf.get(Const.node_file, Const.divulge_expression)
            # 自定义 原影片性质 有码
            self.av_type = conf.get(Const.node_file, self._pattern)
            # ################################################## 其他设置 ##################################################
            # 是否 使用简体中文 简介翻译的结果和jav特征会变成“简体”还是“繁体”，影响影片特征和简介。
            # self.to_language = 'zh' if config_settings.get(Const.node_other, "简繁中文？") == '简' else 'cht'
            self.to_language = 'zh'
            # 网址 javlibrary
            self.url_library = f'{conf.get(Const.node_other, Const.url_library).rstrip("/")}/cn'
            # 网址 javbus
            self.url_bus = conf.get(Const.node_other, Const.url_bus).rstrip('/')
            # 网址 javdb
            self.url_db = conf.get(Const.node_other, Const.url_db).rstrip('/')
            # 网址 javdb
            self.arzon_phpsessid = conf.get(Const.node_other, Const.arzon_phpsessid)
            # 自定义 文件类型 只有列举出的视频文件类型，才会被处理
            self.tuple_video_types = tuple(conf.get(Const.node_other, Const.tuple_video_types).upper().split('、'))
            # 自定义 命名公式中“标题”的长度 windows只允许255字符，所以限制长度，但nfo中的标题是全部
            self.int_title_len = int(conf.get(Const.node_other, Const.int_title_len))
            # ####################################### 百度翻译API ####################################################
            # 账户 百度翻译api
            self.tran_id = conf.get(Const.node_tran, Const.tran_id)
            self.tran_sk = conf.get(Const.node_tran, Const.tran_sk)
            # ####################################### 百度人体分析 ####################################################
            # 是否 需要准确定位人脸的poster
            self.need_face = conf.get(Const.node_body, Const.need_face) == '是'
            # 账户 百度人体分析
            self.ai_id = conf.get(Const.node_body, Const.ai_id)
            self.ai_ak = conf.get(Const.node_body, Const.ai_ak)
            self.ai_sk = conf.get(Const.node_body, Const.ai_sk)
            print('\n读取ini文件成功!\n')
        except:
            print(format_exc())
            input('\n无法读取ini文件，请修改它为正确格式，或者打开“【ini】重新创建ini.exe”创建全新的ini！')

    # 功能: （1）完善用于给用户命名的dict_for_standard，如果用户自定义的各种命名公式中有dict_for_standard未包含的元素，则添加。
    #      （2）将_custom_classify_basis按“+”“\”切割好，准备用于组装后面的归类路径。
    # 参数: 无
    # 返回: dict_for_standard; 更新self.list_name_dir_classify
    # 辅助: os.sep
    def get_dict_for_standard(self):
        dict_for_standard = {'车牌': 'ABC-123',
                             '车牌前缀': 'ABC',
                             '标题': f'{self._pattern}标题',
                             '完整标题': f'完整{self._pattern}标题',
                             '导演': f'{self._pattern}导演',
                             '制作商': f'{self._pattern}制作商',
                             '发行商': f'{self._pattern}发行商',
                             '评分': 0.0,
                             '片长': 0,
                             '系列': f'{self._pattern}系列',
                             '发行年月日': '1970-01-01', '发行年份': '1970', '月': '01', '日': '01',
                             '首个演员': f'{self._pattern}演员', '全部演员': f'{self._pattern}演员',
                             '空格': ' ',
                             '\\': sep, '/': sep,  # 文件路径分隔符
                             '是否中字': '',
                             '是否流出': '',
                             '影片类型': self._av_type,  # 自定义有码、无码、素人、FC2的对应称谓
                             '视频': 'ABC-123',  # 当前及未来的视频文件名，不带ext
                             '原文件名': 'ABC-123', '原文件夹名': 'ABC-123', }
        if self._pattern == 'fc2':
            dict_for_standard['车牌'] = 'FC2-123'
            dict_for_standard['车牌前缀'] = 'FC2'
            dict_for_standard['视频'] = 'FC2-123'
            dict_for_standard['原文件名'] = 'FC2-123'
            dict_for_standard['原文件夹名'] = 'FC2-123'
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
        for i in self.dir_custom_classify_target.split('\\'):
            for j in i.split('+'):
                if j not in dict_for_standard:
                    dict_for_standard[j] = j
                self.list_name_dir_classify.append(j)
            self.list_name_dir_classify.append(sep)
        return dict_for_standard