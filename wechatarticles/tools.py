# coding: utf-8

import time
import urllib


class tools(object):
    """
    一些tools，如时间戳转换
    """

    def __init__(self):
        """
        不需要额外的参数
        Parameters
        ----------
        None

        Returns
        -------
            None
        """
        pass

    @staticmethod
    def timestamp2date(timestamp):
        """
        时间戳转换为日期
        Parameters
        ----------
        timestamp: int or str
            用户账号

        Returns
        -------
        datetime:
            转换好的日期：年-月-日 时:分:秒
        """
        time_array = time.localtime(int(timestamp))
        datetime = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return datetime


def response(flow):
    """
    mitmdumps调用的脚本函数
    如果请求中包含需要的请求流，就在保存后终止运行
    Parameters
    ----------
    flow: http.HTTPFlow
        请求流, 通过命令调用
    
    Returns
    -------
        None
    """
    from mitmproxy import http

    url = urllib.parse.unquote(flow.request.url)
    if "mp.weixin.qq.com/mp/getappmsgext" in url:
        exit()
