# -*- coding:utf-8 -*-
from Classes.Static.Const import Const
from Datetime import time_now


class MyLogger(object):
    """
    日志工具

    用于输出/记录失败/警告次数、失败/警告信息，保存至本地txt
    """

    def __init__(self):
        self._no_fail = 0
        """数量: 错误\n\n可能导致或已经发生的致命错误，比如整理未完成，db或library同车牌有不同视频"""

        self._no_warn = 0
        """数量: 警告\n\n对整理结果不致命的问题，比如找不到简介，bus或arzon同车牌有不同视频"""

        self._dir_choose = ''
        """所选文件夹的路径"""

        self._path_relative = ''
        """路径: 当前jav_file相对于dir_choose的路径\n\n用于报错"""

    def rest_and_record_choose(self, dir_choose: str):
        """每次选择文件夹后重置"""
        self._no_fail = 0
        self._no_warn = 0
        self._record_start(dir_choose)

    def record_fail(self, fail_msg: str, extra_msg: str = None):
        """
        显示错误信息并写入日志

        Args:
            fail_msg: 失败信息
            extra_msg: 额外的错误信息，默认是 出错视频的路径
        """
        self._no_fail += 1
        if not extra_msg:
            extra_msg = self._path_relative
        msg = f'    >第{self._no_fail}个失败！{fail_msg}{extra_msg}\n'
        write_txt(Const.TXT_FAIL, msg)
        print(msg, end='')

    def record_warn(self, warn_msg: str, extra_msg: str = None):
        """
        显示警告信息并写入日志

        Args:
            warn_msg: 警告信息
            extra_msg: 额外的警告信息，一般放出错视频的路径
        """
        self._no_warn += 1
        if not extra_msg:
            extra_msg = self._path_relative
        msg = f'    >第{self._no_warn}个警告！{warn_msg}{extra_msg}\n'
        write_txt(Const.TXT_WARN, msg)
        print(msg, end='')

    def _record_start(self, dir_choose):
        """
        记录此次整理的文件夹、整理的时间

        Args:
            dir_choose: 选择的文件夹
        """
        self._dir_choose = dir_choose
        msg = f'已选择文件夹: {dir_choose}  {time_now()}\n'
        write_txt(Const.TXT_FAIL, msg)
        write_txt(Const.TXT_WARN, msg)
        write_txt(Const.TXT_RENAME, msg)

    def print_end(self):
        """（当前文件夹处理结束）显示整理情况"""
        print('\n当前文件夹完成，', end='')
        if self._no_fail > 0:
            print('失败', self._no_fail, '个!  ', self._dir_choose, '\n')
            with open(Const.TXT_FAIL, 'r', encoding="utf-8") as f:
                content = list(f)
            line = -1
            while 1:
                if content[line].startswith('已'):
                    break
                line -= 1
            for i in range(line + 1, 0):
                print(content[i], end='')
        else:
            print(' “0”失败！  ', self._dir_choose, '\n')
        if self._no_warn > 0:
            print(f'“{Const.TXT_WARN}”还记录了 {self._no_warn} 个警告信息！\n')

    def update_relative_path(self, path_new: str):
        """
        更新”视频文件相对于所选文件夹的路径“

        Args:
            path_new: 新路径
        """
        self._path_relative = path_new


def record_video_old(name_old: str, name_new: str):
    """
    记录新旧文件名

    Args:
        name_old: 旧文件名
        name_new: 新文件名
    """
    msg = f'<<<< {name_old}\n' \
          f'>>>> {name_new}\n'
    write_txt(Const.TXT_RENAME, msg)


def write_txt(path_txt: str, msg: str):
    """
    以append形式向指定txt写入内容

    Args:
        path_txt: 文本路径
        msg: 写入内容，注意加换行符
    """
    with open(path_txt, 'a', encoding="utf-8") as txt:
        txt.write(msg)
