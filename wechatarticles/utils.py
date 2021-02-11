# coding: utf-8
"""
辅助脚本函数
"""
import base64
import html
import json
import os
import re
import time

import requests

from .ArticlesUrls import PC

base_columns = ["url", "title", "date", "headlines", "copyright"]
A_columns = ["read_num", "old_like_num", "like_num"]
B_columns = ["comments_num", "comments_content", "comments_like_num"]
C_columns = ["content", "content_num", "pic_num"]
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


def verify_url(article_url):
    for string in verify_lst:
        if string not in article_url:
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
    biz, uin, key, lst=[], start_timestamp=0, count=10, endcount=99999
):
    t = PC(biz=biz, uin=uin, cookie="")
    try:
        while True:
            res = t.get_urls(key, offset=count)
            if res == []:
                break
            count += 10
            print(count)
            lst.append(res)
            dt = res[-1]["comm_msg_info"]["datetime"]
            if dt <= start_timestamp or count >= endcount:
                break
            time.sleep(5)
    except KeyboardInterrupt as e:
        print("程序手动中断")
        return lst
    except Exception as e:
        print(e)
        print("获取文章链接失败。。。退出程序")
        assert 1 == 2
    finally:
        return lst


def swap_biz_id(biz=None, fakeid=None):
    if biz == None:
        return str(base64.b64encode(fakeid.encode()), encoding="utf-8")
    if fakeid == None:
        return str(base64.b64decode(biz.encode()), encoding="utf-8")
    return None


# 一些tools，如时间戳转换
def timestamp2date(timestamp):
    """
    时间戳转换为日期

    Parameters
    ----------
    timestamp: int or str
        用户账号

    Returns
    -------
    datetime:
        转换好的日期：年-月-日 时:分:秒
    """
    time_array = time.localtime(int(timestamp))
    datetime = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return datetime


def save_mongo(
    data, host=None, port=None, name=None, password="", dbname=None, collname=None
):
    """
    存储数据到mongo

    Parameters
    ----------
    data: list
        需要插入的数据
    host: str
        主机名(默认为本机数据库)
    port: int
        mongo所在主机开放的端口，默认为27017
    username: str
        用户名
    password: str
        用户密码
    dbname: str
        远程连接的数据库名
    collname: str
        需要插入的集合名(collection)
    Returns
    -------
    None
    """
    HOST = "localhost"
    PORT = 27017

    # 检查参数
    host = HOST if host is None else host
    port = PORT if port is None else port

    assert isinstance(host, str)
    assert isinstance(name, str)
    assert isinstance(password, str)
    assert isinstance(dbname, str)
    assert isinstance(collname, str)

    if not isinstance(port, int):
        raise TypeError("port must be an instance of int")

    from pymongo import MongoClient

    # 连接数据库，一次性插入数据
    client = MongoClient(host, port)
    db_auth = client.admin
    db_auth.authenticate(name, password)
    coll = client[dbname][collname]
    coll.insert_many(data)


def save_json(fname, data):
    """
    保存数据为txt格式

    Parameters
    ----------
    fname: str
        保存为txt文件名
    data: list
        爬取到的数据
    Returns
    -------
    None
    """
    assert isinstance(fname, str)

    if ".json" not in fname:
        raise IOError("fname must be json", fname)
    with open(fname, "a+") as f:
        for item in data:
            f.write(json.dumps(item))
            f.write("\n")
