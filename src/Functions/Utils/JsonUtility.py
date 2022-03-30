# -*- coding:utf-8 -*-
import os
from json import load, dump

from User import choose_directory


def read_json_to_dict(path):
    with open(path, encoding='utf-8') as f:
        dict_json = load(f)
    return dict_json


# 显示某一路径json的内容
def show_json_by_path(path):
    dict_json = read_json_to_dict(path)
    for i in dict_json:
        print(i, ':', dict_json[i])


# 展示所有json中的某一项，某一项由手动输入
def show_jsons_one_element_by_dir_choose(dir_choose, key):
    for root, dirs, files in os.walk(dir_choose):
        for file in files:
            if file.endswith(('.json',)):
                path = f'{root}\\{file}'
                dict_json = read_json_to_dict(path)
                print(dict_json['Car'], dict_json[key])


# 展示所有json中的某一项，某一项由手动输入
def show_jsons_special_element_by_dir_choose(dir_choose):
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


# 展示所有json中的某一项，某一项由手动输入
def show_json_one_element_by_path(path, key):
    dict_json = read_json_to_dict(path)
    try:
        print(dict_json[key])
    except KeyError:
        print('无')


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


if __name__ == '__main__':
    print('请选择要整理的文件夹：')
    root_choose = choose_directory()
    # for root, dirs, files in os.walk(root_choose):
    #     for file in files:
    #         if file.endswith('.json'):
    #             replace_key_name(f'{root}\\{file}', 'Javdb', 'JavDb')
    #             replace_key_name(f'{root}\\{file}', 'Javlibrary', 'JavLibrary')
    #             replace_key_name(f'{root}\\{file}', 'Javbus', 'JavBus')

    show_jsons_special_element_by_dir_choose(root_choose)
