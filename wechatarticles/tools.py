# coding: utf-8

import time
import urllib


class tools(object):
    """
    一些tools，如时间戳转换
    """

    def __init__(self):
        """
        不需要额外的参数
        Parameters
        ----------
        None

        Returns
        -------
            None
        """
        pass

    @staticmethod
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

    @staticmethod
    def verify_str(input_string, param_name):
        """
        验证输入是否为字符串
        Parameters
        ----------
        input_string: str
            输入
        param_name: str
            需要验证的参数名
        Returns
        ----------
            None
        """
        if not isinstance(input_string, str):
            raise TypeError("{} must be an instance of str".format(param_name))

    @staticmethod
    def save_mongo(data,
                   host=None,
                   port=None,
                   name=None,
                   password=None,
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
        verify_str(host, "host")
        if not isinstance(port, int):
            raise TypeError("port must be an instance of int")
        verify_str(name, "name")
        verify_str(password, "password")
        verify_str(collname, "collname")

        from pymongo import MongoClient
        # 连接数据库，一次性插入数据
        client = MongoClient(host, port)
        db_auth = client.admin
        db_auth.authenticate(name, password)
        coll = client[dbname][collname]
        coll.insert_many(data)

    @staticmethod
    def save_txt(fname, data):
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
        verify_str(fname, "fname")

        if ".txt" not in fname:
            raise Exception("fname must be txt", fname)
        with open(fname, "a+") as f:
            for item in data:
                f.write(json.dumps(item))
                f.write("\n")


def response(flow):
    """
    mitmdumps调用的脚本函数
    如果请求中包含需要的请求流，就在保存后终止运行
    Parameters
    ----------
    flow: http.HTTPFlow
        请求流, 通过命令调用
    
    Returns
    -------
        None
    """
    from mitmproxy import http

    url = urllib.parse.unquote(flow.request.url)
    if "mp.weixin.qq.com/mp/getappmsgext" in url:
        exit()
