# -*- coding:utf-8 -*-
import os
from os import sep  # 系统路径分隔符
import re

from Classes.Model.JavFile import JavFile
from Config import Ini
from Errors import CustomClassifyTargetDirError
from Functions.Progress.Prepare import get_suren_cars
from Functions.Metadata.Car import find_car_fc2, find_car_youma


# 设置
class FileExplorer(object):
    """磁盘文件检索器\n
    在磁盘中搜索发现jav视频文件，构建javFile对象"""

    def __init__(self, ini: Ini):
        self._pattern = ini.pattern
        """当前主程序的整理模式(youma, wuma, fc2)"""
        self._need_classify = ini.need_classify
        """需要归类"""
        self._need_classify_folder = ini.need_classify_folder
        """归类是针对【文件夹】而不是【文件】"""
        self._need_rename_folder = ini.need_rename_folder
        """需要重命名文件夹或创建新的独立文件夹"""
        self._dir_custom_classify_target = ini.dir_custom_classify_target
        """归类的根目录"""
        self._tuple_video_types = ini.tuple_video_types
        """视频文件类型"""
        self._list_surplus_words = ini.list_surplus_words
        """视频文件名中多余的、干扰车牌的文字"""

        # region 本次程序启动通用
        self._list_suren_cars = get_suren_cars()
        """素人车牌前缀\n\n如果当前处理模式是youma、wuma，让程序能跳过这些素人车牌"""
        self._need_rename_folder = self.judge_need_rename_folder()
        """是否需要重命名文件夹"""
        # endregion

        # region 每次新选择文件夹通用
        self._dir_choose = ''
        """用户此次选择的文件夹"""
        self._dir_classify_target = ''
        """归类的目标根文件夹"""
        self._no_current = 0
        """当前视频（包括非jav）的编号\n\n用于显示进度、获取当前文件夹内视频数量"""
        self._sum_videos_in_choose_dir = 0
        """此次所选文件夹内视频总数"""
        # endregion

        # region 主程序for循环的每一级文件夹通用
        self._dir_current = ''
        """主程序for循环所处的这一级文件夹路径"""
        self._dict_subtitle_file = {}
        """存储字幕文件和车牌对应关系\n\n例如{ 'c:/a/abc_123.srt': 'abc-123' }，用于构建视频文件的字幕体系"""
        self._dict_car_episode = {}
        """存储每一车牌的集数\n\n例如{'abc-123': 1, def-789': 2} 是指 abc-123只有1集，def-789有2集，主要用于理清同一车牌的兄弟姐妹"""
        self._sum_videos_in_current_dir = 0
        """主程序for循环所处的这一级文件夹包含的视频总数\n\n用于判断这一级文件夹是否是独立文件夹"""
        # endregion

    # region 文件夹变化后的重置
    def rest_when_choose(self, dir_choose:str):
        """用户选择新文件夹后重置类实例属性\n
        Args:
            dir_choose: 用户新选择的文件夹路径
        Returns:
            void; 更新实例属性
        """
        self._dir_choose = dir_choose
        # self.dir_classify_target = ''  通过check_classify_target_directory重置
        self.check_classify_target_directory()
        self._no_current = 0
        self._sum_videos_in_choose_dir = self.count_num_videos()

    def rest_current_dir(self, dir_current:str):
        """主程序for循环，每进入新一级文件夹的重置\n
        Args:
            dir_current: 当前所处文件夹
        Returns:
            void; 更新实例属性
        """
        self._dir_current = dir_current
        self._dict_subtitle_file = {}
        self._dict_car_episode = {}
        self._sum_videos_in_current_dir = 0
    # endregion

    # region 修改文件夹
    def judge_need_rename_folder(self):
        """判断到底要不要 重命名文件夹或者创建新的文件夹\n
        Returns:
            bool
        """
        if self._need_classify:  # 如果需要归类
            if self._need_classify_folder:  # 并且是针对文件夹
                return True  # 那么必须重命名文件夹或者创建新的文件夹
        else:  # 不需要归类
            if self._need_rename_folder:  # 但是用户本来就在ini中写了要重命名文件夹
                return True
        return False
    # endregion

    def check_classify_target_directory(self):
        """检查“用户设置的归类根目录”的合法性\n
        Returns:
            void; update实例属性
        """
        # 检查 归类根目录 的合法性
        if self._need_classify:
            dir_custom_classify_target = self._dir_custom_classify_target.rstrip(sep)
            # 用户使用默认的“所选文件夹”
            if dir_custom_classify_target == '所选文件夹':
                self._dir_classify_target = f'{self._dir_choose}{sep}归类完成'
            # 归类根目录 是 用户输入的路径c:\a，继续核实合法性
            else:
                # 用户输入的路径 不是 所选文件夹
                if dir_custom_classify_target != self._dir_choose:
                    if dir_custom_classify_target[:2] != self._dir_choose[:2]:
                        raise CustomClassifyTargetDirError(f'归类的根目录: 【{dir_custom_classify_target}】与所选文件夹不在同一磁盘，无法归类！请修正！')
                    if not os.path.exists(dir_custom_classify_target):
                        raise CustomClassifyTargetDirError(f'归类的根目录: 【{dir_custom_classify_target}】不存在！无法归类！请修正！')
                    self._dir_classify_target = dir_custom_classify_target
                # 用户输入的路径 就是 所选文件夹
                else:
                    self._dir_classify_target = f'{self._dir_choose}{sep}归类完成'
        else:
            self._dir_classify_target = ''

    def init_dict_subtitle_file(self, list_sub_files: list):
        """收集文件们中的字幕文件，存储在self.dict_subtitle_file\n
        Args:
            list_sub_files: (当前一级文件夹的)子文件们
        Returns:
            void; 更新self._dict_subtitle_file
        """
        for file_raw in list_sub_files:
            file_temp = file_raw.upper()
            if file_temp.endswith(('.SRT', '.VTT', '.ASS', '.SSA', '.SUB', '.SMI',)):
                if self._pattern != 'Fc2':
                    # 有码无码不处理FC2
                    if 'FC2' in file_temp:
                        continue
                    # 去除用户设置的、干扰车牌的文字
                    for word in self._list_surplus_words:
                        file_temp = file_temp.replace(word, '')
                    # 得到字幕文件名中的车牌
                    subtitle_car = find_car_youma(file_temp, self._list_suren_cars)
                else:
                    # 仅处理fc2
                    if 'FC2' not in file_temp:
                        continue  # 【跳出2】
                    # 得到字幕文件名中的车牌
                    subtitle_car = find_car_fc2(file_temp)
                # 将该字幕文件和其中的车牌对应到dict_subtitle_file中
                if subtitle_car:
                    self._dict_subtitle_file[file_raw] = subtitle_car

    # 功能:
    # 参数: list_sub_files（当前文件夹的）子文件们
    # 返回: list_jav_files；更新self.dict_car_episode
    # 辅助: JavFile
    def get_list_jav_files(self, list_sub_files):
        """发现jav视频文件\n
        找出list_sub_files中的jav视频文件，实例每一个jav视频文件为javfile对象，存储为list\n
        Args:
            list_sub_files: (当前所处一级文件夹的)子文件们
        Returns:
            list <JavFile>
        """
        list_jav_files = []  # 存放: 需要整理的jav_file
        for file_raw in list_sub_files:
            file_temp = file_raw.upper()
            if file_temp.endswith(self._tuple_video_types) and not file_temp.startswith('.'):
                self._no_current += 1
                self._sum_videos_in_current_dir += 1
                if 'FC2' in file_temp:
                    continue
                for word in self._list_surplus_words:
                    file_temp = file_temp.replace(word, '')
                # 得到视频中的车牌
                car = find_car_youma(file_temp, self._list_suren_cars)
                if car:
                    try:
                        self._dict_car_episode[car] += 1  # 已经有这个车牌了，加一集cd
                    except KeyError:
                        self._dict_car_episode[car] = 1  # 这个新车牌有了第一集
                    # 这个车牌在dict_subtitle_files中，有它的字幕。
                    if car in self._dict_subtitle_file.values():
                        subtitle_file = list(self._dict_subtitle_file.keys())[
                            list(self._dict_subtitle_file.values()).index(car)]
                        del self._dict_subtitle_file[subtitle_file]
                    else:
                        subtitle_file = ''
                    carg = re.search(r'ID-(\d\d)(\d+)', car)
                    if carg:
                        car_id = f'{carg.group(1)}ID-{carg.group(2)}'
                    else:
                        car_id = car
                    # 将该jav的各种属性打包好，包括原文件名带扩展名、所在文件夹路径、第几集、所属字幕文件名
                    jav_struct = JavFile(car, car_id, file_raw, self._dir_current, self._dict_car_episode[car],
                                         subtitle_file,
                                         self._no_current)
                    list_jav_files.append(jav_struct)
                else:
                    print(f'>>无法处理: {self._dir_current[len(self._dir_choose):]}{sep}{file_raw}')
        return list_jav_files

    # 功能：所选文件夹总共有多少个视频文件
    # 参数：用户选择整理的文件夹路径root_choose，视频类型后缀集合tuple_video_type
    # 返回：无
    # 辅助：os.walk
    def count_num_videos(self):
        num_videos = 0
        len_choose = len(self._dir_choose)
        for root, dirs, files in os.walk(self._dir_choose):
            if '归类完成' not in root[len_choose:]:
                for file_raw in files:
                    file_temp = file_raw.upper()
                    if file_temp.endswith(self._tuple_video_types) and not file_temp.startswith('.'):
                        num_videos += 1
        return num_videos

    def init_jav_file_episodes(self, list_jav_files: list):
        """

        更新list_jav_files中每一个jav有多少cd（用于“多cd命名”“判定处理完最后一个cd后允许重命名文件夹等操作”。）

        Args:
            list_jav_files: (当前所处文件夹的子一级包含的)jav视频文件们

        Returns:
            void; 更新list_jav_files

        """
        for jav_file in list_jav_files:
            jav_file.Sum_all_episodes = self._dict_car_episode[jav_file.Car]

    # 功能: 判定影片所在文件夹是否是独立文件夹，独立文件夹是指该文件夹仅用来存放该影片，不包含“.actors”"extrafanrt”外的其他文件夹
    # 辅助: 无
    def judge_separate_folder(self, len_list_jav_files: int, list_sub_dirs: list):
        """
        Args:
            len_list_jav_files: 当前所处文件夹包含的车牌数量
            list_sub_dirs:（当前所处文件夹包含的）子文件夹们
        Returns:
            void; 设定JavFile.Bool_in_separate_folder=bool
        """
        # 当前文件夹下，车牌不止一个；还有其他非jav视频；有其他文件夹，除了演员头像文件夹“.actors”和额外剧照文件夹“extrafanart”；
        if len(self._dict_car_episode) > 1 or self._sum_videos_in_current_dir > len_list_jav_files:
            JavFile.Bool_in_separate_folder = False
            return
        for folder in list_sub_dirs:
            if folder != '.actors' and folder != 'extrafanart':
                JavFile.Bool_in_separate_folder = False
                return
        JavFile.Bool_in_separate_folder = True  # 这一层文件夹是这部jav的独立文件夹
        return

    def sum_all_videos(self):
        return self._sum_videos_in_choose_dir
