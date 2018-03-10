# coding: utf-8
import sys
sys.path.append(os.getcwd())
from wechatarticles import OfficialWeChat
from wechatarticles import LoginWeChat
from pprint import pprint

if __name__ == "__main__":
    # 模拟登录微信公众号平台，获取微信文章的url
    username = "username@qq.com"
    password = "password"
    cookie = "cookie"
    token = "token"
    nickname = "nickname"
    #test = OfficialWeChat(username, password)
    test = OfficialWeChat(cookie=cookie, token=token)

    articles_sum = test.totalNums(nickname)
    artiacle_data = test.get_articles(nickname, begin="10", count="5")
    officical_info = test.get_official_info(nickname)

    print("articles_sum:", end=" ")
    print(articles_sum)
    print("artcles_data:")
    pprint(artiacle_data)
    print("officical_info:")
    pprint(officical_info)

    test.save_txt("test.txt", artiacle_data)
    test.save_sqlite("test.db", "test", artiacle_data)

