# coding:  utf-8
import requests
import sqlite3
import json
from requests.cookies import cookielib
import hashlib
import os


class OfficialWeChat(object):
    """
    获取需要爬取的微信公众号的推文链接
    """

    def __init__(self, username=None, password=None, cookie=None, token=None):
        """
        初始化参数
        Parameters
        ----------
        username: str
            用户账号
        password: str
            用户密码
        nickname : str or unicode
            需要爬取公众号名称
        token : str
            登录微信公众号平台之后获取的token
        cookie : str
            登录微信公众号平台之后获取的cookie

        Returns
        -------
            None
        """
        self.s = requests.session()
        self.headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
        }
        self.params = {
            "lang": "zh_CN",
            "f": "json",
        }

        # 两种登录方式
        if (cookie != None) and (token != None):
            self.__verify_str(cookie, "cookie")
            self.__verify_str(token, "token")
            self.headers["Cookie"] = cookie
            self.params["token"] = token
        elif (username != None) and (password != None):
            self.__verify_str(username, "username")
            self.__verify_str(password, "password")
            # 每次登录需要扫码，不支持cookie缓存
            self.__startlogin_official(username, password)
        else:
            print("please check your paramse")
            raise SystemError

    def __verify_str(self, input_string, param):
        """
        验证输入是否为字符串
        Parameters
        ----------
        input_string: str
            输入
        param: str
            需要验证的参数名
        Returns
        ----------
            None
        """
        if not isinstance(input_string, str):
            raise TypeError("{} must be an instance of str".format(param))

    def __save_login_qrcode(self, img):
        """
        存储和显示登录二维码
        Parameters
        ----------
        img: str
            获取到的二维码数据

        Returns
        -------
            None
        """
        import matplotlib.pyplot as plt
        from PIL import Image
        with open("login.png", "wb+") as fp:
            fp.write(img.content)

        img = Image.open("login.png")
        plt.figure()
        plt.imshow(img)
        plt.show()

    def __save_cookie(self, username):
        """
        存储cookies, username用于文件命名
        Parameters
        ----------
        username: str
            用户账号

        Returns
        -------
            None
        """
        #实例化一个LWPcookiejar对象
        new_cookie_jar = cookielib.LWPCookieJar(username + '.txt')

        #将转换成字典格式的RequestsCookieJar（这里我用字典推导手动转的）保存到LWPcookiejar中
        requests.utils.cookiejar_from_dict(
            {c.name: c.value
             for c in self.s.cookies}, new_cookie_jar)

        #保存到本地文件
        new_cookie_jar.save(
            'cookies/' + username + '.txt',
            ignore_discard=True,
            ignore_expires=True)

    def __read_cookie(self, username):
        """
        读取cookies, username用于文件命名
        Parameters
        ----------
        username: str
            用户账号

        Returns
        -------
            None
        """
        #实例化一个LWPCookieJar对象
        load_cookiejar = cookielib.LWPCookieJar()
        #从文件中加载cookies(LWP格式)
        load_cookiejar.load(
            'cookies/' + username + '.txt',
            ignore_discard=True,
            ignore_expires=True)
        #工具方法转换成字典
        load_cookies = requests.utils.dict_from_cookiejar(load_cookiejar)
        #工具方法将字典转换成RequestsCookieJar，赋值给session的cookies.
        self.s.cookies = requests.utils.cookiejar_from_dict(load_cookies)

    def __md5_passwd(self, password):
        """
        明文密码用md5加密
        Parameters
        ----------
        password: str
            未加密的密码

        Returns
        -------
        str：
            加密后的字符串
        """
        m5 = hashlib.md5()
        m5.update(password.encode('utf-8'))
        pwd = m5.hexdigest()
        return pwd

    def __startlogin_official(self, username, password):
        """
        预备登录微信公众号平台获取Cookies
        Parameters
        ----------
        username: str
            用户账号
        password: str
            用户密码
        Returns
        -------
            None
        """

        pwd = self.__md5_passwd(password)
        data = {
            "username": username,
            "userlang": "zh_CN",
            "token": "",
            "pwd": pwd,
            "lang": "zh_CN",
            "imgcode": "",
            "f": "json",
            "ajax": "1"
        }

        self.headers["Host"] = "mp.weixin.qq.com"
        self.headers["Origin"] = "https://mp.weixin.qq.com"
        self.headers["Referer"] = "https://mp.weixin.qq.com/"

        bizlogin_url = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin"
        qrcode_url = "https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=getqrcode&param=4300&rd=928"

        self.s.post(bizlogin_url, headers=self.headers, data=data)
        img = self.s.get(qrcode_url)
        self.__save_login_qrcode(img)

        self.headers.pop("Host")
        self.headers.pop("Origin")
        self.__login_official(username, password)

    def __login_official(self, username, password):
        """
        正式登录微信公众号平台，获取token
        Parameters
        ----------
        username: str
            用户账号
        password: str
            用户密码
        Returns
        -------
            None
        """
        referer = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=validate&lang=zh_CN&account={}".format(
            username)
        self.headers["Referer"] = referer

        data = {
            "userlang": "zh_CN",
            "token": "",
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
        }
        bizlogin_url = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login"
        res = self.s.post(bizlogin_url, data=data, headers=self.headers).json()
        try:
            # 截取token的字符串
            token = res["redirect_url"].split("=")[-1]
            self.params["token"] = token
            self.__save_cookie(username)
            self.headers.pop("Referer")
        except Exception:
            # 获取token失败，重新登录
            print("please try again")
            self.__startlogin_official(username, password)

    def get_official_info(self, nickname, begin="0", count="5"):
        """
        获取公众号的一些信息
        Parameters
        ----------
        begin: str or int
            起始爬取的页数
        count: str or int
            每次爬取的数量，1-5

        Returns
        -------
        json:
            公众号的一些信息
            {
              'alias': 公众号别名,
              'fakeid': 公众号唯一id,
              'nickname': 公众号名称,
              'round_head_img': 公众号头像的url,
              'service_type': 1公众号性质
            }
        """
        self.__verify_str(nickname, "nickname")
        search_url = "https://mp.weixin.qq.com/cgi-bin/searchbiz"
        self.params["query"] = nickname
        self.params["count"] = count
        self.params["action"] = "search_biz"
        self.params["ajax"] = "1"
        self.params["begin"] = begin

        try:
            official = self.s.get(
                search_url, headers=self.headers,
                params=self.params).json()["list"]
            return official[0]
        except Exception:
            return u"公众号名称错误，请重新输入"

    def totalNums(self, nickname):
        """
        获取公众号的总共发布的文章数量
        Parameters
        ----------
        None

        Returns
        -------
        int
            文章总数
        """
        self.__verify_str(nickname, "nickname")
        try:
            return self.__get_articles_data(nickname, begin="0")["app_msg_cnt"]
        except Exception:
            return u"公众号名称错误，请重新输入"

    def get_articles(self, nickname, begin, count="5"):
        """
        获取公众号的每页的文章信息
        Parameters
        ----------
        begin: str or int
            起始爬取的页数
        count: str or int
            每次爬取的数量，1-5

        Returns
        -------
        list:
            由每个文章信息构成的数组
            [
              {
                'aid': '2650949647_1',
                'appmsgid': 2650949647,
                'cover': 封面的url'digest': 文章摘要,
                'itemidx': 1,
                'link': 文章的url,
                'title': 文章标题,
                'update_time': 更新文章的时间戳
              },
            ]
        """
        self.__verify_str(nickname, "nickname")
        try:
            return self.__get_articles_data(
                nickname, begin=str(begin), count=str(count))["app_msg_list"]
        except Exception:
            return u"公众号名称错误，请重新输入"

    def __get_articles_data(self,
                           nickname,
                           begin,
                           count="5",
                           type_="9",
                           action="list_ex"):
        """
        获取公众号文章的一些信息
        Parameters
        ----------
        begin: str or int
            起始爬取的页数
        count: str or int
            每次爬取的数量，1-5
        type_: str or int
            获取数据的方式，暂不知道具体用途
        action: str
            请求之后的行为动作，"list_ex"获取文章信息的json
        Returns
        -------
        json:
            文章信息的json
            {
              'app_msg_cnt': 公众号发文章总数,
              'app_msg_list': 　一个数组(参看GetArticles),
              'base_resp': {
                'err_msg': 'ok',
                'ret': 0
              }
            }
        """
        appmsg_url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        key_lst = ["query", "ajax"]

        official_info = self.get_official_info(nickname)
        if isinstance(official_info, dict):
            self.params["fakeid"] = official_info["fakeid"]
        else:
            return u"公众号名称错误，请重新输入"
        for key in key_lst:
            if key in self.params.keys():
                self.params.pop(key)

        self.params["begin"] = str(begin)
        self.params["count"] = str(count)
        self.params["type"] = str(type_)
        self.params["action"] = action

        data = self.s.get(
            appmsg_url, headers=self.headers, params=self.params).json()
        return data

    def save_txt(self, fname, data):
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
        self.__verify_str(fname, "fname")

        if ".txt" not in fname:
            raise Exception("fname must be txt", fname)
        with open(fname, "a+") as f:
            for item in data:
                f.write(json.dumps(item))
                f.write("\n")

    def __create_db(self, dbname, tablename):
        """
        创建db数据库
        Parameters
        ----------
        dbname: str
            数据库名(文件名)
        tablename: str
            数据库表名
        Returns
        -------
        None
        """
        with sqlite3.connect(dbname) as con:
            # 创建数据库
            with con as cur:
                create_sql = """
                create table {} (aid varchar(16) primary key, \
                    appmsgid varchar(16),cover text,digest text, \
                    itemidx integer,link text, title text, \
                    update_time integer)
                """.format(tablename)
                cur.execute(create_sql)

    def save_sqlite(self, dbname, tablename, data):
        """
        存储数据到sqlite3中
        Parameters
        ----------
        dbname: str
            数据库名(文件名)
        tablename: str
            数据库表名
        data: list
            爬取到的数据
        Returns
        -------
        None
        """
        self.__verify_str(dbname, "dbname")
        self.__verify_str(tablename, "tablename")

        if dbname not in os.listdir(os.getcwd()):
            self.__create_db(dbname, tablename)
        with sqlite3.connect(dbname) as con:
            # 插入数据
            with con as cur:
                for item in data:
                    try:
                        cur.execute(
                            "insert into {} values (?, ?, ?, ?, ?, ?, ?, ?)".
                            format(tablename), list(item.values()))
                    except Exception:
                        print("please check data")

    def save_mongo(self,
                   data,
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

        host = HOST if host is None else host
        port = PORT if port is None else port
        self.__verify_str(host, "host")
        if not isinstance(port, int):
            raise TypeError("port must be an instance of int")
        self.__verify_str(name, "name")
        self.__verify_str(password, "password")
        self.__verify_str(collname, "collname")

        from pymongo import MongoClient
        client = MongoClient(host, port)
        db_auth = client.admin
        db_auth.authenticate(name, password)
        coll = client[dbname][collname]
        coll.insert_many(data)
