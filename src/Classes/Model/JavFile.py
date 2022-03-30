# -*- coding:utf-8 -*-
import os
from os import sep

# 每一部jav的“结构体”
from Functions.Metadata.Car import extract_suf, extract_pref


class JavFile(object):
    """
    一部影片在用户本地的文件结构

    包含文件名、文件路径、是否有中文字幕等属性
    """

    def __init__(self, car: str, file_raw: str, dir_current: str, episode: int, subtitle: str,
                 no_current: int):
        self.Car = car
        """1 车牌"""

        self.Name = file_raw
        """2 完整文件名\n\n例如ABC-123-cd2.mp4，会在重命名过程中发生变化"""

        self.Ext = os.path.splitext(file_raw)[1].lower()
        """3 视频文件扩展名\n\n例如.mp4、.wmv"""

        self.Dir = dir_current
        """4 视频所在文件夹的路径\n\n例如D:/MyData/测试/DV-1594【朝日奈あかり】，会在重命名过程中发生变化"""

        self.Episode = episode
        """5 第几集\n\n一部时间较长的影片可能被分为多部份，例如cd1 cd2 cd3的1 2 3"""

        self.Sum_all_episodes = 0
        """6 当前车牌总共多少部分\n\n例如abc-123分为abc-123-cd1.MP4和abc-123-cd2.mp4共两部分"""

        self.Subtitle = subtitle
        """7一部影片的字幕的文件名\n\n影片和字幕需在同一文件夹内，例如ABC-123.srt，会在重命名过程中发生变化"""

        self.Ext_subtitle = os.path.splitext(subtitle)[1].lower()
        """8 字幕文件扩展名\n\n例如.srt"""

        self.No = no_current
        """9 编号\n\n当前处理的视频在（所选文件夹）所有视频中的编号，用于显示整理进度"""

        self.Bool_subtitle = False
        """10 是否拥有字幕"""

        self.Bool_divulge = False
        """11 是否无码流出"""

    Bool_in_separate_folder = False
    """是否拥有独立文件夹\n\n同一级文件夹中的影片该值相同，整理过程中据此可以选择为它创建独立文件夹"""

    @property
    def Pref(self):
        """车牌前缀，车尾\n\n例如IPZ"""
        return extract_pref(self.Car)

    @property
    def Suf(self):
        """3 车牌后缀\n\n纯数字，例如ABC-123z的123，26ID-020的20"""
        return extract_suf(self.Car)

    @property
    def Car_search(self):
        """2 搜索用的车牌，给bus和arzon搜索"""
        return self.Car.replace("-", "")

    @property
    def Cd(self):
        """当前视频文件是cd几\n\n例如一部影片有两集，多cd，第一集cd1.第二集cd2；如果只有一集，为空"""
        return f'-cd{self.Episode}' if self.Sum_all_episodes > 1 else ''

    @property
    def Folder(self):
        """所在文件夹的名称"""
        return os.path.basename(self.Dir)

    @property
    def Path(self):
        """视频文件完整路径"""
        return f'{self.Dir}{sep}{self.Name}'

    @property
    def Name_no_ext(self):
        """视频文件名，但不带文件扩展名"""
        return os.path.splitext(self.Name)[0]

    @property
    def Path_subtitle(self):
        """字幕文件完整路径"""
        return f'{self.Dir}{sep}{self.Subtitle}'
