# coding: utf-8

from .ArticlesUrls import PublicAccountsWeb
from .ArticlesInfo import ArticlesInfo


class ArticlesAPI(object):
    """
    整合PublicAccountsWeb和ArticlesInfo，该API慎用，不再维护
    """

    def __init__(
        self,
        username=None,
        password=None,
        official_cookie=None,
        token=None,
        appmsg_token=None,
        wechat_cookie=None,
        outfile=None,
    ):
        """
        初始化参数

        Parameters
        ----------
        username: str
            用户账号
        password: str
            用户密码
        official_cookie : str
            登录微信公众号平台之后获取的cookie
        token : str
            登录微信公众号平台之后获取的token
        wechat_cookie: str
            点开微信公众号文章抓包工具获取的cookie
        appmsg_token: str
            点开微信公众号文章抓包工具获取的appmsg_token
        """
        # 两种登录方式, 扫码登录和手动输入登录
        if (token != None) and (official_cookie != None):
            self.official = PublicAccountsWeb(cookie=official_cookie, token=token)
        elif (username != None) and (password != None):
            self.official = PublicAccountsWeb(username=username, password=password)
        else:
            raise SystemError("please check your params")

        # 支持两种方式， mitmproxy自动获取参数和手动获取参数
        if (appmsg_token == None) and (wechat_cookie == None) and (outfile != None):
            raise SystemError("Not support this method")
        elif (appmsg_token != None) and (wechat_cookie != None):
            self.appmsg_token, self.cookie = appmsg_token, wechat_cookie
        else:
            raise SystemError("please check your params")

        self.wechat = ArticlesInfo(self.appmsg_token, self.cookie)

    def complete_info(self, nickname, begin=0, count=5):
        """
        获取公众号的抓取的文章文章信息

        Parameters
        ----------
        nickname: str
            公众号名称
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
                        'comments': 文章评论信息
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
                            },
                        'cover': 封面的url'digest': 文章摘要,
                        'itemidx': 1,
                        'like_num': 18, 文章点赞数
                        'link': 文章的url,
                        'read_num': 610, 文章阅读数
                        'title': 文章标题,
                        'update_time': 更新文章的时间戳
                    },
                ]
        如果list为空则说明没有相关文章
        """
        # 获取文章数据
        article_data = self.official.get_urls(
            nickname, begin=str(begin), count=str(count)
        )

        # 提取每个文章的url，获取文章的点赞、阅读、评论信息，并加入到原来的json中
        for data in article_data:
            article_url = data["link"]
            comments = self.wechat.comments(article_url)
            read_like_nums = self.wechat.read_like_nums(article_url)
            data["comments"] = comments
            data["read_num"], data["like_num"], data["old_like_num"] = read_like_nums

        return article_data

    def __extract_info(self, articles_data):
        # 提取每个文章的url，获取文章的点赞、阅读、评论信息，并加入到原来的json中
        for data in articles_data:
            article_url = data["link"]
            comments = self.wechat.comments(article_url)
            read_like_nums = self.wechat.read_like_nums(article_url)
            data["comments"] = comments
            data["read_num"], data["like_num"], data["old_like_num"] = read_like_nums

        return articles_data

    def continue_info(self, nickname, begin=0):
        """
        自动获取公众号的抓取的文章文章信息，直到爬取失败为止

        Parameters
        ----------
        nickname: str
            公众号名称
        begin: str or int
            起始爬取的页数

        Returns
        -------
        list:
            由每个文章信息构成的数组::

                [
                {
                    'aid': '2650949647_1',
                    'appmsgid': 2650949647,
                    'comments': 文章评论信息
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
                        },
                    'cover': 封面的url'digest': 文章摘要,
                    'itemidx': 1,
                    'like_num': 18, 文章点赞数
                    'link': 文章的url,
                    'read_num': 610, 文章阅读数
                    'title': 文章标题,
                    'update_time': 更新文章的时间戳
                },
                ]
        如果list为空则说明没有相关文章
        """
        article_datas = []
        count = 5
        while True:
            try:
                # 获取文章数据
                article_datas.append(
                    self.official.get_urls(nickname, begin=str(begin), count=str(count))
                )
            except Exception as e:
                print(e)
                break
            begin += count
            if begin > 40:
                break

        def flatten(x):
            return [y for l in x for y in flatten(l)] if type(x) is list else [x]

        # flatten = lambda x: [y for l in x for y in flatten(l)] if type(x) is list else [x]
        print("第{}篇文章爬取失败，请过段时间再次尝试或换个帐号继续爬取".format(begin))
        return self.__extract_info(flatten(article_datas))
