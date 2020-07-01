# coding: utf-8
import os
from pprint import pprint
from wechatarticles.ReadOutfile import Reader

if __name__ == '__main__':
    outfile = 'outfile'
    reader = Reader()
    reader.contral(outfile)
    appmsg_token, cookie = reader.request(outfile)
    print(appmsg_token, cookie)
