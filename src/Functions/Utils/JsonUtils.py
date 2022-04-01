# -*- coding:utf-8 -*-
import os
from json import load, dump

from Datetime import time_now
from User import choose_directory


def read_json_to_dict(path):
    """
    提供json路径读取为dict

    Args:
        path: json路径
    """
    with open(path, encoding='utf-8') as f:
        dict_json = load(f)
    return dict_json


def show_json_by_path(path):
    """
    展示json的内容

    Args:
        path: json路径
    """
    dict_json = read_json_to_dict(path)
    for i in dict_json:
        print(i, ':', dict_json[i])


def show_jsons_one_element_by_dir_choose(dir_choose, key):
    """
    展示所有json中的某一项，某一项由手动输入

    Args:
        dir_choose: 选择的路径
        key: 键
    """
    for root, dirs, files in os.walk(dir_choose):
        for file in files:
            if file.endswith(('.json',)):
                path = f'{root}\\{file}'
                dict_json = read_json_to_dict(path)
                try:
                    print(dict_json['Car'], dict_json[key])
                except KeyError:
                    print('无')


def show_json_one_element_by_path(path, key):
    """
    展示所有json中的某一项，某一项由手动输入

    Args:
        dir_choose: json路径
        key: 键
    """
    dict_json = read_json_to_dict(path)
    try:
        print(dict_json['Car'], dict_json[key])
    except KeyError:
        print('无')


def judge_json_contain_one_genre_by_path(path, genre):
    """检查某一个json是否包含指定的genre"""
    dict_json = read_json_to_dict(path)
    print('正在检查: ', path)
    if genre in dict_json['Genres']:
        print(path, dict_json['Genres'])
        return True
    else:
        return False


def write_json(path, dict_json):
    # 重新写
    with open(path, 'w', encoding='utf-8') as f:
        dump(dict_json, f, indent=4)


def replace_key_name(path, key_old, key_new):
    dict_json = read_json_to_dict(path)
    if key_old in dict_json:
        # print('旧: ', dict_json)
        dict_json[key_new] = dict_json[key_old]
        del dict_json[key_old]
        # print('新: ', dict_json)
        write_json(path, dict_json)


# region 定制

def show_jsons_special_element_by_dir_choose(dir_choose):
    """
    【定制】修正library的dmm图片到CoverDmm

    Args:
        dir_choose:

    Returns:

    """
    for root, dirs, files in os.walk(dir_choose):
        for file in files:
            if file.endswith(('.json',)):
                path = f'{root}\\{file}'
                print(path)
                dict_json = read_json_to_dict(path)
                if not dict_json['CoverLibrary']:
                    dict_json['CoverDmm'] = ''
                elif not dict_json['CoverLibrary'].startswith('http'):
                    print('特殊:', dict_json['CoverLibrary'])
                    dict_json['CoverDmm'] = ''
                elif 'dmm.co.jp' in dict_json['CoverLibrary']:
                    dict_json['CoverDmm'] = dict_json['CoverLibrary']
                    dict_json['CoverLibrary'] = ''
                write_json(path, dict_json)


# 检查某一路径的json是否没有“剧情”
def check_lost_plot(path):
    if os.path.exists(path):
        dict_json = read_json_to_dict(path)
        # print('当前plot如下')
        # print('plot:', dict_json['plot'])
        return dict_json['plot'] == '未知简介'
    else:
        print('  >没有json：', path)
        return False


# 检查某一路径的json是否没有 系列
def check_lost_series(path):
    if os.path.exists(path):
        dict_json = read_json_to_dict(path)
        return dict_json['series'] == '未知系列'
    else:
        print('  >没有json：', path)
        return False


def upate_coverDb(dir_choose):
    for root, dirs, files in os.walk(dir_choose):
        for file in files:
            if file.endswith(('.json',)):
                path = f'{root}\\{file}'
                dict_json = read_json_to_dict(path)
                item = dict_json['JavDb']
                if item:
                    print('有了', item)
                dict_json['CoverDb'] = f'https://jdbimgs.com/covers/{item[:2].lower()}/{item}.jpg'
                print(dict_json['CoverDb'])
                write_json(path, dict_json)


def exchange_init_modify(path: str):
    dict_json = read_json_to_dict(path)
    if dict_json['Init'] > dict_json['Modify']:
        dict_json['Init'], dict_json['Modify'] = dict_json['Modify'], dict_json['Init']
        print(path)
    else:
        print(dict_json['Init'], dict_json['Modify'])
    write_json(path, dict_json)


# endregion


if __name__ == '__main__':
    print('请选择要整理的文件夹：')
    dir_choose = choose_directory()
    # show_jsons_special_element_by_dir_choose(root_choose
    for root, dirs, files in os.walk(dir_choose):
        for file in files:
            if file.endswith(('.json',)):
                path = f'{root}\\{file}'
                exchange_init_modify(path)
