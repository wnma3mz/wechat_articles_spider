# coding:  utf-8
import hashlib
import os

import requests
from requests.cookies import cookielib


class ArticlesUrls(object):
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

        # 手动输入cookie和token登录
        if (cookie != None) and (token != None):
            self.__verify_str(cookie, "cookie")
            self.__verify_str(token, "token")
            self.headers["Cookie"] = cookie
            self.params["token"] = token
        # 扫描二维码登录
        elif (username != None) and (password != None):
            self.__verify_str(username, "username")
            self.__verify_str(password, "password")
            # 暂不支持cookie缓存
            self.__startlogin_official(username, password)
        else:
            print("please check your paramse")
            raise SystemError

    def __verify_str(self, input_string, param_name):
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
        # 存储二维码
        with open("login.png", "wb+") as fp:
            fp.write(img.content)
        # 显示二维码， 这里使用plt的原因是： 等待用户扫描完之后手动关闭窗口继续运行；否则会直接运行
        try:
            img = Image.open("login.png")
        except Exception:
            raise TypeError(u"账号密码输入错误，请重新输入")
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
        new_cookie_jar.save('cookies/' + username + '.txt',
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
        load_cookiejar.load('cookies/' + username + '.txt',
                            ignore_discard=True,
                            ignore_expires=True)
        #工具方法转换成字典
        load_cookies = requests.utils.dict_from_cookiejar(load_cookiejar)
        #工具方法将字典转换成RequestsCookieJar，赋值给session的cookies.
        self.s.cookies = requests.utils.cookiejar_from_dict(load_cookies)

    def __md5_passwd(self, password):
        """
        微信公众号的登录密码需要用md5方式进行加密
        Parameters
        ----------
        password: str
            加密前的字符串

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
        开始登录微信公众号平台，获取Cookies
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
        # 进行md5加密，一些post的参数
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

        # 增加headers的keys
        self.headers["Host"] = "mp.weixin.qq.com"
        self.headers["Origin"] = "https://mp.weixin.qq.com"
        self.headers["Referer"] = "https://mp.weixin.qq.com/"

        # 账号密码post的url
        bizlogin_url = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin"
        # 获取二维码的url
        qrcode_url = "https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=getqrcode&param=4300&rd=928"

        # 账号密码登录，获取二维码，等待用户扫描二维码，需手动关闭二维码窗口
        self.s.post(bizlogin_url, headers=self.headers, data=data)
        img = self.s.get(qrcode_url)
        self.__save_login_qrcode(img)

        # 去除之后不用的headers的key
        self.headers.pop("Host")
        self.headers.pop("Origin")
        # 获取token
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
        # 设定headers的referer的请求
        referer = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=validate&lang=zh_CN&account={}".format(
            username)
        self.headers["Referer"] = referer

        # 获取token的data
        data = {
            "userlang": "zh_CN",
            "token": "",
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
        }
        # 获取token的url
        bizlogin_url = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login"
        res = self.s.post(bizlogin_url, data=data, headers=self.headers).json()

        try:
            # 截取字符串中的token参数
            token = res["redirect_url"].split("=")[-1]
            self.params["token"] = token
            # self.__save_cookie(username)
            self.headers.pop("Referer")
        except Exception:
            # 获取token失败，重新扫码登录
            print("please try again")
            self.__startlogin_official(username, password)

    def official_info(self, nickname, begin=0, count=5):
        """
        根据关键词返回相关公众号的信息
        Parameters
        ----------
        nickname : str
            需要爬取公众号名称
        begin: str or int
            起始爬取的页数
        count: str or int
            每次爬取的数量，1-5

        Returns
        -------
        list:
            相关公众号的对应信息
            [
                {
                'alias': 公众号别名,
                'fakeid': 公众号唯一id,
                'nickname': 公众号名称,
                'round_head_img': 公众号头像的url,
                'service_type': 1公众号性质
                },
            ...
            ]
        """
        self.__verify_str(nickname, "nickname")
        # 搜索公众号的url
        search_url = "https://mp.weixin.qq.com/cgi-bin/searchbiz"

        # 增加/更改请求参数
        params = {
            "query": nickname,
            "count": str(count),
            "action": "search_biz",
            "ajax": "1",
            "begin": str(begin)
        }
        self.params.update(params)

        try:
            # 返回与输入公众号名称最接近的公众号信息
            official = self.s.get(search_url,
                                  headers=self.headers,
                                  params=self.params)
            return official.json()["list"]
        except Exception:
            raise Exception(u"公众号名称错误或cookie、token错误，请重新输入")

    def articles_nums(self, nickname):
        """
        获取公众号的总共发布的文章数量
        Parameters
        ----------
        nickname : str
            需要爬取公众号名称

        Returns
        -------
        int
            文章总数
        """
        self.__verify_str(nickname, "nickname")
        try:
            return self.__get_articles_data(nickname, begin="0")["app_msg_cnt"]
        except Exception:
            raise Exception(u"公众号名称错误或cookie、token错误，请重新输入")

    def articles(self, nickname, begin=0, count=5):
        """
        获取公众号的每页的文章信息
        Parameters
        ----------
        nickname : str
            需要爬取公众号名称
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
        如果list为空则说明没有相关文章
        """
        self.__verify_str(nickname, "nickname")
        try:
            return self.__get_articles_data(nickname,
                                            begin=str(begin),
                                            count=str(count))["app_msg_list"]
        except Exception:
            raise Exception(u"公众号名称错误或cookie、token错误，请重新输入")

    def lastest_articles(self, biz):
        """
        获取公众号的每页的文章信息
        Parameters
        ----------
        biz : str
            公众号的biz

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
        如果list为空则说明没有相关文章
        """
        try:
            return self.__get_articles_data("", begin="0",
                                            biz=biz)["app_msg_list"]
        except Exception:
            raise Exception(u"公众号名称错误或cookie、token错误，请重新输入")

    def __get_articles_data(self,
                            nickname,
                            begin,
                            biz=None,
                            count=5,
                            type_="9",
                            action="list_ex",
                            query=None):
        """
        获取公众号文章的一些信息
        Parameters
        ----------
        nickname : str
            需要爬取公众号名称
        begin: str or int
            起始爬取的页数
        biz : str
            公众号的biz
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
              'app_msg_list': 　一个数组(参看get_articles函数),
              'base_resp': {
                'err_msg': 'ok',
                'ret': 0
              }
            }
        """
        # 获取文章信息的url
        appmsg_url = "https://mp.weixin.qq.com/cgi-bin/appmsg"

        try:
            if nickname != "":
                # 获取公众号的fakeid
                official_info = self.official_info(nickname)
                self.params["fakeid"] = official_info[0]["fakeid"]
            elif biz != None:
                self.params["fakeid"] = biz
            else:
                raise Exception(u"请输入biz或者nickname")
        except Exception:
            raise Exception(u"公众号名称错误或cookie、token错误，请重新输入")

        # 增加/更改请求参数
        params = {
            "query": query if query != None else "",
            "begin": str(begin),
            "count": str(count),
            "type": str(type_),
            "action": action
        }
        self.params.update(params)

        data = self.s.get(appmsg_url, headers=self.headers, params=self.params)
        return data.json()
