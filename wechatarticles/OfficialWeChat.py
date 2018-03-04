# coding:  utf-8
import requests
import sqlite3
import json

class OfficialWeChat(object):
    """
    获取需要爬取的微信公众号的推文链接
    """

    def __init__(self, token, cookie):
        """
        初始化参数
        Parameters
        ----------
        nickname : str or unicode
            需要爬取公众号名称
        token : str
            登录微信公众号平台之后获取的token
        cookie : str
            登录微信公众号平台之后获取的cookie

        Returns
        -------
        None
        """
        self.s = requests.session()
        self.token = token
        self.headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
            "Cookie":
            cookie
        }
        self.params = {
            "token": self.token,
            "lang": "zh_CN",
            "f": "json",
        }

    def get_official_info(self, nickname, begin="0", count="5"):
        """
        获取公众号的一些信息
        Parameters
        ----------
        begin: str or int
            起始爬取的页数
        count: str or int
            每次爬取的数量，1-5

        Returns
        -------
        json:
            公众号的一些信息
            {
              'alias': 公众号别名,
              'fakeid': 公众号唯一id,
              'nickname': 公众号名称,
              'round_head_img': 公众号头像的url,
              'service_type': 1公众号性质
            }
        """
        search_url = "https://mp.weixin.qq.com/cgi-bin/searchbiz"
        self.params["query"] = nickname
        self.params["count"] = count
        self.params["action"] = "search_biz"
        self.params["ajax"] = "1"
        self.params["begin"] = begin
        public_num = self.s.get(
            search_url, headers=self.headers,
            params=self.params).json()["list"]
        try:
            return public_num[0]
        except Exception:
            return u"公众号名称错误，请重新输入"

    def totalNums(self, nickname):
        """
        获取公众号的总共发布的文章数量
        Parameters
        ----------
        None

        Returns
        -------
        int
            文章总数
        """
        try:
            return self._get_articles_data(nickname, begin="0")["app_msg_cnt"]
        except Exception:
            return u"公众号名称错误，请重新输入"

    def get_articles(self, nickname, begin, count="5"):
        """
        获取公众号的每页的文章信息
        Parameters
        ----------
        begin: str or int
            起始爬取的页数
        count: str or int
            每次爬取的数量，1-5

        Returns
        -------
        list:
            由每个文章信息构成的数组
            [
              {
                'aid': '2650949647_1',
                'appmsgid': 2650949647,
                'cover': 封面的url'digest': 文章摘要,
                'itemidx': 1,
                'link': 文章的url,
                'title': 文章标题,
                'update_time': 更新文章的时间戳
              },
              {
                'aid': '2650949644_1',
                'appmsgid': 2650949644,
                'cover': 封面的url,
                'digest': 文章摘要,
                'itemidx': 1,
                'link': 文章的url,
                'title': 文章标题,
                'update_time': 更新文章的时间戳
              ]
        """
        try:
            return self._get_articles_data(
                nickname, begin=str(begin), count=str(count))["app_msg_list"]
        except Exception:
            return u"公众号名称错误，请重新输入"

    def _get_articles_data(self,
                           nickname,
                           begin,
                           count="5",
                           type_="9",
                           action="list_ex"):
        """
        获取公众号文章的一些信息
        Parameters
        ----------
        begin: str or int
            起始爬取的页数
        count: str or int
            每次爬取的数量，1-5
        type_: str or int
            获取数据的方式，暂不知道具体用途
        action: str
            请求之后的行为动作，"list_ex"获取文章信息的json
        Returns
        -------
        json:
            文章信息的json
            {
              'app_msg_cnt': 公众号发文章总数,
              'app_msg_list': 　一个数组(参看GetArticles),
              'base_resp': {
                'err_msg': 'ok',
                'ret': 0
              }
            }
        """
        appmsg_url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
        key_lst = ["query", "ajax"]

        official_info = self.get_official_info(nickname)
        if isinstance(official_info, dict):
            self.params["fakeid"] = official_info["fakeid"]
        else:
            return u"公众号名称错误，请重新输入"
        for key in key_lst:
            if key in self.params.keys():
                self.params.pop(key)

        self.params["begin"] = str(begin)
        self.params["count"] = str(count)
        self.params["type"] = str(type_)
        self.params["action"] = action

        data = self.s.get(
            appmsg_url, headers=self.headers, params=self.params).json()
        return data

    def save_txt(self, fname, data):
        if ".txt" not in fname:
            raise Exception("fname must be txt", fname)
        with open(fname, "a+") as f:
            for item in data:
                f.write(json.dumps(item))
                f.write("\n")

    def save_sqlite(self, dbname, tablename, data):
        with sqlite3.connect(dbname) as con:
            # 创建数据库
            with con as cur:
                create_sql = """
                create table {} (aid varchar(16) primary key, \
                    appmsgid varchar(16),cover text,digest text, \
                    itemidx integer,link text, title text, \
                    update_time integer)
                """.format(tablename)
                cur.execute(create_sql)

            # 插入数据
            with con as cur:
                for item in data:
                    try:
                        cur.execute(
                            "insert into {} values (?, ?, ?, ?, ?, ?, ?, ?)".
                            format(tablename), list(item.values()))
                    except Exception:
                        print("error")
                        return "error"
