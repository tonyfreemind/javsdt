def convert_2dlist_to_dict(list_src: list):
    """
    将二维list转换为字典

    例如将[['1', 'A'],['2', 'B']]转换为{'1': 'A', '2': 'B'}

    Args:
        list_src: 原list

    Returns:
        目标字典
    """
    dict_dest = {}
    for list_sub in list_src:
        dict_dest[list_sub[0]] = list_sub[1]
    return dict_dest


def cut_str(src: str, len_limit: int):
    """
    从原字符串中切出限制长的新字符串

    Args:
        src: 原字符串
        len_limit: 限制长度

    Returns:
        新字符串
    """
    if len(src) > len_limit:
        target = src[:len_limit]
    else:
        target = src
    return target
