# -*- coding:utf-8 -*-

from Classes.Web.JavWeb import JavWeb
from Static.Config import Ini


class Dmm(JavWeb):
    """
    Dmm刮削工具

    下载图片
    """

    def __init__(self, settings: Ini):
        appoint_symbol = '大米米'
        headers = {}
        super().__init__(settings, appoint_symbol, headers)
