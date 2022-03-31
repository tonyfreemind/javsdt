import os
from os import sep
from shutil import copyfile
from typing import List, TextIO

from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.Handler.MyLogger import record_video_old
from Classes.Static.Errors import TooManyDirectoryLevelsError
from Classes.Static.Const import Const
from Classes.Static.Config import Ini
from Functions.Progress.Picture import check_picture, crop_poster_youma, add_watermark_subtitle, add_watermark_divulge
from Functions.Utils.XML import replace_xml_invalid_char, replace_os_invalid_char
from Functions.Utils.LittleUtils import cut_str, update_ini_file_value_plus_one


class FileLathe(object):
    """ 本地文件规范化"""

    def __init__(self, ini: Ini):

        self._dict = ini.dict_for_standard
        """字典\n\n用于给用户自定义命名的各类元素包含其中"""

        self._dir_classify_root = ''
        """路径: 归类的目标根目录"""

        self._path_fanart = ''
        """当前处理的视频的预期fanart路径"""

        # region ######################################## 1公式元素 ########################################
        self._bool_need_actors_end_of_title = ini.need_actors_end_of_title
        """是否 去除 标题末尾 可能存在的演员姓名"""
        # endregion

        # region ######################################## 2nfo ########################################
        self._need_nfo = ini.need_nfo
        """是否 收集nfo"""

        self._list_name_nfo_title = ini.list_name_nfo_title
        """公式: nfo中title\n\n注意：程序中有两个标题，一个“完整标题”，一个“可能被删减的标题”。用户只需写“标题”，这里nfo实际采用“完整标题”"""

        self._need_zh_plot = ini.need_zh_plot
        """是否 在nfo中plot写入中文简介，否则写原日语简介"""

        self._need_nfo_genres = ini.need_nfo_genres
        """是否 将特征保存到nfo的<genre>中"""

        self._need_series_as_genre = ini.need_series_as_genre
        """是否 将“系列”写入到特征中"""

        self._need_studio_as_genre = ini.need_studio_as_genre
        """是否 将“片商”写入到特征中"""

        self._list_extra_genres = ini.list_extra_genres
        """公式: 额外添加进特征的元素\n\n允许用户将系列、片商等元素作为特征，因为emby不会直接在影片介绍页面上显示片商，也不会读取系列set"""

        self._need_nfo_tags = ini.need_nfo_tags
        """是否 将特征保存到nfo的<tag>中"""
        # endregion

        # region ######################################## 3重命名 ########################################
        self._need_rename_video = ini.need_rename_video
        """是否 重命名视频"""

        self._list_name_video = ini.list_name_video
        """公式: 重命名视频"""

        self._need_rename_folder = ini.need_rename_folder
        """是否 重命名视频所在文件夹，或者为它创建独立文件夹"""

        self._list_name_folder = ini.list_name_folder
        """公式: 新文件夹名\n\n示例: '车牌', '【', '全部演员', '】'"""
        # endregion

        # region ######################################## 4归类 ########################################
        self._need_classify = ini.need_classify
        """是否 归类影片"""

        self._need_classify_folder = ini.need_classify_folder
        """是否 针对“文件夹”归类jav\n\n“否”即针对“文件”"""

        self._list_name_classify_dir = ini.list_name_classify_dir
        """公式: 归类的目标文件夹的拼接"""
        # endregion

        # region ######################################## 5图片 ########################################
        self._need_fanart_poster = ini.need_fanart_poster
        """是否 下载图片"""

        self._list_name_fanart = ini.list_name_fanart
        """公式: 命名 大封面fanart"""

        self._list_name_poster = ini.list_name_poster
        """公式: 命名 小海报poster"""

        self._need_subtitle_watermark = ini.need_subtitle_watermark
        """是否 如果视频有“中字字幕”，给poster的左上角加上“中文字幕”的斜杠"""

        self._need_divulge_watermark = ini.need_divulge_watermark
        """是否 如果视频是“无码流出”，给poster的右上角加上“无码流出”的斜杠"""
        # endregion

        # region ######################################## 6字幕 ########################################
        self._need_rename_subtitle = ini.need_rename_subtitle
        """是否 重命名用户已拥有的字幕"""
        # endregion

        # region ######################################## 7kodi ########################################
        self._bool_sculpture = ini.need_actor_sculpture
        """是否 为kodi收集演员头像"""

        self._need_only_cd = ini.need_only_cd
        """是否 对于多cd的影片，只收集一份图片和nfo（kodi模式）"""
        # endregion

        # region ######################################## 8代理 ########################################
        self._proxy_db = ini.proxy_db
        """是否 代理db\n\n还有代理javdb上的图片"""

        self._proxy_bus = ini.proxy_bus
        """是否 代理bub\n\n还有代理javbus上的图片cdnbus"""

        self._proxy_dmm = ini.proxy_dmm
        """是否 代理dmm图片\n\njavlibrary和javdb上的有码图片几乎都是直接引用dmm"""
        # endregion

        # region ######################################## 9原影片文件的性质 ########################################
        self._subtitle_expression = ini.subtitle_expression
        """是否中字 这个元素的表现形式"""

        self._divulge_expression = ini.divulge_expression
        """是否流出 这个元素的表现形式"""
        # endregion

        # region ######################################## 10其他设置 ########################################
        self._len_title_limit = ini.len_title_limit
        """命名公式中“标题”的长度\n\nwindows只允许255字符，所以限制长度，nfo中的标题不受此影响"""

        self._url_bus = ini.url_bus
        """网址 javbus"""
        # endregion

    def update_dir_classify_root(self, dir_classify_root: str):
        """用fileExplorer中的dir_classify_root更新"""
        self._dir_classify_root = dir_classify_root

    def prefect_dict_for_standard(self, jav_file: JavFile, jav_data: JavData):
        """
        完善self._dict

        用jav_file、jav_model中的原始数据完善self._dict

        Args:
            jav_file: jav视频文件对象
            jav_data: jav元数据对象
        """
        # 标题
        str_actors = ' '.join(jav_data.Actors[:3])  # 演员们字符串
        len_real_limit = self._len_title_limit - len(str_actors) if self._bool_need_actors_end_of_title else 0
        """实际限制的标题长 = 限制标题长 - 末尾可能存在的演员文字长"""
        title_cut = cut_str(jav_data.Title, len_real_limit)
        zh_complete_title = jav_data.TitleZh or jav_data.Title  # 如果用户用了“中文标题”，但没有翻译标题，那么还是用日文
        zh_title_cut = cut_str(zh_complete_title, len_real_limit)
        # jav_data.Title已经删去末尾的演员姓名，如果用户还需要，则再加上
        if self._bool_need_actors_end_of_title:
            self._dict[Const.TITLE] = f'{title_cut} {str_actors}'
            self._dict[Const.ZH_TITLE] = f'{zh_title_cut} {str_actors}'
            self._dict[Const.COMPLETE_TITLE] = f'{jav_data.Title} {str_actors}'
            self._dict[Const.ZH_COMPLETE_TITLE] = f'{zh_complete_title} {str_actors}'
        else:
            self._dict[Const.TITLE] = title_cut
            self._dict[Const.ZH_TITLE] = zh_title_cut
            self._dict[Const.COMPLETE_TITLE] = jav_data.Title
            self._dict[Const.ZH_COMPLETE_TITLE] = zh_complete_title

        # '是否中字'这一命名元素被激活
        self._dict[Const.BOOL_SUBTITLE] = self._subtitle_expression if jav_file.Bool_subtitle else ''
        self._dict[Const.BOOL_DIVULGE] = self._divulge_expression if jav_file.Bool_divulge else ''
        # 车牌
        self._dict[Const.CAR] = jav_data.Car  # car可能发生了变化
        self._dict[Const.CAR_PREF] = jav_data.Pref
        # 日期
        self._dict[Const.RELEASE] = jav_data.Release
        self._dict[Const.RELEASE_YEAR] = jav_data.Release[:4]
        self._dict[Const.RELEASE_MONTH] = jav_data.Release[5:7]
        self._dict[Const.RELEASE_DAY] = jav_data.Release[8:10]
        # 时长
        self._dict[Const.RUNTIME] = jav_data.Runtime
        # 导演
        self._dict[Const.DIRECTOR] = jav_data.Director or '有码导演'
        # 公司
        self._dict[Const.PUBLISHER] = jav_data.Publisher or '有码发行商'
        self._dict[Const.STUDIO] = jav_data.Studio or '有码制作商'
        # 评分
        self._dict[Const.SCORE] = jav_data.Score / 10
        # 系列
        self._dict[Const.SERIES] = jav_data.Series or '有码系列'
        # 全部演员（最多7个） 和 第一个演员
        if jav_data.Actors:
            self._dict[Const.ALL_ACTORS] = ' '.join(jav_data.Actors[:7])  # 演员至多取7个
            self._dict[Const.FIRST_ACTOR] = jav_data.Actors[0]
        else:
            self._dict[Const.FIRST_ACTOR] = self._dict[Const.ALL_ACTORS] = '有码演员'

        # jav_file原文件的一些属性，先定义为原文件名，即将发生变化。
        self._dict[Const.VIDEO] = self._dict[Const.ORIGIN_VIDEO] = jav_file.Name_no_ext
        self._dict[Const.ORIGIN_FOLDER] = jav_file.Folder

    def _assemble_file_formula(self, name: str):
        """
        组装文件相关的命名公式

        Args:
            name: self的成员名称

        Examples:
            var = self._assemble_formula('_list_name_video')
            # 如果 self._list_name_video = ['车牌', '空格', '标题']，self._dict = {'车牌':'ABC-123', '空格':' ', '标题':'我是一个标题', ...}
            # 则得到 var = “ABC-123 我是一个标题”

        Returns:
            拼装命名公式后得到的字符串
        """
        return "".join(
            [replace_os_invalid_char(self._dict[element])
             for element in getattr(self, name)]
        )

    def _assemble_nfo_formula(self, name: str):
        """
        组装nfo相关的命名公式

        Args:
            name: self的成员名称

        Examples:
            var = self._assemble_formula('_list_name_nfo_title')
            # 如果 self._list_name_nfo_title = ['车牌', '空格', '标题']，self._dict = {'车牌':'ABC-123', '空格':' ', '标题':'我是一个标题', ...}
            # 则得到 var = “ABC-123 我是一个标题”

        Returns:
            拼装得到的字符串
        """
        return "".join(
            [replace_xml_invalid_char(self._dict[element])
             for element in getattr(self, name)]
        )

    def rename_mp4(self, jav_file: JavFile):
        """
        重命名磁盘中的视频及字幕文件

        Notes:
            如果重命名失败，会返回目标的视频文件名，需用户自行重命名。如果重命名成功，则返回空。

        Args:
            jav_file: jav视频文件对象

        Returns:
            path_return，需用户自行重命名的视频文件名
        """
        path_return = ''
        """返回的路径\n\n如果重命名操作不成功，将目标视频文件名返回，提醒用户自行重命名"""

        if self._need_rename_video:
            # region 得到新视频文件名
            name_new = self._assemble_file_formula('_list_name_video')
            """新视频文件名，不带文件类型"""
            path_new = f'{jav_file.Dir}{sep}{name_new}{jav_file.Cd}{jav_file.Ext}'
            """视频文件的新路径"""
            # endregion

            # region 重命名视频文件
            if not os.path.exists(path_new):
                # 不存在同路径视频文件
                os.rename(jav_file.Path, path_new)
                record_video_old(jav_file.Path, path_new)
            elif jav_file.Path.upper() == path_new.upper():
                # 已存在目标文件，且就是现在的文件
                try:
                    os.rename(jav_file.Path, path_new)
                # windows本地磁盘，“abc-123.mp4”重命名为“abc-123.mp4”或“ABC-123.mp4”没问题，但有用户反映，挂载的磁盘会报错“file exists error”
                except FileExistsError:
                    # 提醒用户后续自行更改
                    path_return = path_new
                    # 注意：即使重命名操作没有成功，但之后的操作（归类、保存nfo、下载图片等）仍然围绕预期文件名来命名
            # 存在目标文件，但不是现在的文件。
            else:
                raise FileExistsError(f'重命名影片失败，重复的影片，已经有相同文件名的视频了: {path_new}')  # 【终止整理】
            self._dict[Const.VIDEO] = name_new  # 【更新】
            jav_file.Name = f'{name_new}{jav_file.Ext}'  # 【更新】
            print(f'    >修改文件名{jav_file.Cd}完成')
            # endregion

            # region 重命名字幕文件
            if jav_file.Subtitle and self._need_rename_subtitle:
                subtitle_new = f'{name_new}{jav_file.Ext_subtitle}'  # 新字幕文件名
                path_subtitle_new = f'{jav_file.Dir}{sep}{subtitle_new}'  # 字幕文件的新路径
                if jav_file.Path_subtitle != path_subtitle_new:
                    os.rename(jav_file.Path_subtitle, path_subtitle_new)
                    jav_file.Subtitle = subtitle_new  # 【更新】
                print('    >修改字幕名完成')
            # endregion
        return path_return

    def classify_files(self, jav_file: JavFile):
        """
        2归类影片

        只针对视频文件和字幕文件，无视它们当前所在文件夹。

        Args:
            jav_file: jav视频文件对象
        """
        # 如果不需要归类，或者是针对文件夹来归类
        if not self._need_classify or self._need_classify_folder:
            return

        # region 确定归类的目标文件夹
        dir_target = f'{self._dir_classify_root}{sep}{self._assemble_file_formula("_list_name_classify_dir")}'
        """归类的目标文件夹路径"""
        if not os.path.exists(dir_target):
            os.makedirs(dir_target)
        # endregion

        # region 移动视频
        path_target = f'{dir_target}{sep}{jav_file.Name}'  # 新的视频文件路径
        if os.path.exists(path_target):
            raise FileExistsError(f'归类失败，重复的影片，归类的目标文件夹已经存在相同的影片: {path_target}')  # 【终止整理】

        os.rename(jav_file.Path, path_target)
        jav_file.Dir = dir_target  # 【更新】jav.dir
        print('    >归类视频文件完成')
        # endregion

        # region 移动字幕
        if jav_file.Subtitle:
            path_subtitle_new = f'{dir_target}{sep}{jav_file.Subtitle}'  # 新的字幕文件路径
            if jav_file.Path_subtitle != path_subtitle_new:
                os.rename(jav_file.Path_subtitle, path_subtitle_new)  # 下面不再处理字幕，不用更新字幕成员
        # endregion

    def rename_folder(self, jav_file: JavFile):
        """
        3重命名文件夹或创建独立文件夹

        如果已进行第2操作，第3操作不会进行，因为用户只需要归类视频文件，不需要管文件夹。

        Args:
            jav_file: jav元数据对象
        """
        if not self._need_rename_folder:
            return

        # region 得到新文件夹名

        folder_new = self._assemble_file_formula('_list_name_folder')
        """新的所在文件夹名称"""
        # endregion

        # 视频已经在独立文件夹中，且当前视频是该车牌的最后一集，他的兄弟姐妹已经处理完成，直接重命名当前文件夹，无需新建文件夹。
        if jav_file.Bool_in_separate_folder and jav_file.Episode == jav_file.Sum_all_episodes:
            # region 直接重命名现有文件夹
            dir_new = f'{os.path.dirname(jav_file.Dir)}{sep}{folder_new}'  # 新的视频文件所在文件夹路径
            # 目标文件夹还不存在
            if not os.path.exists(dir_new):
                os.rename(jav_file.Dir, dir_new)
                jav_file.Dir = dir_new  # 【更新】jav.dir
            elif jav_file.Dir != dir_new:
                # 文件夹已存在，但不是现在所处的文件夹
                raise FileExistsError(f'重命名文件夹失败，已存在相同文件夹: {dir_new}')  # 【终止整理】
            print('    >重命名文件夹完成')
            # endregion
        else:
            # region 创建新的独立文件夹，再移动
            dir_target = f'{jav_file.Dir}{sep}{folder_new}'
            """新创建的独立文件夹"""
            # 确认没有同名文件夹
            if not os.path.exists(dir_target):
                os.makedirs(dir_target)
            path_new = f'{dir_target}{sep}{jav_file.Name}'
            """新的视频文件路径"""
            # 如果这个文件夹是现成的，确认在它内部没有同名视频文件。
            if os.path.exists(path_new):
                raise FileExistsError(f'创建独立文件夹失败，已存在相同的视频文件: {path_new}')  # 【终止整理】

            # 移动视频
            os.rename(jav_file.Path, path_new)
            jav_file.Dir = dir_target  # 【更新】jav.dir
            print('    >移动到独立文件夹完成')

            # 移动字幕
            if jav_file.Subtitle:
                path_subtitle_new = f'{dir_target}{sep}{jav_file.Subtitle}'  # 新的字幕路径
                os.rename(jav_file.Path_subtitle, path_subtitle_new)  # 后续不会操作字幕文件了，不再更新字幕成员
                print('    >移动字幕到独立文件夹')
            # endregion

    def collect_sculpture(self, jav_file: JavFile, jav_data: JavData):
        """
        6为当前jav收集演员头像到“.actors”文件夹中

        Args:
            jav_file: jav视频文件对象
            jav_data: jav元数据对象
        """
        # 用户不需要收集头像；当前处理的视频文件不是最后一cd。
        if not self._bool_sculpture or jav_file.Episode != 1:
            return

        if not jav_data.Actors:
            print('    >未知演员，无法收集头像')
            return

        for actor in jav_data.Actors:
            path_exist_actor = f'{Const.FOLDER_ACTOR}{sep}{actor[0]}{sep}{actor}'
            """事先准备好的演员头像路径"""
            if os.path.exists(f'{path_exist_actor}.jpg'):
                ext_pic = '.jpg'
            elif os.path.exists(f'{path_exist_actor}.png'):
                ext_pic = '.png'
            else:
                update_ini_file_value_plus_one(Const.INI_ACTOR, Const.NODE_NO_ACTOR, actor)
                continue
            # 已经收录了这个演员头像
            dir_actor_target = f'{jav_file.Dir}{sep}.actors{sep}'
            """头像的目标文件夹"""
            if not os.path.exists(dir_actor_target):
                os.makedirs(dir_actor_target)
            # 复制一份到“.actors”
            copyfile(f'{path_exist_actor}{ext_pic}', f'{dir_actor_target}{actor}{ext_pic}')
            print('    >演员头像收集完成: ', actor)

    def classify_folder(self, jav_file: JavFile):
        """
        7归类影片，针对文件夹

        如果已进行第2操作，第7操作不会进行，因为用户只需要归类视频文件，不需要管文件夹。

        Args:
            jav_file: jav视频文件对象
        """
        # 如果用户不需要归类，或者不需要针对文件夹归类（已经针对文件归类了）
        if not self._need_classify or not self._need_classify_folder:
            return

        # 当前视频是该车牌的最后一集，才能移动
        if jav_file.Episode != jav_file.Sum_all_episodes:
            return

        # 用户选择的文件夹是一部影片的独立文件夹（这次整理只整理了一部车牌），为了避免在这个文件夹里又创建新的归类文件夹（无限套娃）
        if jav_file.Bool_in_separate_folder and self._dir_classify_root.startswith(jav_file.Dir):
            raise TooManyDirectoryLevelsError('无法归类，不建议在当前文件夹内再新建文件夹')

        # region 文件夹内的文件们集体搬家
        dir_target = f'{self._dir_classify_root}{sep}' \
                     f'{self._assemble_file_formula("_list_name_classify_dir")}' \
                     f'{sep}{jav_file.Folder}'
        """新 视频所在文件夹的路径"""
        if os.path.exists(dir_target):
            raise FileExistsError(f'归类失败，归类的目标位置已存在相同文件夹: {dir_target}')

        os.makedirs(dir_target)
        # 把现在文件夹里的东西都搬过去
        jav_files = os.listdir(jav_file.Dir)
        for file in jav_files:
            os.rename(f'{jav_file.Dir}{sep}{file}', f'{dir_target}{sep}{file}')
        # 删除“旧房子”，这是唯一的删除操作，而且os.rmdir只能删除空文件夹
        os.rmdir(jav_file.Dir)
        print('    >归类文件夹完成')
        # endregion

    # region 写nfo
    def write_nfo(self, jav_file: JavFile, jav_data: JavData, genres: List[str]):
        """
        写nfo

        Args:
            jav_file: jav视频文件对象
            jav_data: jav元数据对象
            genres: 特征（包含“中文字幕”等额外特征），不同于jav_data.Genres
        """
        # 不需要nfo
        if not self._need_nfo:
            return

        # nfo路径，果是为kodi准备的nfo，不需要多cd
        path_nfo = f'{jav_file.Dir}{sep}{jav_file.Name_no_ext.replace(jav_file.Cd, "")}.nfo' \
            if self._need_only_cd \
            else f'{jav_file.Dir}{sep}{jav_file.Name_no_ext}.nfo'
        with open(file=path_nfo, mode='w', encoding='utf-8') as f:
            f.write(
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n'
                f'<movie>\n'
                f'  <plot>{replace_xml_invalid_char(jav_data.PlotZh if self._need_zh_plot else jav_data.Plot)}{replace_xml_invalid_char(jav_data.Review)}</plot>\n'
                f'  <title>{self._assemble_nfo_formula("_list_name_nfo_title")}</title>\n'
                f'  <originaltitle>{jav_data.Car} {replace_xml_invalid_char(jav_data.Title)}</originaltitle>\n'
                f'  <director>{replace_xml_invalid_char(jav_data.Director)}</director>\n'
                f'  <rating>{jav_data.Score / 10}</rating>\n'
                f'  <criticrating>{jav_data.Score}</criticrating>\n'
                f'  <year>{jav_data.Release[:4]}</year>\n'
                f'  <mpaa>NC-17</mpaa>\n'
                f'  <customrating>NC-17</customrating>\n'
                f'  <countrycode>JP</countrycode>\n'
                f'  <premiered>{jav_data.Release}</premiered>\n'
                f'  <release>{jav_data.Release}</release>\n'
                f'  <runtime>{jav_data.Runtime}</runtime>\n'
                f'  <country>日本</country>\n'
                f'  <studio>{replace_xml_invalid_char(jav_data.Studio)}</studio>\n'
                f'  <id>{jav_data.Car}</id>\n'
                f'  <num>{jav_data.Car}</num>\n'
                f'  <set>{replace_xml_invalid_char(jav_data.Series)}</set>\n'
            )

            # 需要将特征写入genre或tag中
            if self._need_nfo_genres:
                self._write_genres_or_tags(f, jav_data, genres, 'genre')
            if self._need_nfo_tags:
                self._write_genres_or_tags(f, jav_data, genres, 'tag')

            # 写入演员
            self._write_actors(f, jav_data)

            # 结尾
            f.write('</movie>\n')
        print('    >nfo收集完成')

    def _write_genres_or_tags(self, nfo: TextIO, jav_data: JavData, genres: List[str], symbol: str):
        for i in genres:
            nfo.write(f'  <{symbol}>{i}</{symbol}>\n')
        if self._need_series_as_genre and jav_data.Series:
            nfo.write(f'  <{symbol}>系列:{replace_xml_invalid_char(jav_data.Series)}</{symbol}>\n')
        if self._need_studio_as_genre and jav_data.Studio:
            nfo.write(f'  <{symbol}>片商:{replace_xml_invalid_char(jav_data.Studio)}</{symbol}>\n')
        for i in self._list_extra_genres:
            nfo.write(f'  <{symbol}>{self._dict[i]}</{symbol}>\n')

    @staticmethod
    def _write_actors(nfo: TextIO, jav_data: JavData):
        for actor in jav_data.Actors:
            nfo.write(f'  <actor>\n'
                      f'    <name>{actor}</name>\n'
                      f'    <type>Actor</type>\n'
                      f'  </actor>\n')

    # endregion

    def need_fanart_poster(self):
        return self._need_fanart_poster

    def need_download_fanart(self, jav_file: JavFile):
        """
        判定是否需要下载fanart

        Args:
            jav_file: jav视频文件对象

        Returns:
            是否需要下载
        """

        # fanart预期路径
        path_fanart = f'{jav_file.Dir}{sep}{self._assemble_file_formula("_list_name_fanart")}'
        # kodi只需要一份图片，不管视频是cd几，仅需一份图片。
        if self._need_only_cd:
            path_fanart = path_fanart.replace(jav_file.Cd, '')

        # （1）如果现在的视频文件不是cd1（不是第一集），emby需要多份，直接复制第一集的图片
        # （2）path_fanart已存在，也不需要重复搞图片
        # 如果用户有例如abc-123.mkv和abc-123.mp4这两个视频，并且用户设置“不重命名视频”（导致没有分cd1、cd2），
        # 处理完mkv，再处理mp4，mp4的fanart路径和mkv的相同
        # 引发报错raise SameFileError("{!r} and {!r} are the same file".format(src, dst))
        # 所以一定要判断下path_fanart有没有，如果有，就不再重复搞图片了
        elif jav_file.Episode != 1 and not os.path.exists(path_fanart):
            # 如果用户在一个车牌上有两个视频，一个有字幕，变成了T28-557㊥-cd1-fanart.jpg，另一个没字幕，变成了T28-557-cd2-fanart.jpg，
            # 简单地把cd1的图片路径替换一下cd2，期望能得到cd2的路径，“T28-557㊥-cd1-fanart.jpg” => “T28-557㊥-cd2-fanart.jpg”
            # 但cd2的实际路径是“T28-557-cd2-fanart.jpg”，所以一定先判定一下path_fanart_cd1是否存在
            path_fanart_cd1 = path_fanart.replace(jav_file.Cd, '-cd1')
            if os.path.exists(path_fanart_cd1):
                copyfile(path_fanart_cd1, path_fanart)
                print('    >fanart.jpg复制成功')
                self._path_fanart = path_fanart
                return False  # 复制成功，无需下载

        self._path_fanart = path_fanart
        if not check_picture(path_fanart):
            return True  # 需要下载

        print('    >已有fanart.jpg')
        # 如果 path_fanart = ABC-123.jpg，而用户已有有一个 abc-123，os.path.exists()也会判定成功，所以重命名一下
        os.rename(path_fanart, path_fanart)
        return False  # 已有，不需要下载

    def crop_poster(self, jav_file: JavFile):
        """
        整出poster，加上条幅

        （1）可能不需要管图片；（2）可以直接复制之前cd的poster；（3）依据fanart裁剪poster。

        Args:
            jav_file: jav视频文件对象
        """

        # poster预期路径
        path_poster = f'{jav_file.Dir}{sep}{self._assemble_file_formula("_list_name_poster")}'

        if self._need_only_cd:
            path_poster = path_poster.replace(jav_file.Cd, '')
        elif jav_file.Episode != 1 and not os.path.exists(path_poster):
            path_poster_cd1 = path_poster.replace(jav_file.Cd, '-cd1')
            if os.path.exists(path_poster_cd1):
                copyfile(path_poster_cd1, path_poster)
                print('    >poster.jpg复制成功')
                return  # 复制成功

        if check_picture(path_poster):
            print('    >已有poster.jpg')
            os.rename(path_poster, path_poster)
            # 这里有个问题，如果用户已有poster了，但没条幅，用户又想加上条幅...无法为用户加上
        else:
            crop_poster_youma(self._path_fanart, path_poster)
            # 需要加上条纹
            if self._need_subtitle_watermark and jav_file.Bool_subtitle:
                add_watermark_subtitle(path_poster)
            if self._need_divulge_watermark and jav_file.Bool_divulge:
                add_watermark_divulge(path_poster)

    def check_actors(self):
        """
        检查“演员头像for kodi.ini”、“演员头像”文件夹是否存在
        """
        # 检查头像: 如果需要为kodi整理头像，先检查演员头像ini、头像文件夹是否存在。
        if self._bool_sculpture:
            if not os.path.exists(Const.FOLDER_ACTOR):
                input(f'\n“{Const.FOLDER_ACTOR}”文件夹丢失！请把它放进exe的文件夹中！\n')
            if not os.path.exists(Const.INI_ACTOR):
                if os.path.exists(Const.INI_ACTOR_ORIGIN):
                    copyfile(Const.INI_ACTOR_ORIGIN, Const.INI_ACTOR)
                    print(f'\n“{Const.INI_ACTOR}”成功！')
                else:
                    input('\n请打开“【ini】重新创建ini.exe”创建丢失的程序组件!再重启程序')
