import os
from os import sep
import Config
from shutil import copyfile
from configparser import RawConfigParser  # 读取ini
from configparser import NoOptionError  # ini文件不存在或不存在指定node的错误

from Car import extract_pref
from Classes.Model.JavData import JavData
from Classes.Model.JavFile import JavFile
from Classes.MyLogger import record_video_old
from Classes.Errors import TooManyDirectoryLevelsError, DownloadFanartError
from Classes.Const import Const
from Functions.Utils.Download import download_pic
from Functions.Progress.Picture import check_picture, crop_poster_youma, add_watermark_subtitle, add_watermark_divulge
from Functions.Utils.XML import replace_xml_win, replace_xml
from Functions.Utils.LittleUtils import cut_str


class Standard(object):
    """ 本地文件规范化"""

    def __init__(self, ini: Config.Ini):

        self._dict_for_standard = ini.dict_for_standard
        """字典\n\n用于给用户自定义命名的各类元素包含其中"""

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

        self._dir_custom_classify_root = ini.dir_custom_classify_root
        """路径: 归类的目标根目录"""

        self._list_name_classify_dir = ini.list_name_classify_dir
        """公式: 归类的目标文件夹的拼接\n\n由classify_formula切割得到"""
        # endregion

        # region ######################################## 5图片 ########################################
        self._need_download_fanart = ini.need_download_fanart
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
        """是否 对于多cd的影片，kodi只需要一份图片和nfo"""
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
        self._int_title_len = ini.int_title_len
        """命名公式中“标题”的长度\n\nwindows只允许255字符，所以限制长度，nfo中的标题不受此影响"""

        self._url_bus = ini.url_bus
        """网址 javbus"""

        # 定义 Windows中的非法字符, 将非法字符替换为空格
        self._winDic = str.maketrans(r':<>"\?/*', '        ')
        """定义 Windows中的非法字符, 将非法字符替换为空格"""
        # endregion

    def prefect_dict_for_standard(self, jav_file: JavFile, jav_data: JavData):
        """
        完善dict_for_standard

        用jav_file、jav_model中的原始数据完善dict_for_standard，用于后续的规范化

        Args:
            jav_file: jav视频文件对象
            jav_data: jav元数据对象
        """
        # 标题
        str_actors = ' '.join(jav_data.Actors[:3])  # 演员们字符串
        int_actors_len = len(str_actors) if self._bool_need_actors_end_of_title else 0  # 演员文字长
        len_real_limit = self._int_title_len - int_actors_len  # 实际限制的标题长 = 限制标题长 - 末尾可能存在的演员文字长
        complete_title = replace_xml_win(jav_data.Title)
        zh_complete_title = replace_xml_win(jav_data.TitleZh) if jav_data.TitleZh else complete_title
        title = cut_str(complete_title, len_real_limit)
        zh_title = cut_str(zh_complete_title, len_real_limit)
        # jav_data.Title已经删去末尾的演员姓名，如果用户还需要，则再加上
        if self._bool_need_actors_end_of_title:
            self._dict_for_standard[Const.TITLE] = f'{title} {str_actors}'
            """可能删减过的日语标题\n\n用于文件的重命名"""
            self._dict_for_standard[Const.COMPLETE_TITLE] += f'{complete_title} {str_actors}'
            """完整的日语标题\n\n用于nfo中记录信息"""
            self._dict_for_standard[Const.ZH_TITLE] += f'{zh_title} {str_actors}'
            """可能删减过的中文标题\n\n用于文件的重命名，如果用户没有设置翻译账户，则仍为日语标题"""
            self._dict_for_standard[Const.ZH_COMPLETE_TITLE] += f'{zh_complete_title} {str_actors}'
            """完整的中文标题\n\n用于nfo中记录信息，如果用户没有设置翻译账户，则仍为日语标题"""

        # '是否中字'这一命名元素被激活
        self._dict_for_standard[Const.BOOL_SUBTITLE] = self._subtitle_expression if jav_file.Bool_subtitle else ''
        self._dict_for_standard[Const.BOOL_DIVULGE] = self._divulge_expression if jav_file.Bool_divulge else ''
        # 车牌
        self._dict_for_standard[Const.CAR] = jav_data.Car  # car可能发生了变化
        self._dict_for_standard[Const.CAR_PREF] = extract_pref(jav_data.Car)
        # 日期
        self._dict_for_standard[Const.RELEASE] = jav_data.Release
        self._dict_for_standard[Const.RELEASE_YEAR] = jav_data.Release[0:4]
        self._dict_for_standard[Const.RELEASE_MONTH] = jav_data.Release[5:7]
        self._dict_for_standard[Const.RELEASE_DAY] = jav_data.Release[8:10]
        # 演职人员
        self._dict_for_standard[Const.RUNTIME] = jav_data.Runtime
        self._dict_for_standard[Const.DIRECTOR] = replace_xml_win(jav_data.Director) if jav_data.Director else '有码导演'
        # 公司
        self._dict_for_standard[Const.PUBLISHER] = replace_xml_win(
            jav_data.Publisher) if jav_data.Publisher else '有码发行商'
        self._dict_for_standard[Const.STUDIO] = replace_xml_win(jav_data.Studio) if jav_data.Studio else '有码制作商'
        # 评分 系列
        self._dict_for_standard[Const.SCORE] = jav_data.Score / 10
        self._dict_for_standard[Const.SERIES] = jav_data.Series if jav_data.Series else '有码系列'
        # 全部演员（最多7个） 和 第一个演员
        if jav_data.Actors:
            self._dict_for_standard[Const.ALL_ACTORS] = ' '.join(jav_data.Actors[:7])  # 演员至多取7个
            self._dict_for_standard[Const.FIRST_ACTOR] = jav_data.Actors[0]
        else:
            self._dict_for_standard[Const.FIRST_ACTOR] = self._dict_for_standard[Const.ALL_ACTORS] = '有码演员'

        # jav_file原文件的一些属性，先定义为原文件名，即将发生变化。
        self._dict_for_standard[Const.VIDEO] = self._dict_for_standard[Const.ORIGIN_VIDEO] = jav_file.Name_no_ext
        self._dict_for_standard[Const.ORIGIN_FOLDER] = jav_file.Folder

    def rename_mp4(self, jav_file: JavFile):
        """
        重命名磁盘中的视频及字幕文件

        Notes:
            如果重命名失败，会返回目标的视频文件名，需用户自行重命名。如果重命名成功，则返回空。

        Args:
            jav_file: jav视频文件对象

        Returns:
            需用户自行重命名的视频文件名
        """
        path_return = ''
        """返回的路径\n\n如果重命名操作不成功，将目标视频文件名返回，提醒用户自行重命名"""
        if self._need_rename_video:
            # region 得到新视频文件名
            name_dest = ''
            """新视频文件名\n\n不带文件类型后缀"""
            for element in self._list_name_video:
                name_dest = f'{name_dest}{self._dict_for_standard[element]}'
            if os.name == 'nt':  # 如果是windows系统
                name_dest = name_dest.translate(self._winDic)  # 将文件名中的非法字符替换为空格
            name_dest = f'{name_dest.strip()}{jav_file.Cd}'  # 去除首尾空格，否则windows会自动删除空格，导致程序仍以为带空格
            path_new = f'{jav_file.Dir}{sep}{name_dest}{jav_file.Ext}'
            """视频文件的新路径"""
            # endregion

            # region 重命名视频文件
            # 不存在同路径视频文件
            if not os.path.exists(path_new):
                os.rename(jav_file.Path, path_new)
                record_video_old(jav_file.Path, path_new)
            # 已存在目标文件，且就是现在的文件
            elif jav_file.Path.upper() == path_new.upper():
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
            self._dict_for_standard[Const.VIDEO] = name_dest  # 【更新】
            jav_file.Name = f'{name_dest}{jav_file.Ext}'  # 【更新】
            print(f'    >修改文件名{jav_file.Cd}完成')
            # endregion

            # region 重命名字幕文件
            if jav_file.Subtitle and self._need_rename_subtitle:
                subtitle_new = f'{name_dest}{jav_file.Ext_subtitle}'
                """新字幕文件名"""
                path_subtitle_new = f'{jav_file.Dir}{sep}{subtitle_new}'
                """字幕文件的新路径"""
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
        # 如果需要归类，且不是针对文件夹来归类
        if self._need_classify and not self._need_classify_folder:

            # region 得到归类的目标文件夹
            dir_dest = f'{self._dir_custom_classify_root}{sep}'
            """归类的目标文件夹路径"""
            for element in self._list_name_classify_dir:
                dir_dest = f'{dir_dest}{self._dict_for_standard[element].strip()}'
            # endregion

            # region 创建该文件夹
            if not os.path.exists(dir_dest):
                os.makedirs(dir_dest)
            path_new = f'{dir_dest}{sep}{jav_file.Name}'
            """新的视频文件路径"""
            # endregion

            # region 移动视频和字幕
            if not os.path.exists(path_new):  # 目标文件夹没有相同的影片
                os.rename(jav_file.Path, path_new)
                jav_file.Dir = dir_dest  # 【更新】jav.dir
                print('    >归类视频文件完成')
                # 移动字幕
                if jav_file.Subtitle:
                    path_subtitle_new = f'{dir_dest}{sep}{jav_file.Subtitle}'
                    """新的字幕文件路径"""
                    if jav_file.Path_subtitle != path_subtitle_new:
                        os.rename(jav_file.Path_subtitle, path_subtitle_new)
                    print('    >归类字幕文件完成')
            else:
                raise FileExistsError(f'归类失败，重复的影片，归类的目标文件夹已经存在相同的影片: {path_new}')  # 【终止对该jav的整理】
            # endregion

    def rename_folder(self, jav_file: JavFile):
        """
        3重命名文件夹或创建独立文件夹

        如果已进行第2操作，第3操作不会进行，因为用户只需要归类视频文件，不需要管文件夹。

        Args:
            jav_file: jav元数据对象
        """
        if self._need_rename_folder:

            # region 得到新文件夹名
            folder_new = ''
            for element in self._list_name_folder:
                folder_new = f'{folder_new}{self._dict_for_standard[element]}'
            folder_new = folder_new.rstrip(' .')  # 【临时变量】新的所在文件夹。去除末尾空格和“.”
            # endregion

            # 视频已经在独立文件夹中，直接重命名当前文件夹
            if jav_file.Bool_in_separate_folder:
                # region 重命名文件夹
                # 当前视频是该车牌的最后一集，表明他的兄弟姐妹已经处理完成，才会重命名它们的“家”。
                if jav_file.Episode == jav_file.Sum_all_episodes:
                    dir_new = f'{os.path.dirname(jav_file.Dir)}{sep}{folder_new}'
                    """新的（视频文件）所在文件夹路径"""
                    # 目标文件夹还不存在
                    if not os.path.exists(dir_new):
                        os.rename(jav_file.Dir, dir_new)
                        jav_file.Dir = dir_new  # 【更新】jav.dir
                    # 目标文件夹存在，但就是现在的文件夹，即新旧相同
                    elif jav_file.Dir == dir_new:
                        pass
                    # 真的有一个同名的文件夹了
                    else:
                        raise FileExistsError(f'重命名文件夹失败，已存在相同文件夹: {dir_new}')  # 【终止整理】
                    print('    >重命名文件夹完成')
                # endregion
            # 视频不在独立文件夹中，在当前文件夹中创建新的独立的文件夹
            else:
                # region 创建新的独立文件夹
                dir_dest = f'{jav_file.Dir}{sep}{folder_new}'
                """需要创建的文件夹"""
                # 确认没有同名文件夹
                if not os.path.exists(dir_dest):
                    os.makedirs(dir_dest)
                path_new = f'{dir_dest}{sep}{jav_file.Name}'  # 【临时变量】新的影片路径
                # 如果这个文件夹是现成的，确认在它内部没有同名视频文件。
                if not os.path.exists(path_new):
                    os.rename(jav_file.Path, path_new)
                    jav_file.Dir = dir_dest  # 【更新】jav.dir
                    print('    >移动到独立文件夹完成')
                    # 移动字幕
                    if jav_file.Subtitle:
                        path_subtitle_new = f'{dir_dest}{sep}{jav_file.Subtitle}'
                        """新的字幕路径"""
                        os.rename(jav_file.Path_subtitle, path_subtitle_new)
                        # 后续不会操作 字幕文件 了，jav.path_subtitle不再更新
                        print('    >移动字幕到独立文件夹')
                # 里面已有同名视频文件，这不是它的家。
                else:
                    raise FileExistsError(f'创建独立文件夹失败，已存在相同的视频文件: {path_new}')  # 【终止整理】
                # endregion

    def collect_sculpture(self, jav_file: JavFile, jav_data: JavData):
        """
        6为当前jav收集演员头像到“.actors”文件夹中

        Args:
            jav_file: jav视频文件对象
            jav_data: jav元数据对象
        """
        if self._bool_sculpture and jav_file.Episode == 1:
            if not jav_data.Actors:
                print('    >未知演员，无法收集头像')
            else:
                for each_actor in jav_data.Actors:
                    path_exist_actor = f'{Const.FOLDER_ACTOR}{sep}{each_actor[0]}{sep}{each_actor}'  # 事先准备好的演员头像路径
                    if os.path.exists(f'{path_exist_actor}.jpg'):
                        pic_type = '.jpg'
                    elif os.path.exists(f'{path_exist_actor}.png'):
                        pic_type = '.png'
                    else:
                        config_actor = RawConfigParser()
                        config_actor.read(Const.INI_ACTOR, encoding='utf-8-sig')
                        try:
                            each_actor_times = config_actor.get(Const.NODE_NO_ACTOR, each_actor)
                            config_actor.set(Const.NODE_NO_ACTOR, each_actor, str(int(each_actor_times) + 1))
                        except NoOptionError:
                            config_actor.set(Const.NODE_NO_ACTOR, each_actor, '1')
                        config_actor.write(open(Const.INI_ACTOR, "w", encoding='utf-8-sig'))
                        continue
                    # 已经收录了这个演员头像
                    dir_dest_actor = f'{jav_file.Dir}{sep}.actors{sep}'  # 头像的目标文件夹
                    if not os.path.exists(dir_dest_actor):
                        os.makedirs(dir_dest_actor)
                    # 复制一份到“.actors”
                    copyfile(f'{path_exist_actor}{pic_type}', f'{dir_dest_actor}{each_actor}{pic_type}')
                    print('    >演员头像收集完成: ', each_actor)

    def classify_folder(self, jav_file: JavFile):
        """
        7归类影片，针对文件夹

        如果已进行第2操作，第7操作不会进行，因为用户只需要归类视频文件，不需要管文件夹。

        Args:
            jav_file: jav视频文件对象
        """
        # 需要归类，且当前视频文件是该影片的最后一集
        if self._need_classify and self._need_classify_folder and jav_file.Episode == jav_file.Sum_all_episodes:

            # 用户选择的文件夹是一部影片的独立文件夹，为了避免在这个文件夹里又创建新的归类文件夹
            if jav_file.Bool_in_separate_folder and self._dir_custom_classify_root.startswith(jav_file.Dir):
                raise TooManyDirectoryLevelsError(f'无法归类，不建议在当前文件夹内再新建文件夹')

            # region 得到归类的目标文件夹
            dir_dest = f'{self._dir_custom_classify_root}{sep}'  # 例如C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
            """归类的目标文件夹路径\n\n不包含视频文件所在的文件夹"""
            for j in self._list_name_classify_dir:
                dir_dest = f'{dir_dest}{self._dict_for_standard[j].rstrip(" .")}'
            dir_new = f'{dir_dest}{sep}{jav_file.Folder}'  # 例如C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\【葵司】AVOP-127\
            """新 视频所在文件夹的路径"""
            # endregion

            # region 搬家
            # 目标文件夹还不存在
            if not os.path.exists(dir_new):
                os.makedirs(dir_new)
                # 把现在文件夹里的东西都搬过去
                jav_files = os.listdir(jav_file.Dir)
                for file in jav_files:
                    os.rename(f'{jav_file.Dir}{sep}{file}', f'{dir_new}{sep}{file}')
                # 删除“旧房子”，这是唯一的删除操作，而且os.rmdir只能删除空文件夹
                os.rmdir(jav_file.Dir)
                print('    >归类文件夹完成')
            # 用户已经有了这个文件夹，可能以前处理过同车牌的视频
            else:
                raise FileExistsError(f'归类失败，归类的目标位置已存在相同文件夹: {dir_new}')
            # endregion

    def write_nfo(self, jav_file: JavFile, jav_model: JavData, genres: list):
        """
        写nfo

        Args:
            jav_file: jav视频文件对象
            jav_model: jav元数据对象
            genres: 特征
        """
        if self._need_nfo:

            # nfo路径
            if self._need_only_cd:  # 如果是为kodi准备的nfo，不需要多cd
                path_nfo = f'{jav_file.Dir}{sep}{jav_file.Name_no_ext.replace(jav_file.Cd, "")}.nfo'
            else:
                path_nfo = f'{jav_file.Dir}{sep}{jav_file.Name_no_ext}.nfo'

            # nfo中tilte的写法
            title_in_nfo = ''
            for i in self._list_name_nfo_title:
                title_in_nfo = f'{title_in_nfo}{self._dict_for_standard[i]}'  # nfo中tilte的写法

            # 简介，用中文还是日语
            plot = replace_xml(jav_model.PlotZh) if self._need_zh_plot else replace_xml(jav_model.Plot)

            # 写入nfo
            f = open(path_nfo, 'w', encoding="utf-8")
            f.write(f'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n'
                    f'<movie>\n'
                    f'  <plot>{plot}{replace_xml(jav_model.Review)}</plot>\n'
                    f'  <title>{title_in_nfo}</title>\n'
                    f'  <originaltitle>{jav_model.Car} {replace_xml(jav_model.Title)}</originaltitle>\n'
                    f'  <director>{replace_xml(jav_model.Director)}</director>\n'
                    f'  <rating>{jav_model.Score / 10}</rating>\n'
                    f'  <criticrating>{jav_model.Score}</criticrating>\n'  # 烂番茄评分 用上面的评分*10
                    f'  <year>{jav_model.Release[0:4]}</year>\n'
                    f'  <mpaa>NC-17</mpaa>\n'
                    f'  <customrating>NC-17</customrating>\n'
                    f'  <countrycode>JP</countrycode>\n'
                    f'  <premiered>{jav_model.Release}</premiered>\n'
                    f'  <release>{jav_model.Release}</release>\n'
                    f'  <runtime>{jav_model.Runtime}</runtime>\n'
                    f'  <country>日本</country>\n'
                    f'  <studio>{replace_xml(jav_model.Studio)}</studio>\n'
                    f'  <id>{jav_model.Car}</id>\n'
                    f'  <num>{jav_model.Car}</num>\n'
                    f'  <set>{replace_xml(jav_model.Series)}</set>\n')  # emby不管set系列，kodi可以
            # 需要将特征写入genre
            if self._need_nfo_genres:
                for i in genres:
                    f.write(f'  <genre>{i}</genre>\n')
                if self._need_series_as_genre and jav_model.Series:
                    f.write(f'  <genre>系列:{jav_model.Series}</genre>\n')
                if self._need_studio_as_genre and jav_model.Studio:
                    f.write(f'  <genre>片商:{jav_model.Studio}</genre>\n')
                for i in self._list_extra_genres:
                    f.write(f'  <genre>{self._dict_for_standard[i]}</genre>\n')
            # 需要将特征写入tag
            if self._need_nfo_tags:
                for i in genres:
                    f.write(f'  <tag>{i}</tag>\n')
                if self._need_series_as_genre and jav_model.Series:
                    f.write(f'  <tag>系列:{jav_model.Series}</tag>\n')
                if self._need_studio_as_genre and jav_model.Studio:
                    f.write(f'  <tag>片商:{jav_model.Studio}</tag>\n')
                for i in self._list_extra_genres:
                    f.write(f'  <tag>{self._dict_for_standard[i]}</tag>\n')
            # 写入演员
            for i in jav_model.Actors:
                f.write(f'  <actor>\n'
                        f'    <name>{i}</name>\n'
                        f'    <type>Actor</type>\n'
                        f'  </actor>\n')
            f.write('</movie>\n')
            f.close()
            print('    >nfo收集完成')

    def download_fanart(self, jav_file: JavFile, jav_model: JavData):
        """
        下载fanart，切割poster

        Args:
            jav_file: jav视频文件对象
            jav_model: jav元数据对象
        """
        if self._need_download_fanart:

            # fanart和poster路径
            path_fanart = f'{jav_file.Dir}{sep}'
            path_poster = f'{jav_file.Dir}{sep}'
            for i in self._list_name_fanart:
                path_fanart = f'{path_fanart}{self._dict_for_standard[i]}'
            for i in self._list_name_poster:
                path_poster = f'{path_poster}{self._dict_for_standard[i]}'

            # kodi只需要一份图片，不管视频是cd几，仅需一份图片，不需要cd几。
            if self._need_only_cd:
                path_fanart = path_fanart.replace(jav_file.Cd, '')  # 去除cd
                path_poster = path_poster.replace(jav_file.Cd, '')

            # emby需要多份，如果现在的视频文件不是cd1（不是第一集），直接复制第一集的图片
            elif jav_file.Episode != 1:
                # 如果用户有例如abc-123.mkv和abc-123.mp4这两个视频，并且用户设置“不重命名视频”（导致没有分cd1、cd2），处理完mkv，
                # 再处理mp4，mp4的fanart路径和mkv相同
                # 引发报错raise SameFileError("{!r} and {!r} are the same file".format(src, dst))
                # 所以这里判断下path_fanart有没有，如果有，就不再搞图片了
                if not os.path.exists(path_fanart):
                    copyfile(path_fanart.replace(jav_file.Cd, '-cd1'), path_fanart)
                    print('    >fanart.jpg复制成功')
                    copyfile(path_poster.replace(jav_file.Cd, '-cd1'), path_poster)
                    print('    >poster.jpg复制成功')

            # 是否已存在可用的fanart
            if check_picture(path_fanart):
                # 这里有个遗留问题，如果已有的图片文件名是小写，比如abc-123 xx.jpg，但现在path_fanart是大写ABC-123，无法改变，poster同样
                # print('    >已有fanart.jpg')
                pass
            else:
                status = False  # 用于判断fanart是否下载成功
                if jav_model.Javdb:
                    # Todo 如果javdb的图片不是规则的
                    url_cover = f'https://jdbimgs.com/covers/{jav_model.Javdb[:2].lower()}/{jav_model.Javdb}.jpg'
                    # print('    >从javdb下载封面: ', url_cover)  # 不希望“某些人”看到是从javdb上下载图片
                    print('    >下载封面: ...')
                    status = download_pic(url_cover, path_fanart, self._proxy_db)
                if not status and jav_model.CoverBus:
                    url_cover = f'{self._url_bus}/pics/cover/{jav_model.CoverBus}'
                    print('    >从javbus下载封面: ', url_cover)
                    status = download_pic(url_cover, path_fanart, self._proxy_bus)
                if not status and jav_model.CoverLibrary:
                    url_cover = jav_model.CoverLibrary
                    print('    >从dmm下载封面: ', url_cover)
                    status = download_pic(url_cover, path_fanart, self._proxy_dmm)
                if status:
                    pass
                else:
                    raise DownloadFanartError

            # 裁剪生成 poster
            if check_picture(path_poster):
                # 这里有个问题，如果用户已有poster了，但没条幅，用户又想加上条幅...无法为用户加上
                # print('    >已有poster.jpg')
                pass
            else:
                crop_poster_youma(path_fanart, path_poster)
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
