# coding:  utf-8
import requests


class LoginWeChat(object):
    """
    登录WeChat，获取更加详细的推文信息。如点赞数、评论等
    article_url:
    http://mp.weixin.qq.com/s?__biz=MjM5NDU4ODI0NQ==&mid=2650949647&idx=1&sn=854714295ceee7943fe9426ab10453bf&chksm=bd739b358a041223833057cc3816f9562999e748904f39b166ee2178ce1a565e108fe364b920#rd'
    """

    def __init__(self, key, appmsg_token, cookie, req_id, pass_ticket):
        """
        初始化参数
        Parameters
        ----------
        key: str
            登录WeChat之后获取的key
        appmsg_token: str
            登录WeChat之后获取的appmsg_token
        cookie: str
            登录WeChat之后获取的cookie
        req_id:
            每篇文章的req_id
        pass_ticket:
            每篇文章的pass_ticket

        Returns
        -------
        None
        """
        self.s = requests.session()
        self.key = key
        self.appmsg_token = appmsg_token
        self.req_id = req_id
        self.pass_ticket = pass_ticket
        self.headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
            "Cookie":
            cookie
        }
        self.params = {
            "key": self.key,
            "pass_ticket": self.pass_ticket,
            "appmsg_token": self.appmsg_token,
        }
        self.data = {
            "is_only_read": "1",
            "req_id": self.req_id,
            "pass_ticket": self.pass_ticket,
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
        """
        appmsgext_url = "http://mp.weixin.qq.com/mp/getappmsgext"
        # 解析文章的url,获取请求参数
        string_lst = article_url.split("?")[1].split("&")
        dict_value = [string[string.index("=") + 1:] for string in string_lst]
        __biz, mid, idx, sn, *_ = dict_value
        if sn[-3] == "#":
            sn = sn[:-3]
        self.params["__biz"] = __biz
        self.params["mid"] = mid
        self.params["sn"] = sn
        self.params["idx"] = idx

        data = requests.post(
            appmsgext_url,
            headers=self.headers,
            data=self.data,
            params=self.params).json()
        #         data["appmsgstat"]
        return data
