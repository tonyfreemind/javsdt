from configparser import RawConfigParser
from Classes.MyConst import Const


class Settings(object):
    def __init__(self, pattern):
        self._pattern = pattern
        conf = RawConfigParser()
        conf.read(Const.ini_file, encoding=Const.encoding)
        # ###################################################### 公式元素 ##############################################
        # 是否 去除 标题 末尾可能存在的演员姓名
        self.bool_need_actors_end_of_title = conf.get(Const.node_formula, Const.need_actors_end_of_title) == '是'
        # ###################################################### nfo ##################################################
        # 是否 收集nfo
        self.bool_nfo = conf.get(Const.node_nfo, Const.need_nfo) == '是'
        # 自定义 nfo中title的公式
        self.list_name_nfo_title = conf.get(Const.node_nfo, Const.name_nfo_title_formula)\
            .replace(Const.title, Const.complete_title).split('+')
        # 是否 在nfo中plot写入中文简介，否则写原日语简介
        self.bool_need_zh_plot = conf.get(Const.node_nfo, Const.need_zh_plot) == '是'
        # 自定义 将系列、片商等元素作为特征，因为emby不会直接在影片介绍页面上显示片商，也不会读取系列set
        list_custom_genres = conf.get(Const.node_nfo, Const.custom_genres).split('、') \
            if conf.get(Const.node_nfo, Const.custom_genres) else []
        # 自定义 将系列、片商等元素作为特征，因为emby不会直接在影片介绍页面上显示片商，也不会读取系列set
        self.list_extra_genres = [i for i in list_custom_genres if i != Const.series and i != Const.studio]
        # ？是否将“系列”写入到特征中
        self.bool_write_series = True if Const.series in list_custom_genres else False
        # ？是否将“片商”写入到特征中
        self.bool_write_studio = True if Const.studio in list_custom_genres else False
        # 是否 将特征保存到风格中
        self.bool_genre = conf.get(Const.node_nfo, Const.need_genre) == '是'
        # 是否 将 片商 作为特征
        self.bool_tag = conf.get(Const.node_nfo, Const.need_tag) == '是'
        # ###################################################### 重命名 ################################################
        # 是否 重命名 视频
        self.bool_rename_video = conf.get(Const.node_video, Const.need_rename_video) == '是'
        # 自定义 重命名 视频
        self.list_rename_video = conf.get(Const.node_video, Const.name_video_formula).split('+')
        # 是否 重命名视频所在文件夹，或者为它创建独立文件夹
        self.bool_rename_folder = conf.get(Const.node_folder, Const.need_rename_folder) == '是'
        # 自定义 新的文件夹名  示例: ['车牌', '【', '全部演员', '】']
        self.list_rename_folder = conf.get(Const.node_folder, Const.name_folder_formula).split('+')
        # ######################################################### 归类 ###############################################
        # 是否 归类jav
        self.bool_classify = conf.get(Const.node_classify, Const.need_classify) == '是'
        # 是否 针对“文件夹”归类jav，“否”即针对“文件”
        self.bool_classify_folder = conf.get(Const.node_classify, Const.need_classify_file_not_folder) == '文件夹'
        # 自定义 路径 归类的jav放到哪
        self.custom_classify_target_dir = conf.get(Const.node_classify, Const.custom_classify_target_dir)
        # 自定义 jav按什么类别标准来归类 比如: 影片类型\全部演员
        self.custom_classify_basis = conf.get(Const.node_classify, Const.classify_formula)
        # ####################################################### 图片 ################################################
        # 是否 下载图片
        self.bool_jpg = conf.get(Const.node_fanart, Const.need_download_fanart) == '是'
        # 自定义 命名 大封面fanart
        self.list_name_fanart = conf.get(Const.node_fanart, Const.name_fanart_formula).split('+')
        # 自定义 命名 小海报poster
        self.list_name_poster = conf.get(Const.node_fanart, Const.name_poster_formula).split('+')
        # 是否 如果视频有“中字”，给poster的左上角加上“中文字幕”的斜杠
        self.bool_watermark_subtitle = conf.get(Const.node_fanart, Const.need_subtitle_watermark) == '是'
        # 是否 如果视频是“无码流出”，给poster的右上角加上“无码流出”的斜杠
        self.bool_watermark_divulge = conf.get(Const.node_fanart, Const.need_divulge_watermark) == '是'
        # ##################################################### 字幕 ###################################################
        # 是否 重命名用户已拥有的字幕
        self.bool_rename_subtitle = conf.get(Const.node_subtitle, Const.need_rename_subtitle) == '是'
        # ##################################################### kodi ##################################################
        # 是否 收集演员头像
        self.bool_sculpture = conf.get(Const.node_kodi, Const.need_actor_sculpture) == '是'
        # 是否 对于多cd的影片，kodi只需要一份图片和nfo
        self.bool_cd_only = conf.get(Const.node_kodi, Const.need_only_cd) == '是'
        # ##################################################### 代理 ##################################################
        # 代理端口
        custom_proxy = conf.get(Const.node_proxy, Const.proxy).strip()
        # 代理，如果为空则效果为不使用
        proxys = {'http': f'http://{custom_proxy}', 'https': f'https://{custom_proxy}'} \
            if conf.get(Const.node_proxy, Const.need_http_or_socks5) == 'http' \
            else {'http': f'socks5://{custom_proxy}', 'https': f'socks5://{custom_proxy}'}
        # 是否 使用局部代理
        bool_proxy = conf.get(Const.node_proxy, Const.need_proxy) == '是' and custom_proxy
        # 是否 代理javlibrary
        self.proxy_library = proxys if conf.get(Const.node_proxy, Const.need_proxy_library) == '是' \
                                       and bool_proxy else {}
        # 是否 代理bus，还有代理javbus上的图片cdnbus
        self.proxy_bus = proxys if conf.get(Const.node_proxy, Const.need_proxy_bus) == '是' and bool_proxy else {}
        # 是否 代理321，还有代理javbus上的图片cdnbus
        self.proxy_321 = proxys if conf.get(Const.node_proxy, Const.need_proxy_321) == '是' and bool_proxy else {}
        # 是否 代理db，还有代理javdb上的图片
        self.proxy_db = proxys if conf.get(Const.node_proxy, Const.need_proxy_db) == '是' and bool_proxy else {}
        # 是否 代理arzon
        self.proxy_arzon = proxys if conf.get(Const.node_proxy, Const.need_proxy_arzon) == '是' and bool_proxy else {}
        # 是否 代理dmm图片，javlibrary和javdb上的有码图片几乎都是直接引用dmm
        self.proxy_dmm = proxys if conf.get(Const.node_proxy, Const.need_proxy_dmm) == '是' and bool_proxy else {}
        # ################################################### 原影片文件的性质 ##########################################
        # 自定义 无视的字母数字 去除影响搜索结果的字母数字 xhd1080、mm616、FHD-1080
        self._list_surplus_words_in_filename = conf.get(Const.node_file, Const.surplus_words_in_youma_suren).upper().split('、') \
            if self._pattern != Const.wuma \
            else conf.get(Const.node_file, Const.surplus_words_in_wuma).upper().split('、')
        # 自定义 原影片性质 影片有中文，体现在视频名称中包含这些字符
        self.list_subtitle_words_in_filename = conf.get(Const.node_file, Const.subtitle_expression).strip().split('、')
        # 自定义 是否中字 这个元素的表现形式
        self.custom_subtitle_expression = conf.get(Const.node_file, "是否中字的表现形式")
        # 自定义 原影片性质 影片是无码流出片，体现在视频名称中包含这些字符
        self.list_divulge_words_in_filename = conf.get(Const.node_file, "是否流出即文件名包含").strip().split('、')
        # 自定义 是否流出 这个元素的表现形式
        self.custom_divulge_expression = conf.get(Const.node_file, "是否流出的表现形式")
        # 自定义 原影片性质 有码
        self.av_type = conf.get(Const.node_file, self._pattern)
        # ################################################## 其他设置 ##################################################
        # 是否 使用简体中文 简介翻译的结果和jav特征会变成“简体”还是“繁体”，影响影片特征和简介。
        # self.to_language = 'zh' if config_settings.get("其他设置", "简繁中文？") == '简' else 'cht'
        self.to_language = 'zh'
        # 网址 javlibrary
        self.url_library = f'{conf.get("其他设置", "javlibrary网址").strip().rstrip("/")}/cn'
        # 网址 javbus
        self.url_bus = conf.get("其他设置", "javbus网址").strip().rstrip('/')
        # 网址 javdb
        self.url_db = conf.get("其他设置", "javdb网址").strip().rstrip('/')
        # 网址 javdb
        self.phpsessid = conf.get("其他设置", "arzon的phpsessid").strip()
        # 自定义 文件类型 只有列举出的视频文件类型，才会被处理
        self.tuple_video_types = tuple(conf.get("其他设置", "扫描文件类型").upper().split('、'))
        # 自定义 命名公式中“标题”的长度 windows只允许255字符，所以限制长度，但nfo中的标题是全部
        self.int_title_len = int(conf.get("其他设置", "重命名中的标题长度（50~150）"))
        # ####################################### 百度翻译API ####################################################
        # 账户 百度翻译api
        self.tran_id = conf.get("百度翻译API", "APP ID")
        self.tran_sk = conf.get("百度翻译API", "密钥")
        # ####################################### 百度人体分析 ####################################################
        # 是否 需要准确定位人脸的poster
        self.bool_face = conf.get("百度人体分析", "是否需要准确定位人脸的poster？") == '是'
        # 账户 百度人体分析
        self.al_id = conf.get("百度人体分析", "appid")
        self.ai_ak = conf.get("百度人体分析", "api key")
        self.al_sk = conf.get("百度人体分析", "secret key")
