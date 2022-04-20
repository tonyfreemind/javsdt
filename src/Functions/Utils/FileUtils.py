# -*- coding:utf-8 -*-
import os.path
from os import name as system_name


def replace_xml_invalid_char(src):
    """
    替换xml中的不允许的特殊字符，替换制表符，去除首尾空格

    xml需要转义【&<>"'】，但双引号和单引号似乎被什么操作变得不影响。不处理【空格】元素。

    Args:
        src: 原字符串，例如文件名、简介、标题、导演姓名等

    Returns:
        替换后字符串
    """
    if src == ' ':
        return src
    else:
        return src.replace('&', '&amp;') \
            .replace('<', '&lt;') \
            .replace('>', '&gt;') \
            .replace('\n', '') \
            .replace('\t', '') \
            .replace('\r', '') \
            .strip()


def replace_os_invalid_char(src: str):
    """
    替换windows路径不允许的特殊字符 \/:*?"<>|

    如果src是斜杠，不作处理，它是正常的路径分隔符

    Args:
        src: 原字符串，文件名、简介、标题、导演姓名等

    Returns:
        替换后字符串
    """
    if system_name != 'nt':
        # 不是windows系统
        return src

    if src == '\\':
        return src

    dict_replace = {
        '\\': '#',
        '/': '#',
        ':': '：',
        '*': '#',
        '?': '？',
        '"': '#',
        '<': '《',
        '>': '》',
        '|': '#'
    }
    return src.translate(str.maketrans(dict_replace))


def replace_line_break(src: str):
    """
    去除html中一段文字中的<br>换行
    
    Args:
        src: 

    Returns:

    """
    return src.replace('\n', '') \
        .replace('\t', '') \
        .replace('\r', '') \
        .strip()


def dir_father(path: str):
    """所处文件夹完整路径"""
    name = os.path.dirname(path)
    return name[:-1] if name.endswith('\\') else name
