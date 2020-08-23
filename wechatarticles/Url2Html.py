# coding: utf-8
import os
import re
import time

import requests


class Url2Html(object):
    """根据微信文章链接下载为本地HTML文件"""
    def __init__(self, img_path=None):
        """
        img_path: 本地存储图片的路径，采用绝对路径的方式引用图片。可不下载图片
        """
        self.data_src_re = re.compile(r'data-src="(.*?)"')
        self.data_croporisrc_re = re.compile(r'data-croporisrc="(.*?)"')
        self.src_re = re.compile(r'src="(.*?)"')
        self.img_path = img_path

    def replace_name(self, title):
        """
        对进行标题替换，确保标题符合windows的命名规则
        title: 文章标题
        """
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        title = re.sub(rstr, "", title)
        return title

    def download_img(self, url):
        """
        下载图片
        url: 图片链接
        """
        # 根据链接提取图片名
        name = '{}.{}'.format(
            url.split('/')[-2],
            url.split('/')[3].split('_')[-1])
        imgpath = os.path.join(self.img_path, name)
        # 如果该图片已被下载，可以无需再下载，直接返回路径即可
        if os.path.isfile(imgpath):
            with open(imgpath, 'rb') as f:
                img = f.read()
            return imgpath, img

        response = requests.get(url)
        img = response.content
        with open(imgpath, 'wb') as f:
            f.write(img)
        return imgpath, img

    def replace_img(self, html):
        """
        根据提供的html源码找出其中的图片链接，并对其进行替换
        html: 文章源码
        """
        data_croporisrc_lst = self.data_croporisrc_re.findall(html)
        data_src_lst = self.data_src_re.findall(html)
        src_lst = self.src_re.findall(html)

        img_url_lst = data_croporisrc_lst + data_src_lst + src_lst
        img_lst = []
        for img_url in img_url_lst:
            if 'mmbiz.qpic.cn' in img_url:
                # print(img_url)
                data_src, img = self.download_img(img_url)
                img_lst.append([data_src, img])
                # 以绝对路径的方式替换图片
                html = html.replace(img_url,
                                    data_src).replace('data-src=', 'src=')
        return html, img_lst

    def get_title(self, html):
        """
        根据提供的html源码提取文章中的标题
        html: 文章源码
        """
        try:
            title = html.split('activity-name">')[1].split('</h2')[0].strip()
            return title
        except Exception as e:
            print(e)
            return ''

    def article_info(self, html):
        """
        根据提供的html源码提取文章中的公众号和作者
        html: 文章源码
        """
        account = html.split('rich_media_meta rich_media_meta_text">'
                             )[1].split('</span')[0].strip()
        author = html.split('id="js_name">')[1].split('</a')[0].strip()
        return account, author

    def get_timestamp(self, html):
        """
        根据提供的html源码提取文章发表的时间戳
        html: 文章源码
        """
        timestamp = int(html.split('ct = "')[1].split('";')[0].strip())
        return timestamp

    def timestamp2date(self, timestamp):
        """
        时间戳转日期
        timestamp: 时间戳
        """
        ymd = time.localtime(timestamp)
        date = '{}-{}-{}'.format(ymd.tm_year, ymd.tm_mon, ymd.tm_mday)
        return date

    def rename_title(self, title, html):
        # 自动获取文章标题
        if title == None:
            title = self.get_title(html)
        if title == '':
            return ''
        title = self.replace_name(title)

        if self.account == None:
            try:
                account_name = self.article_info(html)[0]
            except:
                account_name = '未分类'
        else:
            account_name = self.account
        try:
            date = self.timestamp2date(self.get_timestamp(html))
        except:
            date = ''
        try:
            if not os.path.isdir(account_name):
                os.mkdir(account_name)
        except:
            account_name = '未分类'
            if not os.path.isdir(account_name):
                os.mkdir(account_name)

        title = os.path.join(account_name,
                             '[{}]-{}-{}'.format(account_name, date, title))
        return title

    def run(self, url, mode, **kwargs):
        """
        启动函数
        url: 微信文章链接
        mode: 运行模式
            1: 返回html源码，不下载图片
            2: 返回html源码，下载图片但不替换图片路径
            3: 返回html源码，下载图片且替换图片路径
            4: 保存html源码，下载图片且替换图片路径
        kwargs:
            account: 公众号名
            title: 文章名
            img_path: 图片下载路径
        """
        if mode == 1:
            return requests.get(url).text
        elif mode in [2, 3, 4]:
            if 'img_path' in kwargs.keys():
                self.img_path = kwargs['img_path']
            else:
                return '{} 请输入保存图片路径!'.format(url)
            if mode == 2:
                return requests.get(url).text
            elif mode == 3:
                html = requests.get(url).text
                html_img, _ = self.replace_img(html)
                return html_img
            else:
                if 'account' in kwargs.keys():
                    self.account = kwargs['account']
                else:
                    self.account = None
                if 'title' in kwargs.keys():
                    title = kwargs['title']
                else:
                    title = None
                title = self.rename_title(title, html)
                if os.path.isfile(title):
                    return 0
                html = requests.get(url).text
                html_img, _ = self.replace_img(html)
                with open('{}.html'.format(title), 'w', encoding='utf-8') as f:
                    f.write(html_img)
                return '{} success!'.format(url)
        else:
            print("please input correct mode num")
            return 'faied!'


if __name__ == '__main__':

    url_lst = [
        'http://mp.weixin.qq.com/s?__biz=MTc5MTU3NTYyMQ==&mid=2650742058&idx=2&sn=1da6e9ddd1a0281e8c548fb30f8387f0&chksm=5afd0c006d8a851648e91e8cdaebfc2ab61d2518cbba369749b0a29cccb4781c622f966e6b04#rd'
    ]
    uh = Url2Html()
    for url in url_lst:
        s = uh.run(url, mode=4, img_path='D:\\imgs')
        print(s)