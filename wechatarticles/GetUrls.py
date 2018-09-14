# coding: utf-8
import requests


class PCUrls(object):
    """
    通过PC端的wechat，获取需要爬取的微信公众号的推文链接
    """

    def __init__(self, biz, uin, cookie):
        """
        初始化参数
        Parameters
        ----------
        __biz: str
            需要爬取公众号的id
        uin: str
            用户id
        cookies : str
            登录微信后获取的cookie
        Returns
        -------
            None
        """
        self.s = requests.session()
        self.__biz = biz
        self.uin = uin
        self.headers = {
            'Cookies': cookie
        }

    def get_urls(self, key, offset='0'):
        """
        获取urls
        Parameters
        ----------
        key: str
            个人微信号登陆后获取的key
        offset: str or int
            获取起始的页数，从0开始，每次递增10（可以大于10，但是不好确认参数，所以递增10，之后再去重）
        Returns
        ----------
        list:
        由每个文章信息构成的数组，主要获取的参数item['app_msg_ext_info']['content_url'], item['app_msg_ext_info']['title'], item['comm_msg_info']['datetime']
        import html
        消除转义 html.unescape(html.unescape(url)); eval(repr(url).replace('\\', ''))
        [
            {
                'app_msg_ext_info': {
                    'audio_fileid': 0,
                    'author': '',
                    'content': '',
                    'content_url': 文章url，存在转义符'/'需要去除,
                    'copyright_stat': 100,
                    'cover': 文章封面url，存在转义符'/'需要去除,
                    'del_flag': 1,
                    'digest': '',
                    'duration': 0,
                    'fileid': 0,
                    'is_multi': 0,
                    'item_show_type': 8,
                    'malicious_content_type': 0,
                    'malicious_title_reason_id': 0,
                    'multi_app_msg_item_list': [],
                    'play_url': '',
                    'source_url': '',
                    'subtype': 9,
                    'title': 文章标题
                },
                'comm_msg_info': {
                    'content': '',
                    'datetime': 1536930840,
                    'fakeid': '2394588245',
                    'id': 1000000262,
                    'status': 2,
                    'type': 49
                }
            }
        ]
        """
        self.params = {
            'action': 'getmsg',
            '__biz': self.__biz,
            'f': 'json',
            'offset': str(offset),
            'count': '10',
            'uin': self.uin,
            'key': key,
        }
        origin_url = 'https://mp.weixin.qq.com/mp/profile_ext'

        msg_json = self.s.get(origin_url, params=self.params,
                              headers=self.headers).json()
        if 'general_msg_list' in msg_json.keys():
            lst = [item for item in eval(msg_json['general_msg_list'])[
                'list'] if 'app_msg_ext_info' in item.keys()]
            return lst

        raise Exception(
            'Failure:\n1.params is error, please check your params\n2.key is lose efficacy, please update your key')


class MobileUrls(object):
    """
    通过移动端的wechat，获取需要爬取的微信公众号的推文链接
    """

    def __init__(self, biz, cookie):
        """
        初始化参数
        Parameters
        ----------
        __biz: str
            需要爬取公众号的id
        cookie : str
            登录微信后获取的cookie
        Returns
        -------
            None
        """
        self.s = requests.session()
        self.__biz = biz
        self.headers = {
            'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0Chrome/57.0.2987.132 MQQBrowser/6.2 Mobile',
            'Cookie': cookie
        }

    def get_urls(self, appmsg_token, offset='0'):
        """
        获取urls
        Parameters
        ----------
        appmsg_token: str
            个人微信号登陆后获取的token
        offset: str or int
            获取起始的页数，从0开始，每次递增10（可以大于10，但是不好确认参数，所以递增10，之后再去重）
        Returns
        ----------
        list:
        由每个文章信息构成的数组，主要获取的参数item['app_msg_ext_info']['content_url'], item['app_msg_ext_info']['title'], item['comm_msg_info']['datetime']
        import html
        消除转义 html.unescape(html.unescape(url)); eval(repr(url).replace('\\', ''))
        [
            {
                'app_msg_ext_info': {
                    'audio_fileid': 0,
                    'author': '',
                    'content': '',
                    'content_url': 文章url，存在转义符'/'需要去除,
                    'copyright_stat': 100,
                    'cover': 文章封面url，存在转义符'/'需要去除,
                    'del_flag': 1,
                    'digest': '',
                    'duration': 0,
                    'fileid': 0,
                    'is_multi': 0,
                    'item_show_type': 8,
                    'malicious_content_type': 0,
                    'malicious_title_reason_id': 0,
                    'multi_app_msg_item_list': [],
                    'play_url': '',
                    'source_url': '',
                    'subtype': 9,
                    'title': 文章标题
                },
                'comm_msg_info': {
                    'content': '',
                    'datetime': 1536930840,
                    'fakeid': '2394588245',
                    'id': 1000000262,
                    'status': 2,
                    'type': 49
                }
            }
        ]
        """
        self.params = {
            'action': 'getmsg',
            '__biz': self.__biz,
            'f': 'json',
            'offset': str(offset),
            'count': '10',
            'appmsg_token': appmsg_token,
        }
        origin_url = 'https://mp.weixin.qq.com/mp/profile_ext'

        msg_json = self.s.get(origin_url, params=self.params,
                              headers=self.headers).json()
        if 'general_msg_list' in msg_json.keys():
            lst = [item for item in eval(msg_json['general_msg_list'])[
                'list'] if 'app_msg_ext_info' in item.keys()]
            return lst

        raise Exception(
            'Failure:\n1.params is error, please check your params\n2.key is lose efficacy, please update your key')
