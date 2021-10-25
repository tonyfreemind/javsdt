import os
from os import sep  # 系统路径分隔符
from xml.etree.ElementTree import parse, ParseError  # 解析xml格式
import MySettings


class VideoFileAnalysis(object):
    def __init__(self, settings:MySettings.Settings):
        self._list_subtitle_words_in_filename = settings.list_subtitle_symbol_words
        self._list_divulge_words_in_filename = settings.list_divulge_symbol_words

    # 功能: 根据【原文件名】和《已存在的、之前整理的nfo》，判断当前jav是否有“中文字幕”
    # 参数: ①当前jav所处文件夹路径dir_current ②jav文件名不带文件类型后缀name_no_ext，
    # 返回: True
    # 辅助: os.path.exists，xml.etree.ElementTree.parse，xml.etree.ElementTree.ParseError
    def judge_exist_subtitle(self, dir_current, name_no_ext):
        # 去除 '-CD' 和 '-CARIB'对 '-C'判断中字的影响
        name_no_ext = name_no_ext.upper().replace('-CD', '').replace('-CARIB', '')
        # 如果原文件名包含“-c、-C、中字”这些字符
        for i in self._list_subtitle_words_in_filename:
            if i in name_no_ext:
                return True
        # 先前整理过的nfo中有 ‘中文字幕’这个Genre
        path_old_nfo = f'{dir_current}{sep}{name_no_ext}.nfo'
        if os.path.exists(path_old_nfo):
            try:
                tree = parse(path_old_nfo)
            except ParseError:  # nfo可能损坏
                return False
            for child in tree.getroot():
                if child.text == '中文字幕':
                    return True
        return False

    # 功能: 根据【原文件名】和《已存在的、之前整理的nfo》，判断当前jav是否有“无码流出”
    # 参数: ①当前jav所处文件夹路径dir_current ②jav文件名不带文件类型后缀name_no_ext
    # 返回: True
    # 辅助: os.path.exists，xml.etree.ElementTree.parse，xml.etree.ElementTree.ParseError
    def judge_exist_divulge(self, dir_current, name_no_ext):
        # 如果原文件名包含“-c、-C、中字”这些字符
        for i in self._list_divulge_words_in_filename:
            if i in name_no_ext:
                return True
        # 先前整理过的nfo中有 ‘中文字幕’这个Genre
        path_old_nfo = f'{dir_current}{sep}{name_no_ext}.nfo'
        if os.path.exists(path_old_nfo):
            try:
                tree = parse(path_old_nfo)
            except ParseError:  # nfo可能损坏
                return False
            for child in tree.getroot():
                if child.text == '无码流出':
                    return True
        return False

    # 功能: 判断当前jav_file是否有“中文字幕”，是否有“无码流出”
    # 参数: jav_file 处理的jav视频文件对象
    # 返回: 无；更新jav_file
    # 辅助: 无
    def judge_subtitle_and_divulge(self, jav_file):
        # 判断是否有中字的特征，条件有三满足其一即可: 1有外挂字幕 2文件名中含有“-C”之类的字眼 3旧的nfo中已经记录了它的中字特征
        if jav_file.Subtitle:
            jav_file.Bool_subtitle = True  # 判定成功
        else:
            jav_file.Bool_subtitle = self.judge_exist_subtitle(jav_file.Dir, jav_file.Name_no_ext)
        # 判断是否是无码流出的作品，同理
        jav_file.Bool_divulge = self.judge_exist_divulge(jav_file.Dir, jav_file.Name_no_ext)