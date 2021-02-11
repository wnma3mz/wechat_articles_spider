# coding: utf-8
import os
import re
import time

import requests
from bs4 import BeautifulSoup as bs

from .ArticlesUrls import PublicAccountsWeb


class AccountBiz(object):
    """通过公众号名称获取biz

    微信公众号网页版、清博、西瓜 ['xigu', 'qingbo', 'office']

    实测西瓜一次性可获取较多（目前西瓜的已废弃）


    """

    def __init__(
        self,
        cookie,
        token=None,
        method=None,
        t=120,
        proxies={
            "http": None,
            "https": None,
        },
    ):
        """
        Parameters
        ----------
        t: int
            获取一次时间间隔。西瓜10s, 清博10s, 公众号120s
        cookie: str
            平台登录的cookie
        token: str
            官方获取时需要token
        method: str
            三种获取方式，三选一
        """
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
            "Cookie": cookie,
        }
        assert method in ["xigua", "qingbo", "office"]
        self.method = method
        self.cookie = cookie
        self.token = token
        self.t = t
        self.biz_name = "{}, {}"
        self.proxies = proxies

    def run(self, nickname_lst):
        if self.method == "xigua":
            return self.xigua(nickname_lst)
        elif self.method == "qingbo":
            return self.qingbo(nickname_lst)
        else:
            s = ArticlesUrls(cookie=self.cookie, token=self.token, proxies=self.proxies)
            return self.office(s, nickname_lst)

    def office(self, s, nickname_lst):
        self.res_lst = []
        for nickname in nickname_lst:
            try:
                official_infos = s.official_info(nickname)
                if official_infos:
                    official_info = official_infos[0]
                    biz = official_info["fakeid"]
                    tmp = self.biz_name.format(biz, official_info["nickname"])
                    self.res_lst.append(tmp)
                time.sleep(self.t)
            except Exception as e:
                print(e)
                return self.res_lst
        return self.res_lst

    def xigua(self, nickname_lst):
        url = "https://data.xiguaji.com/Search/SearchAct/?type=1&key={}"
        self.res_lst = []
        for nickname in nickname_lst:
            try:
                s = requests.get(
                    url.format(nickname), headers=self.headers, proxies=self.proxies
                )
                soup = bs(s.text, "lxml")
                infos = soup.find_all(class_="number-details")
                if infos:
                    info = infos[0]
                    nickname = info.h3.text.strip()
                    try:
                        biz = info.img["src"].split("__biz=")[1].split("&")[0]
                    except Exception as e:
                        continue
                        print(e)
                    self.res_lst.append(self.biz_name.format(biz, nickname))
                time.sleep(self.t)
            except Exception as e:
                print(e)
                return self.res_lst
        return self.res_lst

    def qingbo(self, nickname_lst):
        url = "http://www.gsdata.cn/query/wx?q={}"
        self.res_lst = []
        for nickname in nickname_lst:
            try:
                s = requests.get(
                    url.format(nickname), headers=self.headers, proxies=self.proxies
                )
                biz_lst = re.findall(
                    r'<input type="hidden" class="biz" value="(.+)">?', s.text
                )
                if biz_lst != []:
                    nicknames_lst = re.findall(
                        r'<span class="color-pink">(.+)</span>', s.text
                    )
                    tmp = self.biz_name.format(biz_lst[0], nicknames_lst[0])
                    self.res_lst.append(tmp)
                time.sleep(self.t)
            except Exception as e:
                print(e)
                return self.res_lst
        return self.res_lst


if __name__ == "__main__":
    nickname_lst = ["科技美学", "AppSo", "InfoQ"]
    cookie = ""
    ab = AccountBiz(cookie, method="xigua", t=10)
    res_lst = ab.run(nickname_lst)

    fname = "1.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(item for item in res_lst))
