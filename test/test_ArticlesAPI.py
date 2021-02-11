# coding: utf-8
import os
from pprint import pprint
from wechatarticles import ArticlesAPI
from wechatarticles.utils import save_json

if __name__ == "__main__":
    # 该API慎用，不再维护

    # 利用公众号获取链接，并获取阅读点赞
    official_cookie = "official_cookie"
    token = "token"
    appmsg_token = "appmsg_token"
    wechat_cookie = "wechat_cookie"

    nickname = "nickname"

    # 手动输入所有参数
    aa = ArticlesAPI(
        official_cookie=official_cookie,
        token=token,
        appmsg_token=appmsg_token,
        wechat_cookie=wechat_cookie,
    )

    # 自定义爬取，每次爬取5篇以上
    data = aa.complete_info(nickname=nickname, begin="0")
    print(len(data))
    pprint(data)

    # 自定义从某部分开始爬取，持续爬取，直至爬取失败为止，一次性最多爬取40篇（功能未测试，欢迎尝试）
    datas = aa.continue_info(nickname=nickname, begin="0")

    save_json("{}.json".format(nickname), data)
