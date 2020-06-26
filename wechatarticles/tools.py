# coding: utf-8

import time
import json


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

def save_mongo(data,
                host=None,
                port=None,
                name=None,
                password="",
                dbname=None,
                collname=None):
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
