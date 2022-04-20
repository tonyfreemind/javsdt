from time import strftime, localtime, time


def time_now():
    """2011-11-11 11:11:11"""
    return strftime("%Y-%m-%d %H:%M:%S", localtime(time()))
