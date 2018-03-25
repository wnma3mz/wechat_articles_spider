# coding: utf-8
import sys
import os
from pprint import pprint
sys.path.append(os.getcwd())
from wechatarticles import ArticlesUrls, tools

if __name__ == "__main__":
    # 模拟登录微信公众号平台，获取微信文章的url
    username = "username@qq.com"
    password = "password"
    cookie = "cookie"
    token = "token"
    nickname = "nickname"
    query = "query"

    test = ArticlesUrls(username, password)
    # test = ArticlesUrls(cookie=cookie, token=token)

    articles_sum = test.articles_nums(nickname)
    artiacle_data = test.articles(nickname, begin="0", count="5")
    officical_info = test.official_info(nickname)

    articles_data_query = test.articles(
        nickname, query=query, begin="0", count="5")
    articles_sum_query = test.articles(nickname, query=query)

    print("articles_sum:", end=" ")
    print(articles_sum)
    print("artcles_data:")
    pprint(artiacle_data)
    print("officical_info:")
    pprint(officical_info)

    tools.save_json("test.json", artiacle_data)
