# coding:  utf-8
import requests


class LoginWeChat(object):
    """
    登录WeChat，获取更加详细的推文信息。如点赞数、评论等
    article_url:
    http://mp.weixin.qq.com/s?__biz=MjM5NDU4ODI0NQ==&mid=2650949647&idx=1&sn=854714295ceee7943fe9426ab10453bf&chksm=bd739b358a041223833057cc3816f9562999e748904f39b166ee2178ce1a565e108fe364b920#rd'
    """

    def __init__(self, appmsg_token, cookie):
        """
        初始化参数
        Parameters
        ----------
        appmsg_token: str, 此处最好用r转义
            登录WeChat之后获取的appmsg_token
        cookie: str
            登录WeChat之后获取的cookie
        Returns
        -------
        None
        """
        self.s = requests.session()
        self.appmsg_token = appmsg_token
        self.headers = {
            "User-Agent":
            "Mozilla/5.0 (Linux; Android 7.1.1; PRO 6 Build/NMF26O; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0                   Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/043909 Mobile Safari/537.36  MicroMessenger/6.6.5.1280(0x26060532) NetType/WIFI Language",
            "Cookie":
            cookie
        }
        self.data = {
            "is_only_read": "1",
            "is_temp_url": "0",
        }

    def GetSpecInfo(self, article_url):
        """
        获取每篇文章具体信息
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        json:
            文章具体信息的json
            {
                'advertisement_info': [],
                'advertisement_num': 0,
                'appmsgstat': {'is_login': True,
                'like_num': 12,
                'liked': False,
                'read_num': 288,
                'real_read_num': 0,
                'ret': 0,
                'show': True},
                'base_resp': {'wxtoken': 2045685972},
                'reward_head_imgs': []
            }
        """
        origin_url = "http://mp.weixin.qq.com/mp/getappmsgext?"
        # 解析文章的url,获取请求参数
        string_lst = article_url.split("?")[1].split("&")
        dict_value = [string[string.index("=") + 1:] for string in string_lst]
        __biz, mid, idx, sn, *_ = dict_value
        if sn[-3] == "#":
            sn = sn[:-3]
        appmsgext_url = origin_url + "__biz={}&mid={}&sn={}&idx={}&appmsg_token={}&x5=1".format(
            __biz, mid, sn, idx, self.appmsg_token)
        data = requests.post(
            appmsgext_url, headers=self.headers, data=self.data).json()
        #         data["appmsgstat"]
        return data
