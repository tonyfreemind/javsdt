from dataclasses import dataclass


@dataclass
class Const(object):
    ini_file: str = '【点我设置整理规则】.ini'
    encoding = 'utf-8-sig'

    node_formula: str = '公式元素'
    need_actors_end_of_title: str = '标题末尾保留演员姓名？'

    node_nfo: str = '收集nfo'
    need_nfo = '是否收集nfo？'
    name_nfo_title_formula: str = 'title的公式'
    need_zh_plot = 'plot是否使用中文简介？'
    custom_genres = '额外增加以下元素到特征中'
    need_genre = '是否将特征保存到genre？'
    need_tag = '是否将特征保存到tag？'

    node_video = '重命名视频文件'
    need_rename_video = '是否重命名视频文件？'
    name_video_formula = '重命名视频文件的公式'

    node_folder = '修改文件夹'
    need_rename_folder = '是否重命名或创建独立文件夹？'
    name_folder_formula = '新文件夹的公式'

    node_classify = '归类影片'
    need_classify = '是否归类影片？'
    need_classify_file_not_folder = '针对文件还是文件夹？'
    custom_classify_target_dir = '归类的根目录'
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

    node_proxy = '局部代理'
    proxy = '代理端口'
    need_http_or_socks5 = 'http还是socks5？'
    proxy_default = '127.0.0.1:1080'
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
    subtitle_expression = '是否中字即文件名包含'




    title = '标题'
    complete_title = '完整标题'
    series = '系列'
    studio = '片商'
    youma = '有码'
    wuma = '无码'
