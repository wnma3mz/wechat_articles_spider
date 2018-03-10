# 微信公众号文章爬虫

实现思路:

1. 从微信公众号平台获取微信公众所有文章的url

2. 登录微信PC端获取文章的阅读数、评论等信息

完整思路可以参考我的博客: [微信公众号爬虫](http://blog.csdn.net/wnma3mz/article/details/78570580)

## 第三方包

- `requests`: 爬取内容

**支持两种爬虫方式**

下面登录方式选用其一即可

1. 账号密码爬虫，输入账号密码后，扫描二维码登录。自动获取cookie和token。此方法需要安装`matplotlib`和`PIL`用于显示二维码图片

2. cookie、token爬虫，手动复制cookie和token。具体cookie和token获取方式见[这篇文档](https://github.com/wnma3mz/wechat_articles_spider/blob/master/docs/get_cookie_token.md)

**支持三种存储方式**

1. txt存储（不建议）

2. sqlite3存储。自带模块，不需要额外安装

3. mongo存储。需要安装`pymongo`

## API实例

以下具体代码见`test/`目录下的实例代码。

```python
# 导入模块
import sys
sys.path.append(path + "/wechat_articles_spider")
from wechatarticles import OfficialWeChat
from wechatarticles import LoginWeChat
from wechatarticles import get_params
```

### 步骤一: 获取公众号的所有文章url

此处有次数限制，不可一次获取太多url(获取超过30、40条貌似就会失败)。解决方案多个账号同时爬取

```python
"""
初始化一些参数
username: 用户账号
password: 用户密码
cookie: 登录后获取的cookie
token: 登录后获取的token
nickname: 需要爬取的公众号
query: 筛选公众号文章的关键词
"""
username = username
password = password
cookie = yourcookie
token = token
nickname = nickname
query = query

# 实例化爬取对象
# 账号密码自动获取cookie和token
test = OfficialWeChat(username=username, password=password)
# 手动输入账号密码
test = OfficialWeChat(cookie=cookie, token=token)

# 输入公众号名称，获取公众号文章总数
articles_sum = test.totalNums(nickname)
# 输入公众号名称，获取公众号部分文章信息, 每次最大返回数为5个
articles_data = test.get_articles(nickname, begin="0", count="5")
# 输入公众号名称，获取公众号的一些信息
officical_info = test.get_official_info(nickname)
# 输入公众号名称，输入关键词，获取公众号相关文章信息, 每次最大返回数为5个
articles_data_query = test.get_articles(nickname, query=query, begin="0", count="5")
# 输入公众号名称，输入关键词，获取公众号相关文章总数
articles_sum_query = test.totalNums(nickname, query=query)

# 保存数据为txt格式
test.save_txt("test.txt", artiacle_data)
# 保存数据为sqlite3
test.save_sqlite("test.db", "test", artiacle_data)
# 保存数据到mongo中
test.save_mongo(data, host=host, port=27017,name=name, password=password, dbname=dbname, collname=collname)
```

### 步骤二：登录微信PC端获取文章信息

关于参数如何手动获取的介绍，可以参考[这篇文档](https://github.com/wnma3mz/wechat_articles_spider/blob/master/docs/get_appmsg_token.md)

关于参数如何自动获取的介绍，可以参考[这篇文档](https://github.com/wnma3mz/wechat_articles_spider/blob/master/docs/关于自动获取微信参数.md)

现已支持自动获取参数(需要安装`mitmproxy`)，建议获取每天或者每半天获取一次即可。此处通过上面获取到的url即可无限爬取，没有次数限制

```python
"""
初始化一些参数。登录WeChat移动端，点击任意一篇微信推文获取下面的参数
appmsg_token
cookie
"""
# 支持自动获取appmsg_token和cookie
appmsg_token, cookie = get_params.main("outfile")

# 实例化爬取对象
# 账号密码自动获取cookie和token
test = LoginWeChat(appmsg_token=appmsg_token, cookie=cookie)
# 获取微信文章的详细信息（包括文章的阅读数、评论数、点赞数等）
# 这里的articles_url是上面获取到的`articles_data`数组中每一项的"link"
test.GetSpecInfo(article_url=article_url)
# 获取文章所有的评论信息(无需appmsg_token和cookie)
comments = test.get_comments(link)
# 获取文章阅读数点赞数
read_num, like_num = test.get_read_like_num(link)
# 保存操作暂时不开发
```

## TO-DO

1. 整合API, 通过搜索公众号直接获取文章阅读数等信息， 搜索公众号文章关键词直接获取文章阅读数信息