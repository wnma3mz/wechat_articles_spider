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


def get_all_urls(urls):
    # 获取所有的url
    url_lst = []
    for item in urls:
        url_lst.append(transfer_url(item['app_msg_ext_info']['content_url']))
        if 'multi_app_msg_item_list' in item['app_msg_ext_info'].keys():
            for ss in item['app_msg_ext_info']['multi_app_msg_item_list']:
                url_lst.append(transfer_url(ss['content_url']))

    return url_lst


def get_all_urls_title_date(urls):
    # 获取所有的[url, title, date]
    import time
    url_lst = []

    for item in urls:
        timestamp = item['comm_msg_info']['datetime']
        time_local = time.localtime(timestamp)
        # 转换成日期
        time_temp = time.strftime("%Y-%m-%d", time_local)

        # 文章url
        url_temp = transfer_url(item['app_msg_ext_info']['content_url'])

        # 文章标题
        title_temp = item['app_msg_ext_info']['title']
        url_lst.append([url_temp, title_temp, time_temp])

        if 'multi_app_msg_item_list' in item['app_msg_ext_info'].keys():
            for ss in item['app_msg_ext_info']['multi_app_msg_item_list']:

                url_temp = transfer_url(ss['content_url'])

                title_temp = ss['title']
                url_lst.append([url_temp, title_temp, time_temp])

    return url_lst


def method_one(biz, uin, cookie):

    t = PCUrls(biz=biz, uin=uin, cookie=cookie)
    count = 0
    lst = []
    while True:
        res = t.get_urls(key, offset=count)
        count += 10
        lst.append(res)

    return method_one


def method_two(biz, cookie):

    t = MobileUrls(biz=biz, cookie=cookie)
    count = 0
    lst = []
    while True:
        res = t.get_urls(appmsg_token, offset=count)
        count += 10
        lst.append(res)

    return method_two


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

    lst = method_one(biz, uin, cookie)

    # 个人微信号登陆后获取的token
    appmsg_token = appmsg_token

    # 方法二：使用MobileUrls。已在Ubuntu下测试

    # 自动获取参数
    '''
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
    '''

    lst = method_two(biz, cookie)

    # 碾平数组
    lst = flatten(lst)

    # 提取url
    url_lst = get_all_urls(lst)

    # 获取点赞数、阅读数、评论信息
    test = ArticlesInfo(appmsg_token, cookie)

    data_lst = []
    for i, url in enumerate(url_lst):

        item = test.comments(url)

        temp_lst = [url, item]

        try:
            read_num, like_num = test.read_like_nums(url)
            temp_lst.append(read_num)
            temp_lst.append(like_num)
        except:
            print("第{}个爬取失败，请更新参数".format(i + 1))
            break

        data_lst.append(temp_lst)
