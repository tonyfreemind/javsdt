import os
from os import sep
from xml.etree.ElementTree import parse, ParseError

from Classes.Config import Ini
from Classes.Model.JavFile import JavFile


class FileAnalyzer(object):
    """jav视频文件性质鉴定\n\n判定该影片是否有字幕、是否无码流出"""

    def __init__(self, ini: Ini):
        self._list_subtitle_words_in_filename = ini.list_subtitle_symbol_words
        self._list_divulge_words_in_filename = ini.list_divulge_symbol_words

    def _judge_exist_subtitle(self, dir_current: str, name_no_ext: str):
        """
        判定当前jav是否有“中文字幕”

        根据【原文件名】和【已存在的、之前整理的nfo】，

        Args:
            dir_current: 当前jav所处文件夹路径
            name_no_ext: 视频文件名，不带文件类型后缀

        Returns:
            bool
        """
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

    def _judge_exist_divulge(self, dir_current: str, name_no_ext: str):
        """
        判断当前jav是否有“无码流出”

        根据【原文件名】和【已存在的、之前整理的nfo】，

        Args:
            dir_current: 当前jav所处文件夹路径
            name_no_ext: jav文件名不带文件类型后缀

        Returns:
            bool
        """
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

    def judge_subtitle_and_divulge(self, jav_file: JavFile):
        """
        判断当前jav_file是否有“中文字幕”，是否有“无码流出”

        Args:
            jav_file: 处理的jav视频文件对象

        Returns:
            void
        """
        # 判断是否有中字的特征，条件有三满足其一即可: 1有外挂字幕 2文件名中含有“-C”之类的字眼 3旧的nfo中已经记录了它的中字特征
        if jav_file.Subtitle:
            jav_file.Bool_subtitle = True  # 判定成功
        else:
            jav_file.Bool_subtitle = self._judge_exist_subtitle(jav_file.Dir, jav_file.Name_no_ext)
        # 判断是否是无码流出的作品，同理
        jav_file.Bool_divulge = self._judge_exist_divulge(jav_file.Dir, jav_file.Name_no_ext)
