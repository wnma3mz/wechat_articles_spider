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

        try:
            account_name = self.article_info(html)[0]
        except:
            account_name = '未分类'
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

    def run(self, url, title=None, text=False, img=True, img_path=None, source=False):
        """
        启动函数
        url: 微信文章链接
        title: 文章标题。若未提供，则根据文章源码自动查找
        text: 只保存文章文本内容
        img: 是否需要下载图片
        img_path: 下载图片的路径。如果img==True, 那么img_path不能为None
        source: 是否返回html源码,返回源码则不保存
        """
        if img:
            if img_path != None:
                self.img_path = img_path
            if self.img_path == None:
                return '{} 请输入保存图片路径!'.format(url)
        html = requests.get(url).text
        title = self.rename_title(title, html)
        if title == '':
            return '{} 该文章已被删除'.format(url)

        # 下载图片并替换
        if img:
            html_img, _ = self.replace_img(html)
        else:
            html_img = html
        if text:
            html_img = html


        if source:
            return html_img
        else:
            with open('{}.html'.format(title), 'w', encoding='utf-8') as f:
                f.write(html_img)
        return '{} success!'.format(url)


if __name__ == '__main__':

    url_lst = [
        'http://mp.weixin.qq.com/s?__biz=MTc5MTU3NTYyMQ==&mid=2650742058&idx=2&sn=1da6e9ddd1a0281e8c548fb30f8387f0&chksm=5afd0c006d8a851648e91e8cdaebfc2ab61d2518cbba369749b0a29cccb4781c622f966e6b04#rd'
    ]
    uh = Url2Html()
    for url in url_lst:
        s = uh.run(url, img_path='D:\\imgs')
        print(s)