# -*- coding:utf-8 -*-
import json
import requests
from hashlib import md5
from time import sleep, time
# from traceback import format_exc
# from aip import AipBodyAnalysis  # 百度ai人体分析

from Static.Config import Ini


class Translator(object):
    """
    百度翻译器

    目前用于翻译简介和标题
    """

    def __init__(self, ini: Ini):
        self._tran_id = ini.tran_id
        self._tran_sk = ini.tran_sk
        self._to_language = ini.to_language
        self._requests = requests.Session()

    def translate(self, word: str):
        """
        调用百度翻译API接口，翻译日语简介

        Args:
            word: 需要翻译的内容

        Returns:
            翻译后的内容

        Notes:
            如果百度翻译返回错误码，会用input暂停程序。
        """
        if not word:
            return ''
        if not self._tran_id or not self._tran_sk:
            print('    >你没有填写百度翻译api账户!')
            return ''

        for _ in range(5):
            # 把账户、翻译的内容、时间 混合md5加密，传给百度验证
            salt = str(time())[:10]
            content = f'{self._tran_id}{word}{salt}{self._tran_sk}'
            md5_content = md5(content.encode("utf-8")).hexdigest()
            # 表单paramas
            paramas = {
                'q': word,
                'from': 'jp',
                'to': self._to_language,
                'appid': f'{self._tran_id}',
                'salt': f'{salt}',
                'sign': f'{md5_content}',
            }

            try:
                rsp = self._requests.get('http://api.fanyi.baidu.com/api/trans/vip/translate',
                                         params=paramas, timeout=(6, 7))
            except:
                print('    >百度翻译拉闸了...重新翻译...')
                continue
            rsp_content = str(rsp.content, encoding="utf-8")
            # 百度返回为空
            if not rsp_content:
                print('    >百度翻译返回为空...重新翻译...')
                sleep(1)
                continue
            # 百度返回了dict json
            json_reads = json.loads(rsp_content)
            if 'code' not in json_reads:
                return json_reads['trans_result'][0]['dst']
            self._judge_error(json_reads['code'])
        print('    >翻译简介失败...请截图联系作者...')
        return f'【百度翻译出错】{word}'

    @staticmethod
    def _judge_error(code: str):
        if code == '54003':
            print('    >请求百度翻译太快...技能冷却1秒...')
            sleep(1)
        elif code == '54005':
            print('    >发送了太多超长的简介给百度翻译...技能冷却3秒...')
            sleep(3)
        elif code == '52001':
            print('    >连接百度翻译超时...重新翻译...')
        elif code == '52002':
            print('    >百度翻译拉闸了...重新翻译...')
        elif code == '52003':
            print('    >请正确输入百度翻译API账号！')
            input('>>javsdt已停止工作...')
        elif code == '58003':
            print('    >你的百度翻译API账户被百度封禁了，请联系作者，告诉你解封办法！“')
            input('>>javsdt已停止工作...')
        elif code == '90107':
            print('    >你的百度翻译API账户还未通过认证或者失效，请前往API控制台解决问题！“')
            input('>>javsdt已停止工作...')
        else:
            print('    >百度翻译error_code！请截图联系作者！', code)

    def prefect_zh(self, jav_data):
        """
        翻译jav_data中的简介和标题

        效果：更新jav_data中的TitleZh、PlotZh

        Args:
            jav_data: 当前影片的元数据

        Returns:
            是否进行了翻译操作
        """
        # 翻译出中文标题和简介
        if self._tran_id and self._tran_sk and not jav_data.TitleZh:
            jav_data.TitleZh = self.translate(jav_data.Title)
            sleep(0.9)
            jav_data.PlotZh = self.translate(jav_data.Plot)
            print('    >>翻译plot成功')
            return True
        else:
            print('    >你没有正确填写百度翻译api账户!')
            return False


class AIBody(object):
    """
    百度AL人体分析

    Todo:
    无码的部分还没写，这里待完善
    """

    def __init__(self, ini: Ini):
        self._ai_id = ini.ai_id
        self._ai_ak = ini.ai_ak
        self._ai_sk = ini.ai_sk

    # #########################[百度人体分析]##############################
    # 百度翻译启动
    # def start_body_analysis(self):
    #     if self.bool_face:
    #         return AipBodyAnalysis(self._al_id, self._ai_ak, self._al_sk)
    #     else:
    #         return None
