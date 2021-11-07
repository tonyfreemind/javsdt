# -*- coding:utf-8 -*-
import os
from os import sep    # 路径分隔符: 当前系统的路径分隔符 windows是“\”，linux和mac是“/”
import json
from traceback import format_exc

from Classes.Web.JavDb import JavDb
from Classes.Web.JavLibrary import JavLibrary
from Classes.Web.JavBus import JavBus
from Classes.Web.Arzon import Arzon
from Classes.FileExplorer import FileExplorer
from Classes.FileAnalyzer import FileAnalyzer
from Classes.Stantdard import Standard
from Classes.MyLogger import Logger
from Classes.Baidu import Translator

from Classes.Config import Ini
from Classes.Model.JavData import JavData
from Classes.Enums import ScrapeStatusEnum
from Classes.Errors import TooManyDirectoryLevelsError, SpecifiedUrlError, CustomClassifyTargetDirError
from Classes.Const import Const

from Functions.Progress.User import choose_directory
from Functions.Utils.JsonUtility import read_json_to_dict


# region（1）准备全局工具
ini = Ini(Const.youma)
fileExplorer = FileExplorer(ini)
fileAnalyzer = FileAnalyzer(ini)
javDb = JavDb(ini)
javLibrary = JavLibrary(ini)
javBus = JavBus(ini)
arzon = Arzon(ini)
translator = Translator(ini)
standard = Standard(ini)
logger = Logger()
# 当前程序文件夹 所处的 父文件夹路径
dir_pwd_father = os.path.dirname(os.getcwd())
# endregion

# region（2）整理程序
# 用户输入“回车”就继续选择文件夹整理
input_key = ''
while not input_key:

    # region （2.1）请用户选择需整理的文件夹；校验归类的目标文件夹的合法性。
    logger.rest()
    dir_choose = choose_directory()
    """用户选择的需要整理的文件夹"""
    # 在txt中记录一下用户的这次操作，在某个时间选择了某个文件夹
    logger.record_start(dir_choose)
    # 新的所选文件夹，重置一些属性
    try:
        fileExplorer.rest_when_choose(dir_choose)
    except CustomClassifyTargetDirError as error:
        input(f'请修正上述错误后重启程序：{str(error)}')
        # os.system('pause')
    # endregion

    # region （3.2）遍历所选文件夹内部进行处理
    print('...文件扫描开始...如果时间过长...请避开高峰期...\n')
    # dir_current【当前所处文件夹】，由浅及深遍历每一层文件夹，list_sub_dirs【子文件夹们】 list_sub_files【子文件们】
    for dir_current, list_sub_dirs, list_sub_files in os.walk(dir_choose):
        # 新的一层级文件夹，重置一些属性
        fileExplorer.rest_current_dir(dir_current)
        # region （3.2.1）当前文件夹内包含jav及字幕文件的状况: 有多少视频，其中多少jav，同一车牌多少cd，当前文件夹是不是独立文件夹
        # （3.2.1.1）什么文件都没有 | 当前目录是“归类完成”文件夹，无需处理
        if not list_sub_files or '归类完成' in dir_current[len(dir_choose):]:
            # or handler.judge_skip_exist_nfo(list_sub_files): | 判断这一层文件夹中有没有nfo
            continue

        # （3.2.1.2）判断文件是不是字幕文件，放入dict_subtitle_file中，字幕文件和车牌对应关系 {'c:\a\abc_123.srt': 'abc-123'}
        fileExplorer.init_dict_subtitle_file(list_sub_files)
        # （3.2.1.3）获取当前所处文件夹，子一级内，包含的jav，放入list_jav_files 存放: 需要整理的jav文件对象jav_file;
        list_jav_files = fileExplorer.get_list_jav_files(list_sub_files)
        # （3.2.1.4）没有jav，则跳出当前所处文件夹
        if not list_jav_files:
            continue
        # （3.2.1.5）判定当前所处文件夹是否是独立文件夹，独立文件夹是指该文件夹仅用来存放该影片，而不是大杂烩文件夹，是后期移动剪切操作的重要依据
        fileExplorer.judge_separate_folder(len(list_jav_files), list_sub_dirs)
        # Bool_in_separate_folder是类属性，不是实例属性，修改类属性会将list_jav_files中的所有jav_file的Bool_in_separate_folder同步
        # （3.2.1.6）处理“集”的问题，（1）所选文件夹总共有多少个视频文件，包括非jav文件，主要用于显示进度（2）同一车牌有多少cd，用于cd2...命名
        fileExplorer.init_jav_file_episodes(list_jav_files)
        # endregion

        # region（3.2.2）开始处理每一部jav文件
        for jav_file in list_jav_files:
            try:
                # region（3.2.2.1）当前进度
                print(f'>> [{jav_file.No}/{fileExplorer.sum_all_videos()}]:{jav_file.Name}')
                print(f'    >发现车牌: {jav_file.Car}')
                logger.path_relative = jav_file.Path[len(dir_choose):]  # 影片的相对于所选文件夹的路径，用于报错
                # endregion

                dir_prefs_jsons = f'{dir_pwd_father}{sep}【重要须备份】已整理的jsons{sep}{jav_file.Pref}{sep}'
                path_json = f'{dir_prefs_jsons}{jav_file.Car}.json'
                if os.path.exists(path_json):
                    # region 读取已有json
                    print(f'    >从本地json读取元数据: {path_json}')
                    jav_model = JavData(**read_json_to_dict(path_json))
                    genres = jav_model.Genres
                    # endregion
                else:
                    # region 去网站获取
                    jav_model = JavData()
                    # region（3.2.2.2）从javdb获取信息
                    status = javDb.scrape(jav_file, jav_model)
                    if status == ScrapeStatusEnum.db_not_found:
                        logger.record_warn(f'javdb找不到该车牌的信息: {jav_file.Car}，')
                    # endregion

                    # region（3.2.2.3）从javlibrary获取信息
                    status = javLibrary.scrape(jav_file, jav_model)
                    if status == ScrapeStatusEnum.library_not_found:
                        logger.record_warn(f'javlibrary找不到该车牌的信息: {jav_file.Car}，')
                    elif status == ScrapeStatusEnum.library_multiple_search_results:
                        logger.record_warn(f'javlibrary搜索到同车牌的不同视频: {jav_file.Car}，')
                    # endregion

                    if not jav_model.Javdb and not jav_model.Javlibrary:
                        logger.record_fail(f'Javdb和Javlibrary都找不到该车牌信息: {jav_file.Car}，')
                        continue  # 结束对该jav的整理

                    # region（3.2.2.4）前往javbus查找【封面】【系列】【特征】.py
                    status = javBus.scrape(jav_file, jav_model)
                    if status == ScrapeStatusEnum.bus_multiple_search_results:
                        logger.record_warn(f'部分信息可能错误，javbus搜索到同车牌的不同视频: {jav_file.Car_id}，')
                    elif status == ScrapeStatusEnum.bus_not_found:
                        logger.record_warn(f'javbus有码找不到该车牌的信息: {jav_file.Car_id}，')
                    # endregion

                    # region（3.2.2.5）arzon找简介
                    status = arzon.scrape(jav_file, jav_model)
                    url_search_arzon = f'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q={jav_file.Car_id.replace("-", "")}'
                    if status == ScrapeStatusEnum.arzon_exist_but_no_plot:
                        logger.record_warn(f'找不到简介，尽管arzon上有搜索结果: {url_search_arzon}，')
                    elif status == ScrapeStatusEnum.arzon_not_found:
                        logger.record_warn(f'找不到简介，影片被arzon下架: {url_search_arzon}，')
                    elif status == ScrapeStatusEnum.interrupted:
                        logger.record_warn(f'访问arzon失败，需要重新整理该简介: {url_search_arzon}，')
                    # endregion

                    # 整合genres
                    jav_model.Genres = list(set(jav_model.Genres))
                    # 我之前错误的写法是 genrs = jav_model.Genrs，导致genrs发生改变后，jav_model.Genrs也发生了变化
                    genres = [genre for genre in jav_model.Genres]

                    # 完善jav_model.CompletionStatus
                    jav_model.prefect_completion_status()
                    # endregion

                # region（3.2.3）后续完善
                # 如果用户 首次整理该片不存在path_json 或 如果这次整理用户正确地输入了翻译账户，则保存json
                if os.path.exists(path_json) or translator.prefect_zh(jav_model):
                    if not os.path.exists(dir_prefs_jsons):
                        os.makedirs(dir_prefs_jsons)
                    with open(path_json, 'w', encoding='utf-8') as f:
                        json.dump(jav_model.__dict__, f, indent=4)
                    print(f'    >保存本地json成功: {path_json}')

                # 完善jav_file
                fileAnalyzer.judge_subtitle_and_divulge(jav_file)
                # 完善写入nfo中的genres
                if jav_file.Bool_subtitle:  # 有“中字“，加上特征”中文字幕”
                    genres.append('中文字幕')
                if jav_file.Bool_divulge:  # 是流出无码片，加上特征'无码流出'
                    genres.append('无码流出')

                # 完善handler.dict_for_standard
                standard.prefect_dict_for_standard(jav_file, jav_model)
                # endregion

                # 1重命名视频
                path_new = standard.rename_mp4(jav_file)
                if path_new:
                    logger.record_fail(f'请自行重命名大小写: ', path_new)

                # 2 归类影片，只针对视频文件和字幕文件。注意: 第2操作和下面（第3操作+第7操作）互斥，只能执行第2操作或（第3操作+第7操作）
                standard.classify_files(jav_file)

                # 3重命名文件夹。如果是针对“文件”归类（即第2步），这一步会被跳过，因为用户只需要归类视频文件，不需要管文件夹。
                standard.rename_folder(jav_file)

                # 更新一下path_relative
                logger.path_relative = f'{sep}{jav_file.Path.replace(dir_choose, "")}'  # 影片的相对于所选文件夹的路径，用于报错

                # 4写入nfo【独特】
                standard.write_nfo(jav_file, jav_model, genres)

                # 5需要两张封面图片【独特】
                standard.download_fanart(jav_file, jav_model)

                # 6收集演员头像【相同】
                standard.collect_sculpture(jav_file, jav_model)

                # 7归类影片，针对文件夹【相同】
                standard.classify_folder(jav_file)

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
            except:
                logger.record_fail(f'发生错误，如一直在该影片报错请截图并联系作者: {format_exc()}')
                continue  # 【退出对该jav的整理】
        # endregion
    # endregion

    # 当前所选文件夹完成
    print('\n当前文件夹完成，', end='')
    logger.print_end(dir_choose)
    input_key = input('回车继续选择文件夹整理: ')
# endregion
