from configparser import RawConfigParser, NoOptionError


def convert_2dlist_to_dict(list_src: list):
    """
    将二维list转换为字典

    例如将[['1', 'A'],['2', 'B']]转换为{'1': 'A', '2': 'B'}

    Args:
        list_src: 原list

    Returns:
        目标字典
    """
    return {list_sub[0]: list_sub[1] for list_sub in list_src}


def cut_str(src: str, len_limit: int):
    """
    从原字符串中切出[:len_limit]限制长的新字符串

    Args:
        src: 原字符串
        len_limit: 限制长度

    Returns:
        新字符串
    """
    return src[:len_limit] if len(src) > len_limit else src


def update_ini_file_value(ini_file: str, section: str, option: str, value: str):
    """
    在ini中写入新的内容

    Args:
        ini_file: ini文件
        section: 节点
        option: 键
        value: 值
    """
    conf = RawConfigParser()
    conf.read(ini_file, encoding='utf-8-sig')
    conf.set(section, option, value)
    conf.write(open(ini_file, "w", encoding='utf-8-sig'))
    print(f'    >保存新的{option}至{ini_file}成功！')


def update_ini_file_value_plus_one(ini_file: str, section: str, option: str):
    """
    给ini指定的某一项的值加上1

    Args:
        ini_file: ini文件
        section: 节点
        option: 键
    """
    ini = RawConfigParser()
    ini.read(ini_file, encoding='utf-8-sig')
    try:
        current_number = ini.get(section, option)
        ini.set(section, option, str(int(current_number) + 1))
    except NoOptionError:
        ini.set(section, option, '1')
    ini.write(open(ini_file, "w", encoding='utf-8-sig'))
