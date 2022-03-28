# -*- coding:utf-8 -*-
import os
from os import sep
from typing import List

from Classes.Model.JavFile import JavFile
from Classes.Static.Config import Ini
from Classes.Static.Errors import CustomClassifyTargetDirError
from Functions.Metadata.Car import find_car_fc2, find_car_youma, get_suren_cars


class FileExplorer(object):
    """
    磁盘文件检索器

    在磁盘中搜索发现jav视频文件，构建javFile对象
    """

    def __init__(self, ini: Ini):

        # region 本次程序启动通用
        self._pattern = ini.pattern
        """当前主程序的整理模式(youma, wuma, fc2)"""

        self._need_classify = ini.need_classify
        """需要归类"""

        self._need_classify_folder = ini.need_classify_folder
        """归类是针对【文件夹】而不是【文件】"""

        self._need_rename_folder = ini.need_rename_folder
        """需要重命名文件夹或创建新的独立文件夹"""

        self._dir_custom_classify_target = ini.dir_custom_classify_root
        """用户自定义的归类的根目录\n\n用于判定出真实的归类根目录"""

        self._tuple_video_types = ini.tuple_video_types
        """视频文件类型"""

        self._list_surplus_words = ini.list_surplus_words
        """视频文件名中多余的、干扰车牌的文字"""
        self._list_suren_cars = get_suren_cars()
        """素人车牌前缀\n\n如果当前处理模式是youma、wuma，让程序能跳过这些素人车牌"""

        self._need_rename_folder = self._judge_need_rename_folder()
        """是否需要重命名文件夹"""
        # endregion

        # region 每次选择的文件夹通用
        self._dir_choose = ''
        """用户此次选择的文件夹"""

        self._dir_classify_target = ''
        """真实的归类的目标根文件夹\n\n每次新选文件夹都会变化"""

        self._no_current = 0
        """当前视频（包括非jav）的编号\n\n用于显示进度、获取（所选文件夹内）视频数量"""

        self._sum_videos_in_choose_dir = 0
        """（所选文件夹内）需处理视频总数"""
        # endregion

        # region 主程序for循环的某一级文件夹通用
        self._dir_current = ''
        """主程序for循环所处的某一层级文件夹路径"""

        self._dict_subtitle_file = {}
        """存储（某一层级文件夹内）字幕文件和车牌对应关系\n\n例如{ 'c:/a/abc_123.srt': 'abc-123' }，用于构建视频文件的字幕体系"""

        self._list_jav_files = []
        """存储（某一层级文件夹内）的jav_files"""

        self._dict_car_episode = {}
        """存储（某一层级文件夹内）每一车牌的集数\n\n例如{'abc-123': 1, def-789': 2} 是指 abc-123只有1集，def-789有2集，主要用于理清同一车牌的兄弟姐妹"""

        self._sum_videos_in_current_dir = 0
        """（某一层级文件夹内）包含的视频总数\n\n用于判断这一级文件夹是否是独立文件夹"""
        # endregion

    def _judge_need_rename_folder(self):
        """
        判断到底要不要 重命名文件夹或者创建新的文件夹

        用户可能选择了不修改文件夹，但选择了归类，那么仍需要修改文件夹

        Returns:
            bool
        """
        if self._need_classify and self._need_classify_folder:
            # 如果需要归类，并且是针对文件夹，那么必须重命名文件夹或者创建新的文件夹
            return True
        elif self._need_rename_folder:
            # 用户本来就在ini中写了要重命名文件夹
            return True
        return False

    # region 重置

    def rest_and_check_choose(self, dir_choose: str):
        """
        用户每次选择文件夹后重置

        Args:
            dir_choose: 用户选择的文件夹路径
        """
        self._dir_choose = dir_choose
        self._no_current = 0
        self._check_classify_target_directory()
        self._sum_videos_in_choose_dir = self._count_videos_amount()

    def _check_classify_target_directory(self):
        """检查用户设置的“归类根目录”的合法性"""

        # 用户需要归类，检查他设置的归类根目录是否合法
        if self._need_classify:
            dir_target = self._dir_custom_classify_target.rstrip(sep)
            if dir_target not in ['所选文件夹', self._dir_choose]:
                # 用户自定义了一个路径
                if dir_target[:2] != self._dir_choose[:2]:
                    raise CustomClassifyTargetDirError(
                        f'归类的根目录: 【{dir_target}】与所选文件夹不在同一磁盘，无法归类！请修正！')
                if not os.path.exists(dir_target):
                    raise CustomClassifyTargetDirError(f'归类的根目录: 【{dir_target}】不存在！无法归类！请修正！')
                self._dir_classify_target = dir_target
            else:
                # 用户希望归类在“所选文件夹”
                self._dir_classify_target = f'{self._dir_choose}{sep}归类完成'
        else:
            # 用户不需要归类，不用关心
            self._dir_classify_target = ''

    def _count_videos_amount(self):
        """
        所选文件夹总共有多少个视频文件

        Returns:
            总数量
        """
        num_videos = 0
        len_choose = len(self._dir_choose)
        for root, dirs, files in os.walk(self._dir_choose):
            if '归类完成' not in root[len_choose:]:
                # 排除”归类完成“文件夹
                for file_raw in files:
                    file_temp = file_raw.upper()
                    if file_temp.endswith(self._tuple_video_types) and not file_temp.startswith('.'):
                        num_videos += 1
        return num_videos

    def rest_current_dir(self, dir_current: str):
        """
        主程序for循环，每进入新一层级文件夹的重置

        Args:
            dir_current: 当前所处文件夹
        """
        self._dir_current = dir_current
        self._dict_subtitle_file = {}
        self._list_jav_files = []
        self._dict_car_episode = {}
        self._sum_videos_in_current_dir = 0

    # endregion

    def init_dict_subtitle_file(self, list_sub_files: list):
        """
        收集文件中的字幕文件，存储在self._dict_subtitle_file

        Args:
            list_sub_files: (当前一层级文件夹的)子文件们
        """
        for file_raw in list_sub_files:
            file = file_raw.upper()
            if file.endswith(('.SRT', '.VTT', '.ASS', '.SSA', '.SUB', '.SMI',)):
                if self._pattern != 'Fc2':
                    # 有码无码不处理FC2
                    if 'FC2' in file:
                        continue
                    # 去除用户设置的、干扰车牌的文字
                    for word in self._list_surplus_words:
                        file = file.replace(word, '')
                    subtitle_car = find_car_youma(file, self._list_suren_cars)
                    """字幕文件名中的车牌"""
                elif 'FC2' in file:
                    subtitle_car = find_car_fc2(file)
                else:
                    continue  # 【跳出2】
                # 找到车牌
                if subtitle_car:
                    # 将 字幕文件 和 车牌 对应到字典中
                    self._dict_subtitle_file[file_raw] = subtitle_car

    def find_jav_files(self, list_sub_files: list):
        """
        发现jav视频文件

        找出list_sub_files中的jav视频文件，实例每一个jav视频文件为javfile对象，存储在self._list_jav_files

        Args:
            list_sub_files: (当前所处一级文件夹的)子文件
        """
        for file_raw in list_sub_files:
            file = file_raw.upper()
            if file.endswith(self._tuple_video_types) and not file.startswith('.'):
                self._no_current += 1
                self._sum_videos_in_current_dir += 1
                if 'FC2' in file:
                    continue
                for word in self._list_surplus_words:
                    file = file.replace(word, '')
                # 查找车牌
                if car := find_car_youma(file, self._list_suren_cars):
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
                    # 将该jav的各种属性打包好，包括原文件名带扩展名、所在文件夹路径、第几集、所属字幕文件名
                    jav_file = JavFile(car, file_raw, self._dir_current, self._dict_car_episode[car],
                                       subtitle_file, self._no_current)
                    self._list_jav_files.append(jav_file)
                else:
                    print(f'>>无法处理: {self._dir_current[len(self._dir_choose):]}{sep}{file_raw}')

    def len_list_jav_files(self):
        """当前一层级文件夹内jav视频文件的数量"""
        return len(self._list_jav_files)

    def init_jav_file_episodes(self):
        """
        更新self._list_jav_files中每一个jav有多少cd

        用于“多cd命名”“判定处理完最后一个cd后允许重命名文件夹”等操作。
        """
        for jav_file in self._list_jav_files:
            jav_file.Sum_all_episodes = self._dict_car_episode[jav_file.Car]

    def judge_separate_folder(self, list_sub_dirs: List[str]):
        """
        判定影片所在文件夹是否是独立文件夹

        独立文件夹是指该文件夹仅用来存放该影片，不包含“.actors”"extrafanrt”外的其他文件夹

        Args:
            list_sub_dirs:（当前所处文件夹包含的）子文件夹们
        """
        # 当前文件夹下，车牌不止一个；还有其他非jav视频；
        if len(self._dict_car_episode) > 1 or self._sum_videos_in_current_dir > self.len_list_jav_files():
            JavFile.Bool_in_separate_folder = False
            return
        # 有其他文件夹，除了演员头像文件夹“.actors”和额外剧照文件夹“extrafanart”；
        for folder in list_sub_dirs:
            if folder not in ['.actors', 'extrafanart']:
                JavFile.Bool_in_separate_folder = False
                return
        JavFile.Bool_in_separate_folder = True  # 这一层文件夹是这部jav的独立文件夹
        return

    # region 成员只读

    def dir_classify_target(self):
        """返回真实的归类根目录"""
        return self._dir_classify_target

    def list_jav_files(self):
        """只读jav_files"""
        return self._list_jav_files

    def sum_all_videos(self):
        """所选文件夹中包含的需处理的视频总数量"""
        return self._sum_videos_in_choose_dir

    # endregion
