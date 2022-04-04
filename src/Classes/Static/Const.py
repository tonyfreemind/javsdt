from dataclasses import dataclass


@dataclass(frozen=True)
class Const(object):
    # region ini用户设置
    INI = '【点我设置整理规则】.ini'
    ENCODING_INI = 'utf-8-sig'

    NODE_FORMULA = '公式元素'
    NEED_ACTORS_END_OF_TITLE = '标题末尾保留演员姓名？'

    NODE_NFO = '收集nfo'
    NEED_NFO = '是否收集nfo？'
    NAME_NFO_TITLE_FORMULA = 'title的公式'
    NEED_ZH_PLOT = 'plot是否使用中文简介？'
    EXTRA_GENRES = '额外增加以下元素到特征中'
    NEED_NFO_GENRES = '是否将特征保存到genre？'
    NEED_NFO_TAGS = '是否将特征保存到tag？'

    NODE_VIDEO = '重命名视频文件'
    NEED_RENAME_VIDEO = '是否重命名视频文件？'
    NAME_VIDEO_FORMULA = '重命名视频文件的公式'

    NODE_FOLDER = '修改文件夹'
    NEED_RENAME_FOLDER = '是否重命名或创建独立文件夹？'
    NAME_FOLDER_FORMULA = '新文件夹的公式'

    NODE_CLASSIFY = '归类影片'
    NEED_CLASSIFY = '是否归类影片？'
    NEED_CLASSIFY_FOLDER = '针对文件还是文件夹？'
    DIR_CUSTOM_CLASSIFY_TARGET = '归类的根目录'
    CLASSIFY_FORMULA = '归类的标准'

    NODE_FANART = '下载封面'
    NEED_DOWNLOAD_FANART = '是否下载封面海报？'
    NAME_FANART_FORMULA = 'fanart的公式'
    NAME_POSTER_FORMULA = 'poster的公式'
    NEED_SUBTITLE_WATERMARK = '是否为poster加上中文字幕条幅？'
    NEED_DIVULGE_WATERMARK = '是否为poster加上无码流出条幅？'

    NODE_SUBTITLE = '字幕文件'
    NEED_RENAME_SUBTITLE = '是否重命名已有的字幕文件？'

    NODE_KODI = 'kodi专用'
    NEED_ACTOR_SCULPTURE = '是否收集演员头像？'
    NEED_ONLY_CD = '是否对多cd只收集一份图片和nfo？'

    PROXY_DEFAULT = '127.0.0.1:1080'
    NODE_PROXY = '局部代理'
    NEED_PROXY = '是否使用局部代理？'
    NEED_HTTP_OR_SOCKS5 = 'http还是socks5？'
    PROXY = '代理端口'
    NEED_PROXY_LIBRARY = '是否代理javlibrary？'
    NEED_PROXY_BUS = '是否代理javbus？'
    NEED_PROXY_321 = '是否代理jav321？'
    NEED_PROXY_DB = '是否代理javdb？'
    NEED_PROXY_ARZON = '是否代理arzon？'
    NEED_PROXY_DMM = '是否代理dmm图片？'

    NODE_FILE = '原影片文件的性质'
    SURPLUS_WORDS_IN_YOUMA_SUREN = '有码素人无视多余的字母数字'
    SURPLUS_WORDS_IN_WUMA = '无码无视多余的字母数字'
    SUBTITLE_SYMBOL_WORDS = '是否中字即文件名包含'
    SUBTITLE_EXPRESSION = '是否中字的表现形式'
    DIVULGE_SYMBOL_WORDS = '是否流出即文件名包含'
    DIVULGE_EXPRESSION = '是否流出的表现形式'

    NODE_OTHER = '其他设置'
    LANGUAGE = '简繁中文？'
    URL_LIBRARY = 'javlibrary网址'
    URL_BUS = 'javbus网址'
    URL_DB = 'javdb网址'
    DB_CF_CLEARANCE = 'db的cf_clearance'
    LIBRARY_CF_CLEARANCE = 'javlibrary的cf_clearance'
    ARZON_PHPSESSID = 'arzon的phpsessid'
    TUPLE_VIDEO_TYPES = '扫描文件类型'
    INT_TITLE_LEN = '重命名中的标题长度（50~150）'

    NODE_TRAN = '百度翻译API'
    TRAN_ID = 'app id'
    TRAN_SK = '密钥'

    NODE_BODY = '百度人体分析'
    NEED_FACE = '是否需要准确定位人脸的poster？'
    AI_ID = 'appid'
    AI_AK = 'api key'
    AI_SK = 'secret key'
    # endregion

    # region 头像统计
    NODE_NO_ACTOR = '缺失的演员头像'
    # endregion

    # region 元素名称
    TITLE = '标题'
    """可能删减过的日语标题\n\n用于文件的重命名"""

    COMPLETE_TITLE = '完整标题'
    """完整的日语标题\n\n用于nfo中记录信息"""

    ZH_TITLE = '中文标题'
    """可能删减过的中文标题\n\n用于文件的重命名，如果用户没有设置翻译账户，则仍为日语标题"""

    ZH_COMPLETE_TITLE = '中文完整标题'
    """完整的中文标题\n\n用于nfo中记录信息，如果用户没有设置翻译账户，则仍为日语标题"""

    SERIES = '系列'
    STUDIO = '片商'
    PUBLISHER = '发行商'
    BOOL_SUBTITLE = '是否中字'
    BOOL_DIVULGE = '是否流出'
    CAR = '车牌'
    CAR_PREF = '车牌前缀'
    RELEASE = '发行年月日'
    RELEASE_YEAR = '发行年份'
    RELEASE_MONTH = '月'
    RELEASE_DAY = '日'
    RUNTIME = '片长'
    DIRECTOR = '导演'
    SCORE = '评分'
    ALL_ACTORS = '全部演员'
    FIRST_ACTOR = '首个演员'
    VIDEO = '视频'
    ORIGIN_FOLDER = '原文件夹名'
    ORIGIN_VIDEO = '原文件名'
    WHITESPACE = '空格'
    AV_TYPE = '影片类型'
    # endregion

    YOUMA = '有码'
    WUMA = '无码'

    # region 错误信息
    NO_IMPLEMENT_ERROR = '方法还未实现'
    # endregion

    # region 本地文件
    TXT_FAIL = '【可删除】失败记录.txt'
    TXT_WARN = '【可删除】警告信息.txt'
    TXT_RENAME = '【可删除】新旧文件名清单.txt'
    TXT_ACTORS_INCLUDED = '已收录的人员清单.txt'
    TXT_ACTORS_NOT_INCLUDED = '已收录的人员清单.txt'

    TXT_SUREN_CARS = '【素人车牌】.txt'
    EXCEL_GENRE = '【特征对照表】.xlsx'

    INI_ACTOR = '【缺失的演员头像统计For Kodi】.ini'
    INI_ACTOR_ORIGIN = 'actors_for_kodi.ini'

    EXE_CREATE_INI = '【ini】重新创建ini.exe'

    FOLDER_ACTOR = '演员头像'
    # endregion

    # region 其他
    CAR_DEFAULT = 'ABC-123'
    XPATH_DB_CARS = '//*[@id="videos"]/div/div[*]/a/div[2]/text()'
    """用于找出db的video code页面上的cars"""
    # region
