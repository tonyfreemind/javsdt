# -*- coding:utf-8 -*-
import sys
import os
import time
from os import sep
from tkinter import filedialog, Tk, TclError


def choose_directory():
    """
    请用户选择要整理的文件夹

    如果当前系统不支持对话框，则让用户输入

    Returns:
        文件夹完整路径
    """
    print('请选择要整理的文件夹: ', end='')
    for _ in range(2):
        try:
            tk = Tk()
            tk.withdraw()
            path_work = filedialog.askdirectory()
            if path_work == '':
                print('你没有选择目录! 请重新选: ')
                time.sleep(2)
                continue
            else:
                # askdirectory 获得是 正斜杠 路径C:/，所以下面要把 / 换成 反斜杠\
                print(path_work)
                return path_work.replace('/', sep)
        except TclError:  # 来自@BlueSkyBot
            try:
                path_work = input("请输入你需要整理的文件夹路径: ")
            except KeyboardInterrupt:
                sys.exit('输入终止，马上退出！')
            if not os.path.exists(path_work) or not os.path.isdir(path_work):
                print('\"{0}\" 不存在当前目录或者输入错误，请重新输入！'.format(path_work))
                time.sleep(2)
            else:
                print(path_work)
                return path_work
    input('你可能不需要我了，请关闭我吧！')
