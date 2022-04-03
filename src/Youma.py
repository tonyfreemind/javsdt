# -*- coding:utf-8 -*-
import os
from os import sep  # 路径分隔符: 当前系统的路径分隔符 windows是“\”，linux和mac是“/”
import json
from traceback import format_exc

from Classes.Web.JavDb import JavDb
from Classes.Web.JavLibrary import JavLibrary
from Classes.Web.JavBus import JavBus
from Classes.Web.Arzon import Arzon
from Classes.Web.Dmm import Dmm
from Classes.Web.Baidu import Translator
from Classes.Handler.FileExplorer import FileExplorer
from Classes.Handler.FileAnalyzer import FileAnalyzer
from Classes.Handler.FileLathe import FileLathe
from Classes.Handler.MyLogger import MyLogger
from Classes.Static.Config import Ini
from Classes.Model.JavData import JavData
from Classes.Static.Enums import ScrapeStatusEnum
from Classes.Static.Errors import TooManyDirectoryLevelsError, SpecifiedUrlError, \
    CustomClassifyTargetDirError, DownloadFanartError
from Classes.Static.Const import Const
from FileUtils import dir_father
from Functions.Utils.Datetime import time_now
from Functions.Utils.User import choose_directory
from Functions.Utils.JsonUtils import read_json_to_dict

# region（1）准备全局工具
logger = MyLogger()
ini = Ini(Const.YOUMA)
fileExplorer = FileExplorer(ini)
fileAnalyzer = FileAnalyzer(ini)
fileLathe = FileLathe(ini)
translator = Translator(ini)
javDb = JavDb(ini)
javLibrary = JavLibrary(ini)
dmm = Dmm(ini)
javBus = JavBus(ini)
arzon = Arzon(ini)
# 当前程序文件夹 所处的 父文件夹路径 Todo 弄一个环境对象
dir_pwd_father = dir_father(os.getcwd())
# endregion

# region（2）整理程序
# 用户输入“回车”就继续选择文件夹整理
input_key = ''
while not input_key:

    # region （2.1）请用户选择需整理的文件夹，重置状态
    dir_choose = choose_directory()
    """用户选择的需要整理的文件夹"""
    # 重置一些属性状态，记录一下用户新选文件夹的操作
    logger.rest_and_record_choose(dir_choose)
    try:
        fileExplorer.rest_and_check_choose(dir_choose)
    except CustomClassifyTargetDirError as error:
        input(f'请修正上述错误后重启程序：{str(error)}')
    fileLathe.update_dir_classify_root(fileExplorer.dir_classify_root)
    # endregion

    # region （3.2）遍历所选文件夹内部进行处理
    print('...文件扫描开始...如果时间过长...请避开高峰期...\n')
    # dir_current【当前所处文件夹】，由浅及深遍历每一层文件夹，list_sub_dirs【子文件夹们】 list_sub_files【子文件们】
    for dir_current, list_sub_dirs, list_sub_files in os.walk(dir_choose):

        # 新的一层级文件夹，重置一些属性
        fileExplorer.rest_current_dir(dir_current)

        # region 当前一级文件夹内的jav情况
        # 什么文件都没有 | 当前目录是“归类完成”文件夹，无需处理
        if not list_sub_files or '归类完成' in dir_current[len(dir_choose):]:
            # or handler.judge_skip_exist_nfo(list_sub_files): | 判断这一层文件夹中有没有nfo
            continue

        # 判断文件是不是字幕文件，放入dict_subtitle_file中，字幕文件和车牌对应关系 {'c:\a\abc_123.srt': 'abc-123'}
        fileExplorer.init_dict_subtitle_file(list_sub_files)

        # 获取当前一级文件夹内，包含的jav
        fileExplorer.find_jav_files(list_sub_files)
        """存放: 需要整理的jav文件对象jav_file"""
        if not fileExplorer.len_list_jav_files:
            continue  # 没有jav，则跳出当前所处文件夹

        # 判定当前所处文件夹是否是独立文件夹，独立文件夹是指该文件夹仅用来存放该影片，而不是大杂烩文件夹，是后期移动剪切操作的重要依据
        fileExplorer.judge_separate_folder(list_sub_dirs)

        # 处理“集”的问题，（1）所选文件夹总共有多少个视频文件，包括非jav文件，主要用于显示进度（2）同一车牌有多少cd，用于cd1，cd2...的命名
        fileExplorer.init_jav_file_episodes()
        # endregion

        # region 开始处理每一部jav文件
        for jav_file in fileExplorer.list_jav_files:

            # region 显示当前进度
            print(f'>> [{jav_file.No}/{fileExplorer.sum_all_videos}]:{jav_file.Name}')
            print(f'    >发现车牌: {jav_file.Car}')
            logger.update_relative_path(jav_file.Path[len(dir_choose):])  # 影片的相对于所选文件夹的路径，用于报错
            # endregion

            try:
                dir_prefs_jsons = f'{dir_pwd_father}{sep}【重要须备份】已整理的jsons{sep}{jav_file.Pref}{sep}'
                """当前车头的jsons存放的路径"""
                path_json = f'{dir_prefs_jsons}{jav_file.Car}.json'
                """当前车牌的json存放的路径"""
                if os.path.exists(path_json):
                    # region 读取已有json
                    print(f'    >从本地json读取元数据: {path_json}')
                    jav_data = JavData(**read_json_to_dict(path_json))
                    genres = jav_data.Genres  # 特征需要单独拎出来加上“中文字幕”等
                    # endregion
                else:
                    # region 去网站获取
                    jav_data = JavData()

                    # region从javdb获取信息
                    javDb.scrape(jav_file, jav_data)
                    # Todo找到一个才报警
                    if javDb.status is ScrapeStatusEnum.not_found:
                        logger.record_warn(f'javdb找不到该车牌的信息: {jav_file.Car}，')
                    elif javDb.status is ScrapeStatusEnum.multiple_results:
                        logger.record_fail(f'javlibrary搜索到同车牌的不同视频: {jav_file.Car}，')
                    # endregion

                    # 从javlibrary获取信息
                    status = javLibrary.scrape(jav_file, jav_data)
                    if status is ScrapeStatusEnum.not_found:
                        logger.record_warn(f'javlibrary找不到该车牌的信息: {jav_file.Car}，')
                    elif status is ScrapeStatusEnum.multiple_results:
                        logger.record_fail(f'javlibrary搜索到同车牌的不同视频: {jav_file.Car}，')
                    # endregion

                    if not jav_data.JavDb and not jav_data.JavLibrary:
                        logger.record_fail(f'Javdb和Javlibrary都找不到该车牌信息: {jav_file.Car}，')
                        continue  # 结束对该jav的整理

                    # 前往javbus查找【封面】【系列】【特征】.py
                    status = javBus.scrape(jav_file, jav_data)
                    if status is ScrapeStatusEnum.multiple_results:
                        logger.record_warn(f'javbus搜索到同车牌的不同视频: {jav_file.Car}，')
                    elif status is ScrapeStatusEnum.not_found:
                        logger.record_warn(f'javbus有码找不到该车牌的信息: {jav_file.Car}，')
                    # endregion

                    # region arzon找简介
                    status = arzon.scrape(jav_file, jav_data)
                    url_search_arzon = f'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q={jav_file.Car_search}'
                    if status is ScrapeStatusEnum.exist_but_no_want:
                        jav_data.Plot = '【arzon有该影片，但找不到简介】'
                        logger.record_warn(f'找不到简介，尽管arzon上有搜索结果: {url_search_arzon}，')
                    elif status is ScrapeStatusEnum.not_found:
                        jav_data.Plot = '【影片下架，暂无简介】'
                        logger.record_warn(f'找不到简介，影片被arzon下架: {url_search_arzon}，')
                    # elif status is ScrapeStatusEnum.failed:
                    #     logger.record_warn(f'访问arzon失败，需要重新整理该简介: {url_search_arzon}，')
                    # endregion

                    # 整合genres
                    jav_data.Genres = list(set(jav_data.Genres))
                    genres = list(jav_data.Genres)

                    # 完善CompletionStatus
                    jav_data.prefect_completion_status()
                    # endregion

                    # 更新path_json
                    path_json = f'{dir_prefs_jsons}{jav_data.Car}.json'

                # region 后续完善
                # 如果 进行了翻译操作 或 不存在path_json，则保存json
                if translator.prefect_zh(jav_data) or not os.path.exists(path_json):
                    if not os.path.exists(dir_prefs_jsons):
                        os.makedirs(dir_prefs_jsons)
                    jav_data.Modify = time_now()
                    with open(path_json, 'w', encoding='utf-8') as f:
                        json.dump(jav_data.__dict__, f, indent=4)
                    print(f'    >保存本地json成功: {path_json}')

                # 完善jav_file
                fileAnalyzer.judge_subtitle_and_divulge(jav_file)
                # 完善写入nfo中的genres
                if jav_file.Bool_subtitle:  # 有“中字“，加上特征”中文字幕”
                    genres.append('中文字幕')
                if jav_file.Bool_divulge:  # 是流出无码片，加上特征'无码流出'
                    genres.append('无码流出')

                # 完善handler.dict_for_standard
                fileLathe.prefect_dict_for_standard(jav_file, jav_data)

                # 1重命名视频
                if path_new := fileLathe.rename_mp4(jav_file):
                    logger.record_fail('请自行重命名大小写: ', path_new)

                # 2 归类影片，只针对视频文件和字幕文件。注意: 第2操作和下面（第3操作+第7操作）互斥，只能执行第2操作或（第3操作+第7操作）
                fileLathe.classify_files(jav_file)

                # 3重命名文件夹。如果是针对“文件”归类（即第2步），这一步会被跳过，因为用户只需要归类视频文件，不需要管文件夹。
                fileLathe.rename_folder(jav_file)

                # 更新一下path_relative
                logger.update_relative_path(f'{sep}{jav_file.Path.replace(dir_choose, "")}')  # 影片的相对于所选文件夹的路径，用于报错

                # 4写入nfo【独特】
                fileLathe.write_nfo(jav_file, jav_data, genres)

                # 5需要两张封面图片【独特】
                if fileLathe.need_fanart_poster():
                    # 如果需要下载图片，依次去各网站下载，成功则停止
                    if (
                            fileLathe.need_download_fanart(jav_file)
                            and not javDb.download_picture(jav_data.CoverDb, fileLathe.path_fanart)
                            and not javBus.download_picture(jav_data.CoverBus, fileLathe.path_fanart)
                            and not dmm.download_picture(jav_data.CoverDmm, fileLathe.path_fanart)
                            and not javLibrary.download_picture(jav_data.CoverDmm, fileLathe.path_fanart)
                    ):
                        raise DownloadFanartError('下载fanart失败: ')
                    # 裁剪生成poster
                    fileLathe.crop_poster(jav_file)

                # 6收集演员头像【相同】
                fileLathe.collect_sculpture(jav_file, jav_data)

                # 7归类影片，针对文件夹【相同】
                fileLathe.classify_folder(jav_file)

            except SpecifiedUrlError as error:
                logger.record_fail(str(error))
                continue
            except KeyError as error:
                logger.record_fail(f'发现新的特征需要添加至【特征对照表】，请告知作者: {error}，')
                continue
            except FileExistsError as error:
                logger.record_fail(str(error))
                continue
            except TooManyDirectoryLevelsError as error:
                logger.record_fail(str(error))
                continue
            except DownloadFanartError as error:
                logger.record_fail(str(error))
                continue
            except:
                logger.record_fail(f'发生错误，如一直在该影片报错请截图并联系作者: {format_exc()}')
                continue  # 【退出对该jav的整理】
                # endregion
    # endregion

    # 当前所选文件夹完成
    logger.print_end()
    input_key = input('回车继续选择文件夹整理: ')
# endregion
