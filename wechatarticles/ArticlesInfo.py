# coding:  utf-8
import re

import requests


class ArticlesInfo(object):
    """
    登录WeChat，获取更加详细的推文信息。如点赞数、阅读数、评论等
    """

    def __init__(self, appmsg_token, cookie):
        """
        初始化参数
        Parameters
        ----------
        cookie: str
            点开微信公众号文章抓包工具获取的cookie
        appmsg_token: str
            点开微信公众号文章抓包工具获取的appmsg_token

        Returns
        -------
        None
        """
        self.s = requests.session()
        self.appmsg_token = appmsg_token
        self.headers = {
            "User-Agent":
            "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0Chrome/57.0.2987.132 MQQBrowser/6.2 Mobile",
            "Cookie":
            cookie
        }
        self.data = {
            "is_only_read": "1",
            "is_temp_url": "0",
            "appmsg_type": "9", # 新参数，不加入无法获取like_num
        }

    def __verify_url(self, article_url):
        """
        简单验证文章url是否符合要求
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        None
        """
        verify_lst = ["mp.weixin.qq.com", "__biz", "mid", "sn", "idx"]
        for string in verify_lst:
            if string not in article_url:
                raise Exception(
                    "params is error, please check your article_url")

    def read_like_nums(self, article_url):
        """
        获取阅读数和点赞数
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        (int, int):
            阅读数、点赞数
        """
        try:
            appmsgstat = self.__get_appmsgext(article_url)["appmsgstat"]
            return appmsgstat["read_num"], appmsgstat["like_num"], appmsgstat["old_like_num"]
        except Exception:
            raise Exception("params is error, please check your article_url")

    def comments(self, article_url):
        """
        获取文章评论
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        json:
            {
                "base_resp": {
                    "errmsg": "ok",
                    "ret": 0
                },
                "elected_comment": [
                    {
                        "content": 用户评论文字,
                        "content_id": "6846263421277569047",
                        "create_time": 1520098511,
                        "id": 3,
                        "is_from_friend": 0,
                        "is_from_me": 0,
                        "is_top": 0, 是否被置顶
                        "like_id": 10001,
                        "like_num": 3,
                        "like_status": 0,
                        "logo_url": "http://wx.qlogo.cn/mmhead/OibRNdtlJdkFLMHYLMR92Lvq0PicDpJpbnaicP3Z6kVcCicLPVjCWbAA9w/132",
                        "my_id": 23,
                        "nick_name": 评论用户的名字,
                        "reply": {
                            "reply_list": [ ]
                        }
                    }
                ],
                "elected_comment_total_cnt": 3, 评论总数
                "enabled": 1,
                "friend_comment": [ ],
                "is_fans": 1,
                "logo_url": "http://wx.qlogo.cn/mmhead/Q3auHgzwzM6GAic0FAHOu9Gtv5lEu5kUqO6y6EjEFjAhuhUNIS7Y2AQ/132",
                "my_comment": [ ],
                "nick_name": 当前用户名,
                "only_fans_can_comment": false
            }
        """
        __biz, _, idx, _ = self.__get_params(article_url)
        getcomment_url = "https://mp.weixin.qq.com/mp/appmsg_comment?action=getcomment&__biz={}&idx={}&comment_id={}&limit=100"
        try:
            url = getcomment_url.format(__biz, idx, self.__get_comment_id(article_url))
            comment_json = self.s.get(url, headers=self.headers).json()
        except Exception as e:
            print(e)
            comment_json = {}
        return comment_json

    def __get_comment_id(self, article_url):
        """
        获取comment_id
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        str:
            comment_id获取评论必要参数
        """
        res = self.s.get(article_url, data=self.data)
        # 使用正则提取comment_id
        comment_id = re.findall(r'comment_id = "\d+"',
                                res.text)[0].split(" ")[-1][1:-1]
        return comment_id

    def __get_params(self, article_url):
        """
        解析文章url, 获取必要的请求参数
        Parameters
        ----------
        article_url: str
            文章链接

        Returns
        -------
        (str, str, str, str):
            __biz, mid, idx, sn
        """
        # 简单验证文章的url是否正确
        self.__verify_url(article_url)

        # 切分url, 提取相应的参数
        string_lst = article_url.split("?")[1].split("&")
        dict_value = [string[string.index("=") + 1:] for string in string_lst]
        __biz, mid, idx, sn, *_ = dict_value
        sn = sn[:-3] if sn[-3] == "#" else sn

        return __biz, mid, idx, sn

    def __get_appmsgext(self, article_url):
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
        __biz, mid, idx, sn = self.__get_params(article_url)

        # 将params参数换到data中请求。这一步貌似不换也行
        origin_url = "https://mp.weixin.qq.com/mp/getappmsgext?"
        appmsgext_url = origin_url + "appmsg_token={}&x5=0".format(self.appmsg_token)
        self.data["__biz"] = __biz
        self.data["mid"] = mid
        self.data["sn"] = sn
        self.data["idx"] = idx

        # appmsgext_url = origin_url + "__biz={}&mid={}&sn={}&idx={}&appmsg_token={}&x5=1".format(
        #     __biz, mid, sn, idx, self.appmsg_token)
        appmsgext_json = requests.post(
            appmsgext_url, headers=self.headers, data=self.data).json()

        if "appmsgstat" not in appmsgext_json.keys():
            raise Exception(
                "get info error, please check your cookie and appmsg_token")
        return appmsgext_json
