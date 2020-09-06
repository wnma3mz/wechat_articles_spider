# coding: utf-8
import os
from pprint import pprint
from wechatarticles import ArticlesUrls, tools

if __name__ == "__main__":
    # 模拟登录微信公众号平台，获取微信文章的url
    cookie = "cookie"
    token = "token"
    nickname = "nickname"
    query = "query"

    test = ArticlesUrls(cookie=cookie, token=token)

    articles_sum = test.articles_nums(nickname)
    artiacle_data = test.articles(nickname, begin="0", count="5")
    officical_info = test.official_info(nickname)

    print("articles_sum:", end=" ")
    print(articles_sum)
    print("artcles_data:")
    pprint(artiacle_data)
    print("officical_info:")
    pprint(officical_info)

    tools.save_json("test.json", artiacle_data)
