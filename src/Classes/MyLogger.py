from time import strftime, localtime, time

from Const import Const


class Logger(object):
    """
    日志工具

    用于记录失败/警告次数、失败/警告信息，保存至本地txt
    """

    def __init__(self):
        self._no_fail = 0
        """数量: 错误\n\n可能导致或已经发生的致命错误，比如整理未完成，同车牌有不同视频"""

        self._no_warn = 0
        """数量: 警告\n\n对整理结果不致命的问题，比如找不到简介"""

        self._dir_choose = ''
        """所选文件夹的路径"""

        self._path_relative = ''
        """路径: 当前jav_file相对于dir_choose的路径\n\n用于报错"""

    def rest(self):
        """每次选择文件夹后重置"""
        self._no_fail = 0
        self._no_warn = 0

    def record_fail(self, fail_msg: str, extra_msg: str = None):
        """
        显示错误信息并写入日志

        Args:
            fail_msg: 失败信息
            extra_msg: 额外的错误信息，一般放出错视频的路径
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

    def record_start(self, dir_choose):
        """
        记录此次整理的文件夹、整理的时间

        Args:
            dir_choose: 选择的文件夹
        """
        self._dir_choose = dir_choose
        msg = f'已选择文件夹: {dir_choose}  {strftime("%Y-%m-%d %H:%M:%S", localtime(time()))}\n'
        write_txt(Const.TXT_FAIL, msg)
        write_txt(Const.TXT_WARN, msg)
        write_txt(Const.TXT_RENAME, msg)

    def print_end(self):
        """（当前文件夹处理结束）显示整理情况"""
        if self._no_fail > 0:
            print('失败', self._no_fail, '个!  ', self._dir_choose, '\n')
            line = -1
            with open(Const.TXT_FAIL, 'r', encoding="utf-8") as f:
                content = list(f)
            while 1:
                if content[line].startswith('已'):
                    break
                line -= 1
            for i in range(line + 1, 0):
                print(content[i], end='')
            print(f'\n“{Const.TXT_FAIL}”已记录错误\n')
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


def record_video_old(name_new: str, name_old: str):
    """
    记录新旧文件名

    Args:
        name_new: 新文件名
        name_old: 旧文件名
    """
    msg = f'<<<< {name_old}\n>>>> {name_new}\n'
    write_txt(Const.TXT_RENAME, msg)


def write_txt(path_txt: str, msg: str):
    """
    以append形式向指定txt写入内容

    Args:
        path_txt: 文本路径
        msg: 写入内容，注意加换行符
    """
    txt = open(path_txt, 'a', encoding="utf-8")
    txt.write(msg)
    txt.close()
