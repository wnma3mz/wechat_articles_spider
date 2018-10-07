# coding: utf-8
import os
import sys
from pprint import pprint
sys.path.append(os.getcwd())
import html
from wechatarticles.ReadOutfile import Reader
from wechatarticles.GetUrls import PCUrls, MobileUrls


def flatten(x): return [y for l in x for y in flatten(
    l)] if type(x) is list else [x]


def transfer_url(url):
    url = html.unescape(html.unescape(url))
    return eval(repr(url).replace('\\', ''))


if __name__ == '__main__':
    # 方法一：使用PCUrls。已在win10下测试
    # 需要抓取公众号的__biz参数
    biz = biz
    # 个人微信号登陆后获取的uin
    uin = uin
    # 个人微信号登陆后获取的cookie
    cookie = cookie
    # 个人微信号登陆后获取的key，隔段时间更新
    key = key

    t = PCUrls(biz=biz, uin=uin, cookie=cookie)
    count = 0
    lst = []
    while True:
        res = t.get_urls(key, offset=count)
        count += 10
        lst.append(res)
    # 个人微信号登陆后获取的token
    appmsg_token = appmsg_token

    # 方法二：使用MobileUrls。已在Ubuntu下测试
    from ReadOutfile import Reader
    biz = biz

    # 自动获取appmsg_token, cookie
    outfile = 'outfile'
    reader = Reader()
    reader.contral(outfile)
    appmsg_token, cookie = reader.request(outfile)
    # 通过抓包工具，手动获取appmsg_token, cookie，手动输入参数
    appmsg_token = appmsg_token
    cookie = cookie

    t = PCUrls(biz=biz, cookie=cookie)
    count = 0
    lst = []
    while True:
        res = t.get_urls(appmsg_token, offset=count)
        count += 10
        lst.append(res)

    # 碾平数组
    lst = flatten(lst)

    '''
    如果需要抓取comments，需要转义；只抓取阅读数不需要转义
    for article in lst:
        tmp_url = article['app_msg_ext_info']['content_url']
        article['app_msg_ext_info']['content_url'] = transfer_url(tmp_url)
    '''
    # 获取点赞数、阅读数、评论信息
    test = ArticlesInfo(appmsg_token, cookie)

    for i, item in enumerate(lst):
        url = item['app_msg_ext_info']['content_url']
        item['app_msg_ext_info']['comments'] = test.comments(url)
        try:
            item['app_msg_ext_info']['read_num'], item['app_msg_ext_info']['like_num'] = test.read_like_nums(
                url)
        except:
            print("第{}个爬取失败，请更新参数".format(i + 1))
            break
