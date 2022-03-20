class TooManyDirectoryLevelsError(Exception):
    """太多的文件夹层级\n\n如果用户选择一个独立文件夹，并希望归类，程序会继续在这个独立文件夹内新建归类文件夹，应当阻止这个操作"""
    pass


class DownloadFanartError(Exception):
    """下载fanart.jpg出错"""
    pass


class SpecifiedUrlError(Exception):
    """用户为影片指定的网址有问题"""
    pass


class CustomClassifyTargetDirError(Exception):
    """用户自定义的归类根目录有问题"""
    pass


class DbCodePageNothingError(Exception):
    """当前javdb的车头页面无数据"""
    pass


class InRangeButDbNotFoundError(Exception):
    """javdb找不到"""
    pass

