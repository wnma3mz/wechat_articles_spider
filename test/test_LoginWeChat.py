# coding: utf-8
import sys
import os
sys.path.append(os.getcwd())
from wechatarticles import OfficialWeChat
from wechatarticles import LoginWeChat
from wechatarticles import get_params
from pprint import pprint

if __name__ == '__main__':
    appmsg_token, cookie = get_params.main("outfile")
    appmsg_token, cookie  = "appmsg_token", "cookie"
    article_url = "http://mp.weixin.qq.com/s?__biz=MjM5NDU4ODI0NQ==&mid=2650949647&idx=1&sn=854714295ceee7943fe9426ab10453bf&chksm=bd739b358a041223833057cc3816f9562999e748904f39b166ee2178ce1a565e108fe364b920#rd'"
    test = LoginWeChat(appmsg_token, cookie)
    comments = test.get_comments(article_url)
    read_num, like_num = test.get_read_like_num(article_url)
    print("comments:")
    pprint(comments)
    print("read_like_num:", read_num, like_num)
