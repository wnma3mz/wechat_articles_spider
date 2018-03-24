# coding: utf-8
import os
import sys
from pprint import pprint
sys.path.append(os.getcwd())
from wechatarticles.ReadOutfile import Reader
from wechatarticles import ArticlesAPI

if __name__ == '__main__':
    username = "username"
    password = "password"
    official_cookie = "official_cookie"
    token = "token"
    appmsg_token = "appmsg_token"
    wechat_cookie = "wechat_cookie"

    nickname = "nickname"

    # 手动输入所有参数
    test = ArticlesAPI(
        official_cookie=official_cookie,
        token=token,
        appmsg_token=appmsg_token,
        wechat_cookie=wechat_cookie)

    # 输入账号密码，自动登录公众号，手动输入appmsg_token和wechat_cookie
    test = ArticlesAPI(
        username=username,
        password=password,
        appmsg_token=appmsg_token,
        wechat_cookie=wechat_cookie)

    # 手动输入official_cookie和token, 自动获取appmsg_token和wechat_cookie
    test = ArticlesAPI(
        official_cookie=official_cookie, token=token, outfile="outfile")

    data = test.complete_info(nickname=nickname, begin="0")
    print(data.__len__())
    pprint(data)
