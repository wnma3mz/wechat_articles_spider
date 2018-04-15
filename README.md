# 微信公众号文章爬虫

实现思路:

1. 从微信公众号平台获取微信公众所有文章的url

2. 登录微信PC端获取文章的阅读数、评论等信息

完整思路可以参考我的博客: [微信公众号爬虫](http://blog.csdn.net/wnma3mz/article/details/78570580)

## python版本

- `python`: 3.6.2

### 第三方包

- `requests`: 爬取内容

详情见[requirements.txt](https://github.com/wnma3mz/wechat_articles_spider/blob/master/requirements.txt)

## 功能实现

- 获取某公众号信息

- 获取某公众号所有文章数量

- 获取某公众号所有文章信息（包含点赞数、阅读数、评论信息），需要手动更改循环

- 获取某公众号指定文章的信息

- 支持两种微信公众号登录方式, 下面方法选用其一即可

    1. 账号密码爬虫，输入账号密码后，扫描二维码登录。自动获取cookie和token。此方法需要安装`matplotlib`和`PIL`用于显示二维码图片

    2. cookie、token登录，手动复制cookie和token。

- 支持两种获取文章阅读数和点赞数的方式，下面方式选用其一即可

    1. 利用抓包工具手动获取

    2. 安装python第三方库`mitmproxy`自动获取

- 支持存储方式

    1. txt存储（不建议）

    2. mongo存储。需要安装`pymongo`

## 变量名的说明

|     变量名      |        作用        |
| :-------------: | :----------------: |
|    usernmae     |  个人公众号的账号  |
|    password     |  个人公众号的密码  |
| official_cookie | 个人公众号的cookie |
|    token     |  个人公众号的token  |
|    appmsg_token     |  个人微信号的appmsg_token  |
| wechat_cookie | 个人微信号的cookie |
|    nickname     |  需要获取文章的公众号名称  |
|    query     | 筛选公众号文章的关键词  |
| outfile | mitmproxy抓包获取请求的保存文件 |
| begin | 从第几篇文章开始爬取 |
| count | 每次爬取的文章数(最大为5, 但是返回结果可能会大于５) |

## API实例

以下完整事例代码见`test/`目录下的实例代码。

official_cookie和token手动获取方式见[这篇文档](https://github.com/wnma3mz/wechat_articles_spider/blob/master/docs/get_cookie_token.md)

wechat_cookie和appmsg_token手动获取的介绍，可以参考[这篇文档](https://github.com/wnma3mz/wechat_articles_spider/blob/master/docs/get_appmsg_token.md)

wechat_cookie和appmsg_token自动获取的介绍(需要安装`mitmproxy`)，可以参考[这篇文档](https://github.com/wnma3mz/wechat_articles_spider/blob/master/docs/关于自动获取微信参数.md)。默认开放端口为8080。


wechat_cookie和appmsg_token建议获取每天或者每半天获取一次即可。此处通过上面获取到的url即可无限爬取，没有次数限制

```python
# 导入模块
import sys
sys.path.append(path + "/wechat_articles_spider")
from wechatarticles import OfficialWeChat
from wechatarticles import LoginWeChat
from wechatarticles import ReadOutfile
from wechatarticles import ArticlesAPI
```

### 一次性获取文章的信息(阅读、点赞、评论信息)

```python
# 下面三种方式任选一种即可

# 手动输入所有参数
test = ArticlesAPI(
    official_cookie=official_cookie,
    token=token,
    appmsg_token=appmsg_token,
    wechat_cookie=wechat_cookie)

# 输入账号密码，自动登录公众号，手动输入appmsg_token和wechat_cookie
test = ArticlesAPI(
    username=username,
    password=password,
    appmsg_token=appmsg_token,
    wechat_cookie=wechat_cookie)

# 手动输入official_cookie和token, 自动获取appmsg_token和wechat_cookie
test = ArticlesAPI(
    official_cookie=official_cookie, token=token, outfile=outfile)

# 自定义爬取，每次爬取5篇以上
data = test.complete_info(nickname=nickname, begin="0")

# 自定义从某部分开始爬取，持续爬取，直至爬取失败为止，一次性最多爬取40篇（功能未测试，欢迎尝试）
datas = test.continue_info(nickname=nickname, begin="0")

```

### 分解步骤
#### 步骤一: 获取公众号的所有文章url

此处有次数限制，不可一次获取太多url(获取超过30、40条貌似就会失败)。解决方案多个账号同时爬取

```python
# 实例化爬取对象
# 账号密码自动获取cookie和token
test = ArticlesUrls(username=username, password=password)
# 手动输入账号密码
test = ArticlesUrls(cookie=official_cookie, token=token)

# 输入公众号名称，获取公众号文章总数
articles_sum = test.articles_nums(nickname)
# 输入公众号名称，获取公众号部分文章信息, 每次最大返回数为5个
articles_data = test.articles(nickname, begin="0", count="5")
# 输入公众号名称，获取公众号的一些信息
officical_info = test.official_info(nickname)
# 输入公众号名称，输入关键词，获取公众号相关文章信息, 每次最大返回数为5个
articles_data_query = test.articles(nickname, query=query, begin="0", count="5")
# 输入公众号名称，输入关键词，获取公众号相关文章总数
articles_sum_query = test.articles_nums(nickname, query=query)
```

#### 步骤二：登录微信PC端获取文章信息

```python
# 支持自动获取appmsg_token和cookie
appmsg_token, cookie = Reader().contral(outfile)

# 实例化爬取对象
# 账号密码自动获取cookie和token
test = ArticlesInfo(appmsg_token=appmsg_token, cookie=wechat_cookie)
# 获取文章所有的评论信息(无需appmsg_token和cookie)
comments = test.comments(link)
# 获取文章阅读数点赞数
read_num, like_num = test.read_like_nums(link)
```

## TO-DO

- [ ] 完善API设计

- [ ] 增加协程`asyncio`

- [ ] 发布第三方包