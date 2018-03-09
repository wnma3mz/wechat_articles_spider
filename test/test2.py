# coding: utf-8
import sys
sys.path.append("./wechat_articles_spider")
from wechatarticles import OfficialWeChat
from wechatarticles import LoginWeChat
from pprint import pprint

if __name__ == '__main__':
    cookie = "cookie"
    appmsg_token = "appmsg_token"
    article_url = "http://mp.weixin.qq.com/s?__biz=MjM5NDU4ODI0NQ==&mid=2650949647&idx=1&sn=854714295ceee7943fe9426ab10453bf&chksm=bd739b358a041223833057cc3816f9562999e748904f39b166ee2178ce1a565e108fe364b920#rd'"
    test = LoginWeChat(appmsg_token, cookie)
    comments = test.get_comments(article_url)
    comments = test.get_comments(article_url)
    read_like_num = test.get_read_like_num(article_url)

