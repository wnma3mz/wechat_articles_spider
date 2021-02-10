# coding: utf-8
import time

import requests


class WechatBook(object):
    """
    通过微信读书，获取需要爬取的微信公众号的推文链接
    vid是固定的微信账号
    skey是变动的
    需要注意抓取时间，如每次抓取暂停50s，则可以抓取51次左右。
    该接口也不会封禁（暂时来看），如果被判定频繁，只需要在移动端进行滑动验证码，则可以继续抓取
    """

    def __init__(
        self, skey, vid, user_agent=None, proxies={"http": None, "https": None}
    ):
        self.s = requests.session()
        self.base_url = "https://i.weread.qq.com/book/articles?bookId=MP_WXS_{}&count=20&offset={}&synckey={}"
        user_agent = (
            "WeRead/5.3.4 (iPhone; iOS 14.1; Scale/2.00)"
            if user_agent == None
            else user_agent
        )
        self.headers = {
            "User-Agent": user_agent,
            "Cookies": "wr_logined=1",
            "skey": skey,
            "vid": vid,
        }
        self.proxies = proxies

    def get_urls(self, bookid, offset="0"):
        url = self.base_url.format(bookid, offset, str(time.time()).split(".")[0])
        res = self.s.get(url, headers=self.headers, proxies=self.proxies)
        if "reviews" in res.json():
            item_lst = res.json()["reviews"]
            return [item["review"] for item in item_lst]
        else:
            print(res.json())
            return []
