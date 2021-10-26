import MySettings
from XML import replace_xml_win


class InfoHandler(object):
    def __init__(self, settings:MySettings.Settings):
        self._bool_need_actors_end_of_title = settings.need_actors_end_of_title
        self._int_title_len = settings.int_title_len
        # 用于给用户自定义命名的字典
        self.dict_for_standard = self.get_dict_for_standard()


    # 功能: 用jav_file、jav_model中的原始数据完善dict_for_standard
    # 参数: jav_file 处理的jav视频文件对象，jav_model 保存jav元数据的对象
    # 返回: 无；更新dict_for_standard
    # 辅助: replace_xml_win，replace_xml_win
    def prefect_dict_for_standard(self, jav_file, jav_model):
        # 标题
        str_actors = ' '.join(jav_model.Actors[:3])
        int_actors_len = len(str_actors) if self._bool_need_actors_end_of_title else 0
        int_current_len = self._int_title_len - int_actors_len
        self.dict_for_standard['完整标题'] = replace_xml_win(jav_model.Title)
        self.dict_for_standard['中文完整标题'] = replace_xml_win(jav_model.TitleZh) \
            if jav_model.TitleZh else self.dict_for_standard['完整标题']
        # 处理影片的标题过长。用户只需要在ini中写“标题”，但事实上，文件重命名操作中的“标题“是删减过的标题，nfo中的标题才是完整标题
        if len(self.dict_for_standard['完整标题']) > int_current_len:
            self.dict_for_standard['标题'] = self.dict_for_standard['完整标题'][:int_current_len]
        else:
            self.dict_for_standard['标题'] = self.dict_for_standard['完整标题']
        if len(self.dict_for_standard['中文完整标题']) > int_current_len:
            self.dict_for_standard['中文标题'] = self.dict_for_standard['中文完整标题'][:int_current_len]
        else:
            self.dict_for_standard['中文标题'] = self.dict_for_standard['中文完整标题']
        if self._bool_need_actors_end_of_title:
            self.dict_for_standard['标题'] = f'{self.dict_for_standard["标题"]} {str_actors}'
            self.dict_for_standard['完整标题'] += f'{self.dict_for_standard["完整标题"]} {str_actors}'
            self.dict_for_standard['中文标题'] += f'{self.dict_for_standard["中文标题"]} {str_actors}'
            self.dict_for_standard['中文完整标题'] += f'{self.dict_for_standard["中文完整标题"]} {str_actors}'

        # '是否中字'这一命名元素被激活
        self.dict_for_standard['是否中字'] = self._custom_subtitle_expression if jav_file.Bool_subtitle else ''
        self.dict_for_standard['是否流出'] = self._custom_divulge_expression if jav_file.Bool_divulge else ''
        # 车牌
        self.dict_for_standard['车牌'] = jav_model.Car  # car可能发生了变化
        self.dict_for_standard['车牌前缀'] = jav_model.Car.split('-')[0]
        # 日期
        self.dict_for_standard['发行年月日'] = jav_model.Release
        self.dict_for_standard['发行年份'] = jav_model.Release[0:4]
        self.dict_for_standard['月'] = jav_model.Release[5:7]
        self.dict_for_standard['日'] = jav_model.Release[8:10]
        # 演职人员
        self.dict_for_standard['片长'] = jav_model.Runtime
        self.dict_for_standard['导演'] = replace_xml_win(jav_model.Director) if jav_model.Director else '有码导演'
        # 公司
        self.dict_for_standard['发行商'] = replace_xml_win(jav_model.Publisher) if jav_model.Publisher else '有码发行商'
        self.dict_for_standard['制作商'] = replace_xml_win(jav_model.Studio) if jav_model.Studio else '有码制作商'
        # 评分 系列
        self.dict_for_standard['评分'] = jav_model.Score / 10
        self.dict_for_standard['系列'] = jav_model.Series if jav_model.Series else '有码系列'
        # 全部演员（最多7个） 和 第一个演员
        if jav_model.Actors:
            if len(jav_model.Actors) > 7:
                self.dict_for_standard['全部演员'] = ' '.join(jav_model.Actors[:7])
            else:
                self.dict_for_standard['全部演员'] = ' '.join(jav_model.Actors)
            self.dict_for_standard['首个演员'] = jav_model.Actors[0]
        else:
            self.dict_for_standard['首个演员'] = self.dict_for_standard['全部演员'] = '有码演员'

        # jav_file原文件的一些属性   dict_for_standard['视频']，先定义为原文件名，即将发生变化。
        self.dict_for_standard['视频'] = self.dict_for_standard['原文件名'] = jav_file.Name_no_ext
        self.dict_for_standard['原文件夹名'] = jav_file.Folder
