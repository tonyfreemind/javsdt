from os.path import splitext, basename
from os import sep


# 每一部jav的“结构体”
class JavFile(object):
    def __init__(self, car, car_id, file_raw, dir_current, episode, subtitle, no_current):
        self.Car = car                                     # 车牌
        self.Car_id = car_id                               # 去bus和arzon搜索的车牌，不同在于Car_id是26ID-xxx，Car是ID-26xxx
        self.Pref = car.split('-')[0]                      # 车牌前缀
        self.Name = file_raw                               # 完整文件名 ABC-123-cd2.mp4；会在重命名过程中发生变化
        self.Ext = splitext(file_raw)[1].lower()           # 视频文件扩展名 .mp4
        self.Dir = dir_current                             # 视频所在文件夹的路径；会在重命名过程中发生变化
        self.Episode = episode                             # 第几集 cd1 cd2 cd3
        self.Sum_all_episodes = 0                          # 当前车牌总共多少集，用户的
        self.Subtitle = subtitle                           # 字幕文件名  ABC-123.srt；会在重命名过程中发生变化
        self.Ext_subtitle = splitext(subtitle)[1].lower()  # 字幕扩展名  .srt
        self.No = no_current                              # 当前处理的视频在所有视频中的编号，整理进度
        self.Bool_subtitle = False                           # 拥有字幕
        self.Bool_divulge = False                            # 是无码流出

    # 类属性，类似于面向对象语言中的静态成员
    Bool_in_separate_folder = False         # 是否拥有独立文件夹，同一级文件夹中的jav具有相同的值

    # 多cd，如果有两集，第一集cd1.第二集cd2；如果只有一集，为空
    @property
    def Cd(self):
        return f'-cd{self.Episode}' if self.Sum_all_episodes > 1 else ''

    # 所在文件夹名称
    @property
    def Folder(self):
        return basename(self.Dir)

    # 这下面列为属性而不是字段，因为name、dir、subtitle会发生变化
    # 视频文件完整路径
    @property
    def Path(self):
        return f'{self.Dir}{sep}{self.Name}'

    # 视频文件名，但不带文件扩展名
    @property
    def Name_no_ext(self):
        return splitext(self.Name)[0]

    # 字幕文件完整路径
    @property
    def Path_subtitle(self):
        return f'{self.Dir}{sep}{self.Subtitle}'
