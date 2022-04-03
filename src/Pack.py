import os
import sys

print('\n请选择打包程序:'
      '    0、退出'
      '    1、CreateIni.py'
      '    2、Youma.py\n')

while 1:
    pattern = input('请输入:')

    if pattern == '0':
        sys.exit()

    if pattern == '1':
        os.system('pyinstaller CreateIni.py -i ./StaticFiles/ini.ico')
        print('OK！\n')

    elif pattern == '2':
        os.system('pyinstaller Youma.py -i ./StaticFiles/javsdt.ico')
        print('OK！\n')

    else:
        print('还不支持，请重新输入！\n')
