# coding: utf-8
import requests
from bs4 import BeautifulSoup as bs
from bs4.element import NavigableString
import re
# 该文件仅作测试用，可能失效
path = 'F:\\wechat_articles_spider\\test\\imgs\\{}'
parse_lst = ['article', 'a']
str_lst = ['hr', 'span', 'ul']


def extract_text(p):
    pass


def download_img(url, name):
    response = requests.get(url)
    img = response.content
    imgpath = path.format(name)
    with open(imgpath, 'wb') as f:
        f.write(img)


def parse_section(sections):
    content = ''
    global section
    for section in sections:
        if section.name == None:
            content += section
        elif item.name == 'section':
            section_str = str(item)
            for img in item.find_all('img'):
                section_str = section_str.replace(
                    str(img), '\n\n![img]({})\n\n'.format(img['data-src']))
            content += section_str
            content += section_str
        elif section.name in str_lst:
            content += str(section)
        elif section.name == 'p':
            tmp = ''.join(str(content) for content in section.contents)
            content += tmp
        elif section.name in parse_lst:
            content += parse_section(section.contents)
        elif section.name == 'img':
            url = section['data-src']
            """
            name = url.split('/')[-2] + '.' + url.split('/')[-1].split('=')[1]
            download_img(url, name)
            content += '![{}]({})\n'.format(name, path.format(name))
            """
            content += '![img]({})\n'.format(url)
            # content += str(section)
        elif section.name == 'br':
            content += '</br>'
        elif section.name == 'strong':
            content += '<strong>{}</strong>'.format(section.string)
        elif section.name == 'iframe':
            content += 'iframe\n'
        else:
            print(section.name)
            # print(section)

    return content


url_lst = ['https://mp.weixin.qq.com/s/3Xqrn52jObN-M524Jld1yw']
with open('t.md', 'w', encoding='utf-8') as f:
    for url in url_lst[::-1]:
        html = requests.get(url)
        soup = bs(html.text, 'lxml')
        # try:
        body = soup.find(class_="rich_media_area_primary_inner")
        title = body.find(class_="rich_media_title").text.strip()
        author = body.find(
            class_="rich_media_meta rich_media_meta_nickname").a.text.strip()
        content_p = body.find(class_="rich_media_content")
        content_lst = content_p.contents

        content = ''

        for item in content_lst:
            if item.name == None:
                content += item
            elif item.name == 'section':
                section_str = str(item)
                for img in item.find_all('img'):
                    section_str = section_str.replace(
                        str(img), '\n\n![img]({})\n\n'.format(img['data-src']))
                content += section_str
            elif item.name in str_lst:
                content += str(item)
            elif item.name == 'p':
                tmp = ''.join(str(content) for content in item.contents)
                content += tmp
            elif item.name in parse_lst:
                content += parse_section(item.contents)
            elif item.name == 'br':
                content += '</br>'
            elif item.name == 'strong':
                content += '<strong>{}</strong>'.format(item.string)
            elif item.name == 'iframe':
                content += 'iframe\n'
            elif section.name == 'img':
                url = section['data-src']
                content += '![img]({})\n'.format(url)
            else:
                print(item.name)

        f.write('## ' + title + '\n')
        f.write(author + '\n')
        f.write(content + '\n')
        f.write('<div style="page-break-after: always;"></div>\n')
        # except:
        #     print(url)
        #     pass