import re

import requests
from bs4 import BeautifulSoup as bs

from .utils import timestamp2date


class AlbumInfo:
    """
    从专栏获取数据
    """

    def __init__(self):
        self.url = "https://mp.weixin.qq.com/mp/appmsgalbum"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        }

    def run(self, params):
        s = requests.get(self.url, params=params, proxies=None, headers=self.headers)

        data = s.text.split("cgiData = ")[1].split(";\n")[0]
        data = data.replace("\t", "").replace("\n", "")

        # ftitle = eval(re.findall(",title: (.+?),", data)[0])
        title_lst = re.findall("{title: (.+?),", data)
        create_time_lst = re.findall(",create_time: (.+?),", data)
        url_lst = re.findall(",url: (.+?),", data)
        read_count_lst = re.findall(",read_count: (.+?),", data)

        create_time_lst = [
            timestamp2date("%Y-%m-%d", eval(eval((stamp)))) for stamp in create_time_lst
        ]
        url_lst = [eval(url) for url in url_lst]
        title_lst = [eval(title) for title in title_lst]

        return url_lst, title_lst, create_time_lst, read_count_lst

    @staticmethod
    def extract_url(a):
        soup = bs(a, "lxml")
        lst = soup.find_all("a")
        lst = [item["href"] for item in lst]
        return lst


if __name__ == "__main__":

    params = {
        "action": "getalbum",
        "__biz": "Mzg3MjMyNjM3Ng==",
        "scene": "1",
        "album_id": "1445532813889191937",
        "count": "3",
    }

    ai = AlbumInfo()
    # "链接", " 标题", " 日期", "阅读量"
    url_lst, title_lst, create_time_lst, read_count_lst = ai.run(params)

    res_lst = []
    for url, title, date, read_count in zip(
        url_lst, title_lst, create_time_lst, read_count_lst
    ):
        res_lst.append([url, title, date, read_count])
