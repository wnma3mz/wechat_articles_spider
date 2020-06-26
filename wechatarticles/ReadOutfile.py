# coding: utf-8
import os
import re

from mitmproxy import io
from mitmproxy.exceptions import FlowReadException
from mitmproxy import http
import urllib
import sys
import typing


class Reader:
    """
    运行mitmproxy，并筛选cookie和appmsg_token， 这里的编码是二进制编码，所以需要decode
    command: python get_params outfile
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

    def __get_cookie(self, headers_tuple):
        """
        提取cookie
        Parameters
        ----------
        headers_tuple: tuple
            每个元组里面又包含了一个由两个元素组成的元组

        Returns
        -------
        cookie
            cookie参数
        """
        cookie = None
        for item in headers_tuple:
            key, value = item
            # 找到第一个元素为Cookie的元组
            if key == b"Cookie":
                cookie = value.decode()
                break
        return cookie

    def __get_appmsg_token(self, path_str):
        """
        提取appmsg_token
        Parameters
        ----------
        path_str: str
            一个由二进制编码的字符串

        Returns
        -------
        appmsg_token
            appmsg_token参数
        """
        path = path_str.decode()
        # 使用正则进行筛选
        appmsg_token_string = re.findall("appmsg_token.+?&", path)
        # 筛选出来的结果: 'appmsg_token=xxxxxxx&'
        appmsg_token = appmsg_token_string[0].split("=")
        appmsg_token = appmsg_token[1][:-1]
        return appmsg_token

    def request(self, outfile):
        """
        读取文件，获取appmsg_token和cookie
        Parameters
        ----------
        outfile: str
            文件路径

        Returns
        -------
        (str, str)
            appmsg_token, cookie：需要的参数
        """
        cookie, appmsg_token = '', ''
        with open(outfile, "rb") as logfile:
            freader = io.FlowReader(logfile)
            try:
                for f in freader.stream():
                    # 获取完整的请求信息
                    state = f.get_state()
                    # 尝试获取cookie和appmsg_token,如果获取成功就停止
                    try:
                        # 截取其中request部分
                        request = state["request"]
                        # 提取Cookie
                        cookie = self.__get_cookie(request["headers"])
                        # 提取appmsg_token
                        appmsg_token = self.__get_appmsg_token(request["path"])
                    except Exception:
                        continue
            except FlowReadException as e:
                print("Flow file corrupted: {}".format(e))
        # 如果获取成功就直接返回，获取失败就需要重新抓包
        if cookie != '' and appmsg_token != '':
            return appmsg_token, cookie
        return self.contral(outfile)

    def contral(self, outfile):
        """
        控制函数，调用命令保存http请求，并筛选获取appmsg_token和cookie
        Parameters
        ----------
        outfile: str
            文件路径

        Returns
        -------
        (str, str)
            appmsg_token, cookie：需要的参数
        """
        path = os.path.split(os.path.realpath(__file__))[0]
        command = "mitmdump -qs {}/ReadOutfile.py {} mp.weixin.qq.com/mp/getappmsgext".format(path, outfile)
        os.system(command)

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
    url = urllib.parse.unquote(flow.request.url)
    outfile = sys.argv[3]
    f: typing.IO[bytes] = open(outfile, 'wb')
    w = io.FlowWriter(f)
    if "mp.weixin.qq.com/mp/getappmsgext" in url:
        w.add(flow)
        f.close()
        exit()

