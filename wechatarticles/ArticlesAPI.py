# coding: utf-8

from .LoginWeChat import LoginWeChat
from .OfficialWeChat import OfficialWeChat
from .ReadOutfile import Reader


class ArticlesAPI(object):
    """
    __doc__
    """

    def __init__(self,
                 username=None,
                 password=None,
                 official_cookie=None,
                 token=None,
                 appmsg_token=None,
                 wechat_cookie=None,
                 outfile=None):
        # 两种登录方式
        if (token != None) and (official_cookie != None):
            self.officical = OfficialWeChat(cookie=official_cookie, token=token)
        elif (username != None) and (password != None):
            self.officical = OfficialWeChat(
                username=username, password=password)
        else:
            print("please check your paramse")
            raise SystemError

        if (appmsg_token == None) and (wechat_cookie == None) and (outfile != None):
            self.appmsg_token, self.cookie = Reader().contral(outfile)
        elif (appmsg_token != None) and (wechat_cookie != None):
            self.appmsg_token, self.cookie = appmsg_token, wechat_cookie
        else:
            print("please check your params")
            raise SystemError
        self.wechat = LoginWeChat(self.appmsg_token, self.cookie)

    def get_data(self, nickname):
        artiacle_data = self.officical.get_articles(
            nickname, begin="0", count="5")
        for data in artiacle_data:
            comments = self.wechat.get_comments(article_url=data["link"])
            read_num, like_num = self.wechat.get_read_like_num(
                article_url=data["link"])
            data["comments"] = comments
            data["read_num"], data["like_num"] = read_num, like_num

        return artiacle_data