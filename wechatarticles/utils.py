# coding: utf-8
"""
辅助脚本函数
"""
import base64
import html
import os
import re
import time
import glob

from .ArticlesUrls import PC

base_columns = ["url", "title", "date", "headlines"]
custom_columns = ["copyright_stat"]
A_columns = ["read_num", "old_like_num", "like_num"]
B_columns = ["comments_num", "comments_content", "comments_like_num"]
C_columns = ["text_content", "content_num", "pic_num"]
mode_columns = {
    1: A_columns,
    2: B_columns,
    3: C_columns,
    4: A_columns + B_columns,
    5: A_columns + C_columns,
    6: B_columns + C_columns,
    7: A_columns + B_columns + C_columns,
}


# url, readnum likenum
def flatten(x):
    return [y for l in x for y in flatten(l)] if type(x) is list else [x]


def remove_duplicate_json(fname):
    # 删除json中重复的数据
    # fname: xxx.json
    with open(fname, "r", encoding="utf-8") as f:
        data = f.readlines()

    id_re = re.compile(r'datetime": (.+), "fakeid"')
    sort_func = lambda line: id_re.findall(line)[0]

    list_data = list(set(data))
    sort_data = sorted(list_data, key=sort_func)[::-1]

    # sort_data = sorted(list(set_data),
    #                    key=lambda line: re.findall(
    #                        r'datetime": (.+), "fakeid"', line)[0])[::-1]

    with open(fname, "w", encoding="utf-8") as f:
        f.writelines(sort_data)


def merge_duplicate_json():
    f_lst = glob.glob("*.json")
    for fname in f_lst:
        with open(fname, "r", encoding="utf-8") as f:
            data = f.readlines()
        print(fname)
        flag = True
        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                if data[i] == data[j]:
                    flag = False
                    print(i)
                    break
            if flag == False:
                break


def end_func(timestamp, end_timestamp):
    if timestamp < end_timestamp:
        print(timestamp, end_timestamp)
        return True
    return False


def transfer_url(url):
    url = html.unescape(html.unescape(url))
    return eval(repr(url).replace("\\", ""))


def save_f(fname):
    i = 1
    while True:
        if os.path.isfile("{}.json".format(fname)):
            i += 1
            fname += "-" + str(i)
        else:
            break

    return fname


# verify_lst = ["mp.weixin.qq.com", "__biz", "mid", "sn", "idx"]
verify_lst = ["mp.weixin.qq.com", "__biz", "mid", "idx"]


def verify_url(url):
    # 过滤特殊链接
    if "video?" in url or "show?" in url:
        return False
    for string in verify_lst:
        if string not in url:
            return False
    return True


def copyright_num(copyright_stat):
    if copyright_stat == 11:
        return 1  # 标记原创
    else:
        return 0


def copyright_num_detailed(copyright_stat):
    copyright_stat_lst = [14, 12, 201]
    if copyright_stat == 11:
        return 1  # 标记原创
    elif copyright_stat == 100:
        return 0  # 荐号
    elif copyright_stat == 101:
        return 2  # 转发
    elif copyright_stat == 0:
        return 3  # 来源非微信文章
    elif copyright_stat == 1:
        return 4  # 形容词（xxx的公众号）
    elif copyright_stat in copyright_stat_lst:
        return 5
    else:
        return None


def read_nickname(fname):
    # 读取数据
    with open(fname, "r", encoding="utf-8") as f:
        haved_data = f.readlines()
    return [line.split(", ") for line in haved_data]


def get_history_urls(
    biz,
    uin,
    key,
    lst=[],
    start_timestamp=0,
    start_count=10,
    end_count=99999,
    return_flag=False,
):
    """
    获取历史文章链接

    Parameters
    ----------
    biz: str
        公众号id
    uin: str
        个人微信号id
    key: str
        个人微信号key
    lst: list
        已有的数据列表
    start_timestampe: int
        截至时间戳
    start_count: int
        开始的条数
    end_count: int
        截至条数
    return_flag: bool
        是否返回状态信息

    Returns
    -------
    lst:
        获取到的历史文章数据
    """
    t = PC(biz=biz, uin=uin, cookie="")
    flag = True
    try:
        while True:
            res = t.get_urls(key, offset=start_count)
            if res == []:
                break
            start_count += 10
            lst.append(res)
            dt = res[-1]["comm_msg_info"]["datetime"]
            print(start_count, timestamp2date(dt))
            if dt <= start_timestamp or start_count >= end_count:
                break
            time.sleep(5)
    except KeyboardInterrupt as e:
        flag = False
        print("程序手动中断")
    except Exception as e:
        print(e)
        flag = False
        print("获取文章链接失败。。。退出程序")
    finally:
        if return_flag:
            return flag, lst
        return lst


def swap_biz_id(biz=None, fakeid=None):
    if biz == None:
        return str(base64.b64encode(fakeid.encode()), encoding="utf-8")
    if fakeid == None:
        return str(base64.b64decode(biz.encode()), encoding="utf-8")
    return None


# 一些tools，如时间戳转换
def timestamp2date(timestamp, time_format_str="%Y-%m-%d"):
    """
    时间戳转换为日期

    Parameters
    ----------
    timestamp: int or str
        时间戳
        
    time_format_str: str
        转换日期格式, "%Y-%m-%d %H:%M:%S"; "%Y-%m-%d; %Y年%m月%d日%H时%M分%S秒

    Returns
    -------
    datetime:
        转换好的日期：年-月-日 时:分:秒
    """
    time_array = time.localtime(int(timestamp))
    datetime = time.strftime(time_format_str, time_array)
    return datetime
