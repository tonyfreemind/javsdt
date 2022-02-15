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
