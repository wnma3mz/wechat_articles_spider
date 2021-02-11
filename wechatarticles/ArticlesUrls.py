# coding:  utf-8
import hashlib
import os
import time

import requests
from requests.cookies import cookielib

# TODO: 抽象一个基类


class PublicAccountsWeb(object):
    """通过微信公众号网页版抓取链接，或者公众号信息"""

    def __init__(self, cookie, token, proxies={"http": None, "https": None}):
        """
        Parameters
        ----------
        token : str
            登录微信公众号平台之后获取的token
        cookie : str
            登录微信公众号平台之后获取的cookie
        """
        self.s = requests.session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"
        }
        self.params = {
            "lang": "zh_CN",
            "f": "json",
        }

        # 手动输入cookie和token登录
        self.__verify_str(cookie, "cookie")
        self.__verify_str(token, "token")
        self.headers["Cookie"] = cookie
        self.params["token"] = token
        self.proxies = proxies

    def __verify_str(self, input_string, param_name):
        """
        验证输入是否为字符串

        Parameters
        ----------
        input_string: str
            输入
        param_name: str
            需要验证的参数名
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
        """
        # 实例化一个LWPcookiejar对象
        new_cookie_jar = cookielib.LWPCookieJar(username + ".txt")

        # 将转换成字典格式的RequestsCookieJar（这里我用字典推导手动转的）保存到LWPcookiejar中
        requests.utils.cookiejar_from_dict(
            {c.name: c.value for c in self.s.cookies}, new_cookie_jar
        )

        # 保存到本地文件
        new_cookie_jar.save(
            "cookies/" + username + ".txt", ignore_discard=True, ignore_expires=True
        )

    def __read_cookie(self, username):
        """
        读取cookies, username用于文件命名

        Parameters
        ----------
        username: str
            用户账号
        """
        # 实例化一个LWPCookieJar对象
        load_cookiejar = cookielib.LWPCookieJar()
        # 从文件中加载cookies(LWP格式)
        load_cookiejar.load(
            "cookies/" + username + ".txt", ignore_discard=True, ignore_expires=True
        )
        # 工具方法转换成字典
        load_cookies = requests.utils.dict_from_cookiejar(load_cookiejar)
        # 工具方法将字典转换成RequestsCookieJar，赋值给session的cookies.
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
        m5.update(password.encode("utf-8"))
        pwd = m5.hexdigest()
        return pwd

    def __startlogin_official(self, username, password):
        """
        获取登录二维码，进而获取Cookies

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
            "ajax": "1",
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
        登录微信公众号平台，获取token

        Parameters
        ----------
        username: str
            用户账号
        password: str
            用户密码
        """
        # 设定headers的referer的请求
        referer = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=validate&lang=zh_CN&account={}".format(
            username
        )
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
        res = self.s.post(
            bizlogin_url, data=data, headers=self.headers, proxies=self.proxies
        ).json()

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
            相关公众号的对应信息::

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
            "begin": str(begin),
        }
        self.params.update(params)

        try:
            # 返回与输入公众号名称最接近的公众号信息
            official = self.s.get(
                search_url,
                headers=self.headers,
                params=self.params,
                proxies=self.proxies,
            )
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

    def get_urls(self, nickname, begin=0, count=5):
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
            由每个文章信息构成的数组::

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
            return self.__get_articles_data(
                nickname, begin=str(begin), count=str(count)
            )["app_msg_list"]
        except Exception:
            raise Exception(u"公众号名称错误或cookie、token错误，请重新输入")

    def latest_articles(self, biz):
        """
        获取公众号的最新页的文章信息

        Parameters
        ----------
        biz : str
            公众号的biz

        Returns
        -------
        list:
            由每个文章信息构成的数组::

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
            return self.__get_articles_data("", begin="0", biz=biz)["app_msg_list"]
        except Exception:
            raise Exception(u"公众号名称错误或cookie、token错误，请重新输入")

    def __get_articles_data(
        self,
        nickname,
        begin,
        biz=None,
        count=5,
        type_="9",
        action="list_ex",
        query=None,
    ):
        """
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
            文章信息的json::

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
            "action": action,
        }
        self.params.update(params)

        data = self.s.get(
            appmsg_url, headers=self.headers, params=self.params, proxies=self.proxies
        )
        return data.json()


class PC(object):
    """通过PC端的微信，获取需要爬取的微信公众号的推文链接"""

    def __init__(self, biz, uin, cookie, proxies={"http": None, "https": None}):
        """
        Parameters
        ----------
        __biz: str
            需要爬取公众号的id
        uin: str
            用户id
        cookies : str
            登录微信后获取的cookie

        """
        self.s = requests.session()
        self.__biz = biz
        self.uin = uin
        self.headers = {"Cookies": cookie}
        self.proxies = proxies

    def get_urls(self, key, offset="0"):
        """
        Parameters
        ----------
        key: str
            个人微信号登陆后获取的key
        offset: str or int
            获取起始的页数，从0开始，每次递增10（可以大于10，但是不好确认参数，所以递增10，之后再去重）
        Returns
        ----------
        list:
        由每个文章信息构成的数组，主要获取的参数`item['app_msg_ext_info']['content_url']`, `item['app_msg_ext_info']['title']`, `item['comm_msg_info']['datetime']`::

            import html
            消除转义 html.unescape(html.unescape(url)); eval(repr(url).replace('\\', ''))
            [
                {
                    'app_msg_ext_info': {
                        'audio_fileid': 0,
                        'author': '',
                        'content': '',
                        'content_url': 文章url，存在转义符'/'需要去除,
                        'copyright_stat': 100,
                        'cover': 文章封面url，存在转义符'/'需要去除,
                        'del_flag': 1,
                        'digest': '',
                        'duration': 0,
                        'fileid': 0,
                        'is_multi': 0,
                        'item_show_type': 8,
                        'malicious_content_type': 0,
                        'malicious_title_reason_id': 0,
                        'multi_app_msg_item_list': [],
                        'play_url': '',
                        'source_url': '',
                        'subtype': 9,
                        'title': 文章标题
                    },
                    'comm_msg_info': {
                        'content': '',
                        'datetime': 1536930840,
                        'fakeid': '2394588245',
                        'id': 1000000262,
                        'status': 2,
                        'type': 49
                    }
                }
            ]
        """
        self.params = {
            "action": "getmsg",
            "__biz": self.__biz,
            "f": "json",
            "offset": str(offset),
            "count": "10",
            "uin": self.uin,
            "key": key,
        }
        origin_url = "https://mp.weixin.qq.com/mp/profile_ext"

        msg_json = self.s.get(
            origin_url, params=self.params, headers=self.headers, proxies=self.proxies
        ).json()
        if "general_msg_list" in msg_json.keys():
            lst = [
                item
                for item in eval(msg_json["general_msg_list"])["list"]
                if "app_msg_ext_info" in item.keys()
            ]
            return lst

        raise Exception(
            "Failure:\n1.params is error, please check your params\n2.key is lose efficacy, please update your key"
        )


class Mobile(object):
    """通过移动端的wechat，获取需要爬取的微信公众号的推文链接"""

    def __init__(self, biz, cookie):
        """
        Parameters
        ----------
        __biz: str
            需要爬取公众号的id
        cookie : str
            登录微信后获取的cookie
        """
        self.s = requests.session()
        self.__biz = biz
        self.headers = {
            "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0Chrome/57.0.2987.132 MQQBrowser/6.2 Mobile",
            "Cookie": cookie,
        }

    def get_urls(self, appmsg_token, offset="0"):
        """
        Parameters
        ----------
        appmsg_token: str
            个人微信号登陆后获取的token
        offset: str or int
            获取起始的页数，从0开始，每次递增10（可以大于10，但是不好确认参数，所以递增10，之后再去重）
        
        Returns
        ----------
        list:
        由每个文章信息构成的数组::

            [
                {
                    'app_msg_ext_info': {
                        'audio_fileid': 0,
                        'author': '',
                        'content': '',
                        'content_url': 文章url，存在转义符'/'需要去除,
                        'copyright_stat': 100,
                        'cover': 文章封面url，存在转义符'/'需要去除,
                        'del_flag': 1,
                        'digest': '',
                        'duration': 0,
                        'fileid': 0,
                        'is_multi': 0,
                        'item_show_type': 8,
                        'malicious_content_type': 0,
                        'malicious_title_reason_id': 0,
                        'multi_app_msg_item_list': [],
                        'play_url': '',
                        'source_url': '',
                        'subtype': 9,
                        'title': 文章标题
                    },
                    'comm_msg_info': {
                        'content': '',
                        'datetime': 1536930840,
                        'fakeid': '2394588245',
                        'id': 1000000262,
                        'status': 2,
                        'type': 49
                    }
                }
            ]
        """
        self.params = {
            "action": "getmsg",
            "__biz": self.__biz,
            "f": "json",
            "offset": str(offset),
            "count": "10",
            "appmsg_token": appmsg_token,
        }
        origin_url = "https://mp.weixin.qq.com/mp/profile_ext"

        msg_json = self.s.get(
            origin_url, params=self.params, headers=self.headers, proxies=self.proxies
        ).json()
        if "general_msg_list" in msg_json.keys():
            lst = [
                item
                for item in eval(msg_json["general_msg_list"])["list"]
                if "app_msg_ext_info" in item.keys()
            ]
            return lst

        raise Exception(
            "Failure:\n1.params is error, please check your params\n2.key is lose efficacy, please update your key"
        )


class WeBook(object):
    """
    通过微信读书，获取需要爬取的微信公众号的推文链接
    vid是固定的微信账号
    skey是变动的
    需要注意抓取时间，如每次抓取暂停50s，则可以抓取51次左右。
    该接口也不会封禁（暂时来看），如果被判定频繁，只需要在移动端进行滑动验证码，则可以继续抓取
    """

    def __init__(
        self, skey, vid, user_agent=None, proxies={"http": None, "https": None}
    ):
        self.s = requests.session()
        self.base_url = "https://i.weread.qq.com/book/articles?bookId=MP_WXS_{}&count=20&offset={}&synckey={}"
        user_agent = (
            "WeRead/5.3.4 (iPhone; iOS 14.1; Scale/2.00)"
            if user_agent == None
            else user_agent
        )
        self.headers = {
            "User-Agent": user_agent,
            "Cookies": "wr_logined=1",
            "skey": skey,
            "vid": vid,
        }
        self.proxies = proxies

    def get_urls(self, bookid, offset="0"):
        url = self.base_url.format(bookid, offset, str(time.time()).split(".")[0])
        res = self.s.get(url, headers=self.headers, proxies=self.proxies)
        if "reviews" in res.json():
            item_lst = res.json()["reviews"]
            return [item["review"] for item in item_lst]
        else:
            print(res.json())
            return []
