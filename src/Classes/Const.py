from dataclasses import dataclass


@dataclass
class Const(object):
    # region ini用户设置
    ini = '【点我设置整理规则】.ini'
    encoding_ini = 'utf-8-sig'

    node_formula = '公式元素'
    need_actors_end_of_title = '标题末尾保留演员姓名？'

    node_nfo = '收集nfo'
    need_nfo = '是否收集nfo？'
    name_nfo_title_formula = 'title的公式'
    need_zh_plot = 'plot是否使用中文简介？'
    extra_genres = '额外增加以下元素到特征中'
    need_nfo_genres = '是否将特征保存到genre？'
    need_nfo_tags = '是否将特征保存到tag？'

    node_video = '重命名视频文件'
    need_rename_video = '是否重命名视频文件？'
    name_video_formula = '重命名视频文件的公式'

    node_folder = '修改文件夹'
    need_rename_folder = '是否重命名或创建独立文件夹？'
    name_folder_formula = '新文件夹的公式'

    node_classify = '归类影片'
    need_classify = '是否归类影片？'
    need_classify_folder = '针对文件还是文件夹？'
    dir_custom_classify_target = '归类的根目录'
    classify_formula = '归类的标准'

    node_fanart = '下载封面'
    need_download_fanart = '是否下载封面海报？'
    name_fanart_formula = 'fanart的公式'
    name_poster_formula = 'poster的公式'
    need_subtitle_watermark = '是否为poster加上中文字幕条幅？'
    need_divulge_watermark = '是否为poster加上无码流出条幅？'

    node_subtitle = '字幕文件'
    need_rename_subtitle = '是否重命名已有的字幕文件？'

    node_kodi = 'kodi专用'
    need_actor_sculpture = '是否收集演员头像？'
    need_only_cd = '是否对多cd只收集一份图片和nfo？'

    proxy_default = '127.0.0.1:1080'
    node_proxy = '局部代理'
    proxy = '代理端口'
    need_http_or_socks5 = 'http还是socks5？'
    need_proxy = '是否使用局部代理？'
    need_proxy_library = '是否代理javlibrary？'
    need_proxy_bus = '是否代理javbus？'
    need_proxy_321 = '是否代理jav321？'
    need_proxy_db = '是否代理javdb？'
    need_proxy_arzon = '是否代理arzon？'
    need_proxy_dmm = '是否代理dmm图片？'

    node_file = '原影片文件的性质'
    surplus_words_in_youma_suren = '有码素人无视多余的字母数字'
    surplus_words_in_wuma = '无码无视多余的字母数字'
    subtitle_symbol_words = '是否中字即文件名包含'
    subtitle_expression = '是否中字的表现形式'
    divulge_symbol_words = '是否流出即文件名包含'
    divulge_expression = '是否流出的表现形式'

    node_other = '其他设置'
    url_library = 'javlibrary网址'
    url_bus = 'javbus网址'
    url_db = 'javdb网址'
    arzon_phpsessid = 'arzon的phpsessid'
    tuple_video_types = '扫描文件类型'
    int_title_len = '重命名中的标题长度（50~150）'

    node_tran = '百度翻译API'
    tran_id = 'APP ID'
    tran_sk = '密钥'

    node_body = '百度人体分析'
    need_face = '是否需要准确定位人脸的poster？'
    ai_id = 'appid'
    ai_ak = 'api key'
    ai_sk = 'secret key'
    # endregion

    # region 头像统计
    ini_actor: str = '【缺失的演员头像统计For Kodi】.ini'
    node_no_actor = '缺失的演员头像'
    # endregion

    # region 元素名称
    title = '标题'
    complete_title = '完整标题'
    series = '系列'
    studio = '片商'
    # endregion

    youma = '有码'
    wuma = '无码'

    # region 错误信息
    baidu_translate_account_empty_error = '    >你没有填写百度翻译api账户!'
    baidu_translate_account_error = '    >请正确输入百度翻译API账号！'
    # endregion
