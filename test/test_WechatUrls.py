# coding: utf-8
import os
from pprint import pprint
from wechatarticles import PublicAccountsWeb

if __name__ == "__main__":
    # 模拟登录微信公众号平台，获取微信文章的url
    cookie = "cookie"
    token = "token"
    nickname = "nickname"

    paw = PublicAccountsWeb(cookie=cookie, token=token)
    # articles_sum = paw.articles_nums(nickname)
    article_data = paw.get_urls(nickname, begin="0", count="5")
    # official_info = paw.official_info(nickname)

    # print("articles_sum:", end=" ")
    # print(articles_sum)
    print("artcles_data:")
    pprint(article_data)
    # print("official_info:")
    # pprint(official_info)
