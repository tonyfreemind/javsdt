import os
from os import sep
import Config
from Classes.MyLogger import record_video_old
from Classes.Errors import TooManyDirectoryLevelsError, DownloadFanartError
from Const import Const
from Functions.Utils.Download import download_pic
from configparser import RawConfigParser  # 读取ini
from configparser import NoOptionError  # ini文件不存在或不存在指定node的错误
from shutil import copyfile
from Functions.Progress.Picture import check_picture, crop_poster_youma, add_watermark_subtitle, add_watermark_divulge
from Functions.Utils.XML import replace_xml_win, replace_xml
from Model.JavData import JavData
from Model.JavFile import JavFile


class StandardHandler(object):
    def __init__(self, ini: Config.Ini):
        self._bool_need_actors_end_of_title = ini.need_actors_end_of_title
        self._int_title_len = ini.int_title_len
        # 用于给用户自定义命名的字典
        self._dict_for_standard = ini.dict_for_standard()
        self._subtitle_expression = ini.subtitle_expression
        self._divulge_expression = ini.divulge_expression
        self._need_rename_video = ini.need_rename_video
        self._list_name_video = ini.list_name_video
        self._need_rename_subtitle = ini.need_rename_subtitle
        self._need_classify = ini.need_classify
        self._need_classify_folder = ini.need_classify_folder
        self._dir_custom_classify_target = ini.dir_custom_classify_target
        self._list_name_dir_classify = ini.list_name_dir_classify
        self._need_rename_folder = ini.need_rename_folder
        self._list_name_folder = ini.list_name_folder
        self._bool_sculpture =ini.need_actor_sculpture

        # 定义 Windows中的非法字符, 将非法字符替换为空格
        self.winDic = str.maketrans(r':<>"\?/*', '        ')

    # jav_file: jav视频文件对象
    # jav_data: jav元数据对象
    def prefect_dict_for_standard(self, jav_file: JavFile, jav_data: JavData):
        """用jav_file、jav_model中的原始数据完善dict_for_standard\n
        Args:
            jav_file: jav视频文件对象
            jav_data: jav元数据对象
        Returns:
            void; 更新self._dict_for_standard
        """
        # 标题
        str_actors = ' '.join(jav_data.Actors[:3])
        int_actors_len = len(str_actors) if self._bool_need_actors_end_of_title else 0
        int_current_len = self._int_title_len - int_actors_len  # 限制标题长 - 末尾可能存在的演员文字长 = 实际限制的标题长
        self._dict_for_standard['完整标题'] = replace_xml_win(jav_data.Title)
        self._dict_for_standard['中文完整标题'] = replace_xml_win(jav_data.TitleZh) \
            if jav_data.TitleZh else self._dict_for_standard['完整标题']
        # 处理影片的标题过长。文件重命名操作中的“标题“是删减过的标题，nfo中的标题才是“完整标题”，而用户只需要在ini中写“标题”
        if len(self._dict_for_standard['完整标题']) > int_current_len:
            self._dict_for_standard['标题'] = self._dict_for_standard['完整标题'][:int_current_len]
        else:
            self._dict_for_standard['标题'] = self._dict_for_standard['完整标题']
        if len(self._dict_for_standard['中文完整标题']) > int_current_len:
            self._dict_for_standard['中文标题'] = self._dict_for_standard['中文完整标题'][:int_current_len]
        else:
            self._dict_for_standard['中文标题'] = self._dict_for_standard['中文完整标题']
        if self._bool_need_actors_end_of_title:
            self._dict_for_standard['标题'] = f'{self._dict_for_standard["标题"]} {str_actors}'
            self._dict_for_standard['完整标题'] += f'{self._dict_for_standard["完整标题"]} {str_actors}'
            self._dict_for_standard['中文标题'] += f'{self._dict_for_standard["中文标题"]} {str_actors}'
            self._dict_for_standard['中文完整标题'] += f'{self._dict_for_standard["中文完整标题"]} {str_actors}'

        # '是否中字'这一命名元素被激活
        self._dict_for_standard['是否中字'] = self._subtitle_expression if jav_file.Bool_subtitle else ''
        self._dict_for_standard['是否流出'] = self._divulge_expression if jav_file.Bool_divulge else ''
        # 车牌
        self._dict_for_standard['车牌'] = jav_data.Car  # car可能发生了变化
        self._dict_for_standard['车牌前缀'] = jav_data.Car.split('-')[0]
        # 日期
        self._dict_for_standard['发行年月日'] = jav_data.Release
        self._dict_for_standard['发行年份'] = jav_data.Release[0:4]
        self._dict_for_standard['月'] = jav_data.Release[5:7]
        self._dict_for_standard['日'] = jav_data.Release[8:10]
        # 演职人员
        self._dict_for_standard['片长'] = jav_data.Runtime
        self._dict_for_standard['导演'] = replace_xml_win(jav_data.Director) if jav_data.Director else '有码导演'
        # 公司
        self._dict_for_standard['发行商'] = replace_xml_win(jav_data.Publisher) if jav_data.Publisher else '有码发行商'
        self._dict_for_standard['制作商'] = replace_xml_win(jav_data.Studio) if jav_data.Studio else '有码制作商'
        # 评分 系列
        self._dict_for_standard['评分'] = jav_data.Score / 10
        self._dict_for_standard['系列'] = jav_data.Series if jav_data.Series else '有码系列'
        # 全部演员（最多7个） 和 第一个演员
        if jav_data.Actors:
            if len(jav_data.Actors) > 7:
                self._dict_for_standard['全部演员'] = ' '.join(jav_data.Actors[:7])
            else:
                self._dict_for_standard['全部演员'] = ' '.join(jav_data.Actors)
            self._dict_for_standard['首个演员'] = jav_data.Actors[0]
        else:
            self._dict_for_standard['首个演员'] = self._dict_for_standard['全部演员'] = '有码演员'

        # jav_file原文件的一些属性   dict_for_standard['视频']，先定义为原文件名，即将发生变化。
        self._dict_for_standard['视频'] = self._dict_for_standard['原文件名'] = jav_file.Name_no_ext
        self._dict_for_standard['原文件夹名'] = jav_file.Folder

    def rename_mp4(self, jav_file: JavFile):
        """重命名磁盘中的视频文件\n
        Args:
            jav_file: jav视频文件对象
        Returns:
            path_return 如果重命名为新文件名不成功，将新文件名路径告知用户，提醒用户自行重命名；如果成功，则为空。
        """
        # 如果重命名操作不成功，将path_new赋值给path_return，提醒用户自行重命名
        path_return = ''
        if self._need_rename_video:
            # 构造新文件名，不带文件类型后缀
            name_without_ext = ''
            for j in self._list_name_video:
                name_without_ext = f'{name_without_ext}{self._dict_for_standard[j]}'
            if os.name == 'nt':  # 如果是windows系统
                name_without_ext = name_without_ext.translate(self.winDic)  # 将文件名中的非法字符替换为空格
            name_without_ext = f'{name_without_ext.strip()}{jav_file.Cd}'  # 去除末尾空格，否则windows会自动删除空格，导致程序仍以为带空格
            path_new = f'{jav_file.Dir}{sep}{name_without_ext}{jav_file.Ext}'  # 【临时变量】path_new 视频文件的新路径

            # 一般情况，不存在同名视频文件
            if not os.path.exists(path_new):
                os.rename(jav_file.Path, path_new)
                record_video_old(jav_file.Path, path_new)
            # 已存在目标文件，但就是现在的文件
            elif jav_file.Path.upper() == path_new.upper():
                try:
                    os.rename(jav_file.Path, path_new)
                # windows本地磁盘，“abc-123.mp4”重命名为“abc-123.mp4”或“ABC-123.mp4”没问题，但有用户反映，挂载的磁盘会报错“file exists error”
                except FileExistsError:
                    # 提醒用户后续自行更改
                    path_return = path_new
            # 存在目标文件，不是现在的文件。
            else:
                raise FileExistsError(f'重命名影片失败，重复的影片，已经有相同文件名的视频了: {path_new}')  # 【终止对该jav的整理】
            self._dict_for_standard['视频'] = name_without_ext  # 【更新】 dict_for_standard['视频']
            jav_file.Name = f'{name_without_ext}{jav_file.Ext}'  # 【更新】jav.name，重命名操作可能不成功，但之后的操作仍然围绕成功的jav.name来命名
            print(f'    >修改文件名{jav_file.Cd}完成')
            # 重命名字幕
            if jav_file.Subtitle and self._need_rename_subtitle:
                subtitle_new = f'{name_without_ext}{jav_file.Ext_subtitle}'  # 【临时变量】subtitle_new
                path_subtitle_new = f'{jav_file.Dir}{sep}{subtitle_new}'  # 【临时变量】path_subtitle_new
                if jav_file.Path_subtitle != path_subtitle_new:
                    os.rename(jav_file.Path_subtitle, path_subtitle_new)
                    jav_file.Subtitle = subtitle_new  # 【更新】 jav.subtitle 字幕完整文件名
                print('    >修改字幕名完成')
        return path_return

    def classify_files(self, jav_file: JavFile):
        """2归类影片，只针对视频文件和字幕文件，无视它们当前所在文件夹\n
        Args:
            jav_file: jav视频文件对象
        Returns:
            void
        """
        # 如果需要归类，且不是针对文件夹来归类
        if self._need_classify and not self._need_classify_folder:
            # 移动的目标文件夹路径
            dir_dest = f'{self._dir_custom_classify_target}{sep}'
            for j in self._list_name_dir_classify:
                # 【临时变量】归类的目标文件夹路径    C:\Users\JuneRain\Desktop\测试文件夹\葵司\
                dir_dest = f'{dir_dest}{self._dict_for_standard[j].strip()}'
            # 还不存在该文件夹，新建
            if not os.path.exists(dir_dest):
                os.makedirs(dir_dest)
            path_new = f'{dir_dest}{sep}{jav_file.Name}'  # 【临时变量】新的影片路径
            # 目标文件夹没有相同的影片，防止用户已经有一个“avop-127.mp4”，现在又来一个
            if not os.path.exists(path_new):
                os.rename(jav_file.Path, path_new)
                print('    >归类视频文件完成')
                # 移动字幕
                if jav_file.Subtitle:
                    path_subtitle_new = f'{dir_dest}{sep}{jav_file.Subtitle}'  # 【临时变量】新的字幕路径
                    if jav_file.Path_subtitle != path_subtitle_new:
                        os.rename(jav_file.Path_subtitle, path_subtitle_new)
                    print('    >归类字幕文件完成')
                jav_file.Dir = dir_dest  # 【更新】jav.dir
            else:
                raise FileExistsError(f'归类失败，重复的影片，归类的目标文件夹已经存在相同的影片: {path_new}')  # 【终止对该jav的整理】

    def rename_folder(self, jav_file: JavFile):
        """ 3重命名文件夹或创建独立文件夹\n
        如果已进行第2操作，第3操作不会进行，因为用户只需要归类视频文件，不需要管文件夹。\n
        Args:
            jav_file: jav元数据对象
        Returns:
            void; 更新jav_file.Dir
        """
        if self._need_rename_folder:
            # 构造 新文件夹名folder_new
            folder_new = ''
            for j in self._list_name_folder:
                folder_new = f'{folder_new}{self._dict_for_standard[j]}'
            folder_new = folder_new.rstrip(' .')  # 【临时变量】新的所在文件夹。去除末尾空格和“.”
            # 是独立文件夹，才会重命名文件夹
            if jav_file.Bool_in_separate_folder:
                # 当前视频是该车牌的最后一集，他的兄弟姐妹已经处理完成，才会重命名它们的“家”。
                if jav_file.Episode == jav_file.Sum_all_episodes:
                    dir_new = f'{os.path.dirname(jav_file.Dir)}{sep}{folder_new}'  # 【临时变量】新的影片所在文件夹路径。
                    # 想要重命名的目标影片文件夹不存在
                    if not os.path.exists(dir_new):
                        os.rename(jav_file.Dir, dir_new)
                        jav_file.Dir = dir_new  # 【更新】jav.dir
                    # 目标影片文件夹存在，但就是现在的文件夹，即新旧相同
                    elif jav_file.Dir == dir_new:
                        pass
                    # 真的有一个同名的文件夹了
                    else:
                        raise FileExistsError(f'重命名文件夹失败，已存在相同文件夹: {dir_new}')  # 【终止对该jav的整理】
                    print('    >重命名文件夹完成')
            # 不是独立的文件夹，建立独立的文件夹
            else:
                path_separate_folder = f'{jav_file.Dir}{sep}{folder_new}'  # 【临时变量】需要创建的的影片所在文件夹。
                # 确认没有同名文件夹
                if not os.path.exists(path_separate_folder):
                    os.makedirs(path_separate_folder)
                path_new = f'{path_separate_folder}{sep}{jav_file.Name}'  # 【临时变量】新的影片路径
                # 如果这个文件夹是现成的，在它内部确认有没有“abc-123.mp4”。
                if not os.path.exists(path_new):
                    os.rename(jav_file.Path, path_new)
                    print('    >移动到独立文件夹完成')
                    # 移动字幕
                    if jav_file.Subtitle:
                        path_subtitle_new = f'{path_separate_folder}{sep}{jav_file.Subtitle}'  # 【临时变量】新的字幕路径
                        os.rename(jav_file.Path_subtitle, path_subtitle_new)
                        # 后续不会操作 字幕文件 了，jav.path_subtitle不再更新
                        print('    >移动字幕到独立文件夹')
                    jav_file.Dir = path_separate_folder  # 【更新】jav.dir
                # 里面已有“avop-127.mp4”，这不是它的家。
                else:
                    raise FileExistsError(f'创建独立文件夹失败，已存在相同的视频文件: {path_new}')  # 【终止对该jav的整理】

    def collect_sculpture(self, jav_file: JavFile, jav_data: JavData):
        """6为当前jav收集演员头像到“.actors”文件夹中\n
        Args:
            jav_file: jav视频文件对象
            jav_data: jav元数据对象
        Returns:
            void;
        """
        if self._bool_sculpture and jav_file.Episode == 1:
            if not jav_data.Actors:
                print('    >未知演员，无法收集头像')
            else:
                for each_actor in jav_data.Actors:
                    path_exist_actor = f'演员头像{sep}{each_actor[0]}{sep}{each_actor}'  # 事先准备好的演员头像路径
                    if os.path.exists(f'{path_exist_actor}.jpg'):
                        pic_type = '.jpg'
                    elif os.path.exists(f'{path_exist_actor}.png'):
                        pic_type = '.png'
                    else:
                        config_actor = RawConfigParser()
                        config_actor.read(Const.ini_actor, encoding='utf-8-sig')
                        try:
                            each_actor_times = config_actor.get(Const.node_no_actor, each_actor)
                            config_actor.set(Const.node_no_actor, each_actor, str(int(each_actor_times) + 1))
                        except NoOptionError:
                            config_actor.set(Const.node_no_actor, each_actor, '1')
                        config_actor.write(open(Const.ini_actor, "w", encoding='utf-8-sig'))
                        continue
                    # 已经收录了这个演员头像
                    dir_dest_actor = f'{jav_file.Dir}{sep}.actors{sep}'  # 头像的目标文件夹
                    if not os.path.exists(dir_dest_actor):
                        os.makedirs(dir_dest_actor)
                    # 复制一份到“.actors”
                    copyfile(f'{path_exist_actor}{pic_type}', f'{dir_dest_actor}{each_actor}{pic_type}')
                    print('    >演员头像收集完成: ', each_actor)

    # 功能:
    # 参数: jav_file 处理的jav视频文件对象
    # 返回: 处理的影片jav（所在文件夹路径改变）
    # 辅助: os.exists, os.rename, os.makedirs，
    def classify_folder(self, jav_file):
        """7归类影片，针对文件夹\n
        （如果已进行第2操作，第7操作不会进行，因为用户只需要归类视频文件，不需要管文件夹）
        Args:
            jav_file:

        Returns:

        """
        # 需要移动文件夹，且，是该影片的最后一集
        if self._need_classify and self._need_classify_folder and jav_file.Episode == jav_file.Sum_all_episodes:
            # 用户选择的文件夹是一部影片的独立文件夹，为了避免在这个文件夹里又生成新的归类文件夹
            if jav_file.Bool_in_separate_folder and self._dir_custom_classify_target.startswith(jav_file.Dir):
                raise TooManyDirectoryLevelsError(f'无法归类，不建议在当前文件夹内再新建文件夹')
            # 归类放置的目标文件夹
            dir_dest = f'{self._dir_custom_classify_target}{sep}'
            # 移动的目标文件夹
            for j in self._list_name_dir_classify:
                # 【临时变量】 文件夹移动的目标上级文件夹  C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
                dir_dest = f'{dir_dest}{self._dict_for_standard[j].rstrip(" .")}'
            # 【临时变量】 文件夹移动的目标路径   C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\【葵司】AVOP-127\
            dir_new = f'{dir_dest}{sep}{jav_file.Folder}'
            # print(dir_new)
            # 还不存在归类的目标文件夹
            if not os.path.exists(dir_new):
                os.makedirs(dir_new)
                # 把现在文件夹里的东西都搬过去
                jav_files = os.listdir(jav_file.Dir)
                for i in jav_files:
                    os.rename(f'{jav_file.Dir}{sep}{i}', f'{dir_new}{sep}{i}')
                # 删除“旧房子”，这是javsdt唯一的删除操作，而且os.rmdir只能删除空文件夹
                os.rmdir(jav_file.Dir)
                print('    >归类文件夹完成')
            # 用户已经有了这个文件夹，可能以前处理过同车牌的视频
            else:
                raise FileExistsError(f'归类失败，归类的目标位置已存在相同文件夹: {dir_new}')

    # 功能: 写nfo
    # 参数: jav_file 处理的jav视频文件对象，jav_model 保存jav元数据的对象，genres
    # 返回: 素人车牌list
    # 辅助: 无
    def write_nfo(self, jav_file, jav_model, genres):
        if self._bool_nfo:
            # 如果是为kodi准备的nfo，不需要多cd
            if self._bool_cd_only:
                path_nfo = f'{jav_file.Dir}{sep}{jav_file.Name_no_ext.replace(jav_file.Cd, "")}.nfo'
            else:
                path_nfo = f'{jav_file.Dir}{sep}{jav_file.Name_no_ext}.nfo'
            # nfo中tilte的写法
            title_in_nfo = ''
            for i in self._list_name_nfo_title:
                title_in_nfo = f'{title_in_nfo}{self._dict_for_standard[i]}'  # nfo中tilte的写法
            # 开始写入nfo，这nfo格式是参考的kodi的nfo
            plot = replace_xml(jav_model.PlotZh) if self._bool_need_zh_plot else replace_xml(jav_model.Plot)
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
            if self._bool_genre:
                for i in genres:
                    f.write(f'  <genre>{i}</genre>\n')
                if self._bool_write_series and jav_model.Series:
                    f.write(f'  <genre>系列:{jav_model.Series}</genre>\n')
                if self._bool_write_studio and jav_model.Studio:
                    f.write(f'  <genre>片商:{jav_model.Studio}</genre>\n')
                for i in self._list_extra_genres:
                    f.write(f'  <genre>{self._dict_for_standard[i]}</genre>\n')
            # 需要将特征写入tag
            if self._bool_tag:
                for i in genres:
                    f.write(f'  <tag>{i}</tag>\n')
                if self._bool_write_series and jav_model.Series:
                    f.write(f'  <tag>系列:{jav_model.Series}</tag>\n')
                if self._bool_write_studio and jav_model.Studio:
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

    def download_fanart(self, jav_file, jav_model):
        if self._bool_jpg:
            # fanart和poster路径
            path_fanart = f'{jav_file.Dir}{sep}'
            path_poster = f'{jav_file.Dir}{sep}'
            for i in self._list_name_fanart:
                path_fanart = f'{path_fanart}{self._dict_for_standard[i]}'
            for i in self._list_name_poster:
                path_poster = f'{path_poster}{self._dict_for_standard[i]}'
            # kodi只需要一份图片，不管视频是cd几，图片仅一份不需要cd几。
            if self._bool_cd_only:
                path_fanart = path_fanart.replace(jav_file.Cd, '')
                path_poster = path_poster.replace(jav_file.Cd, '')
            # emby需要多份，现在不是第一集，直接复制第一集的图片
            elif jav_file.Episode != 1:
                # 如果用户不重名视频，并且用户的原视频是第二集，没有带cd2，例如abc-123.mkv和abc-123.mp4，
                # 会导致fanart路径和cd1相同，引发报错raise SameFileError("{!r} and {!r} are the same file".format(src, dst))
                # 所以这里判断下path_fanart有没有
                if not os.path.exists(path_fanart):
                    copyfile(path_fanart.replace(jav_file.Cd, '-cd1'), path_fanart)
                    print('    >fanart.jpg复制成功')
                    copyfile(path_poster.replace(jav_file.Cd, '-cd1'), path_poster)
                    print('    >poster.jpg复制成功')
            # kodi或者emby需要的第一份图片
            if check_picture(path_fanart):
                # 这里有个遗留问题，如果已有的图片文件名是小写，比如abc-123 xx.jpg，现在path_fanart是大写ABC-123，无法改变，poster同理
                # print('    >已有fanart.jpg')
                pass
            else:
                status = False
                if jav_model.Javdb:
                    url_cover = f'https://jdbimgs.com/covers/{jav_model.Javdb[:2].lower()}/{jav_model.Javdb}.jpg'
                    # print('    >从javdb下载封面: ', url_cover)
                    print('    >下载封面: ...')
                    status = download_pic(url_cover, path_fanart, self.proxy_db)
                if not status and jav_model.CoverBus:
                    url_cover = f'{self.url_bus}/pics/cover/{jav_model.CoverBus}'
                    print('    >从javbus下载封面: ', url_cover)
                    status = download_pic(url_cover, path_fanart, self.proxy_bus)
                if not status and jav_model.CoverLibrary:
                    url_cover = jav_model.CoverLibrary
                    print('    >从dmm下载封面: ', url_cover)
                    status = download_pic(url_cover, path_fanart, self.proxy_dmm)
                if status:
                    pass
                else:
                    raise DownloadFanartError
            # 裁剪生成 poster
            if check_picture(path_poster):
                # print('    >已有poster.jpg')
                pass
            else:
                crop_poster_youma(path_fanart, path_poster)
                # 需要加上条纹
                if self._bool_watermark_subtitle and jav_file.Bool_subtitle:
                    add_watermark_subtitle(path_poster)
                if self._bool_watermark_divulge and jav_file.Bool_divulge:
                    add_watermark_divulge(path_poster)

    # 功能: 如果需要为kodi整理头像，则先检查“演员头像for kodi.ini”、“演员头像”文件夹是否存在; 检查 归类根目录 的合法性
    # 参数: 是否需要整理头像，用户自定义的归类根目录，用户选择整理的文件夹路径
    # 返回: 归类根目录路径
    # 辅助: os.sep，os.path.exists，shutil.copyfile
    def check_actors(self):
        # 检查头像: 如果需要为kodi整理头像，先检查演员头像ini、头像文件夹是否存在。
        if self._bool_sculpture:
            if not os.path.exists('演员头像'):
                input('\n“演员头像”文件夹丢失！请把它放进exe的文件夹中！\n')
            if not os.path.exists(Const.ini_actor):
                if os.path.exists('actors_for_kodi.ini'):
                    copyfile('actors_for_kodi.ini', Const.ini_actor)
                    print(f'\n“{Const.ini_actor}”成功！')
                else:
                    input('\n请打开“【ini】重新创建ini.exe”创建丢失的程序组件!')
