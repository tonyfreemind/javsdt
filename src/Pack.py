import os
import shutil
from os import sep
import sys
from enum import IntEnum

from Functions.Utils.FileUtils import dir_father


class PyEnum(IntEnum):
    CreateIni = 1
    Youma = 2


print('\n请选择打包程序:'
      '    0、退出'
      '    1、全体打包\n')


def move(dir_dist: str):
    for file in os.listdir(dir_dist):
        dir_sdt = f'{dir_father(dir_dist)}{sep}javsdt'
        if not os.path.exists(dir_sdt):
            os.makedirs(dir_sdt)
        path_dest = f'{dir_sdt}{sep}{file}'
        if not os.path.exists(path_dest):
            os.rename(f'{dir_dist}{sep}{file}', path_dest)


dir_sdt = 'dist/javsdt'
while 1:
    pattern = input('请输入: ')

    if pattern == '0':
        sys.exit()

    if pattern == '1':
        os.system('pyinstaller CreateIni.py -i StaticFiles/ini.ico')
        print('>>pyinstaller完成')
        move(f'dist{sep}CreateIni')
        print('>>移动完成')
        shutil.rmtree(f'dist{sep}CreateIni')
        os.remove('CreateIni.spec')
        print('>>删除完成\n')

        os.system('pyinstaller Youma.py -i StaticFiles/javsdt.ico')
        print('>>pyinstaller完成')
        move(f'dist{sep}Youma')
        print('>>移动完成')
        shutil.rmtree(f'dist{sep}Youma')
        os.remove('Youma.spec')
        print('>>删除完成\n')

        os.rename(f'{dir_sdt}{sep}CreateIni.exe', f'{dir_sdt}{sep}【ini】重新创建ini.exe')
        os.rename(f'{dir_sdt}{sep}Youma.exe', f'{dir_sdt}{sep}【有码】.exe')
        print('>>重命名完成')

        shutil.copytree('StaticFiles', f'{dir_sdt}{sep}StaticFiles')
        shutil.copy('【特征对照表】.xlsx', f'{dir_sdt}{sep}【特征对照表】.xlsx')
        shutil.copy('【素人车牌】.txt', f'{dir_sdt}{sep}【素人车牌】.txt')
        print('>>StaticFiles、【特征对照表】、【素人车牌】复制完成')

        # os.system(f'cd {dir_sdt}')
        # order = f'{os.getcwd()}{sep}{dir_sdt}{sep}【ini】重新创建ini.exe'
        # print(order)
        # os.system(order)
        # print('>>重新创建ini完成')

    else:
        print('还不支持，请重新输入！\n')
