# 微信公众号文章爬虫

步骤:

1. 从微信公众号平台获取微信公众所有文章的url

2. 登录微信PC端获取文章的阅读数、评论等信息

具体可以参考: [微信公众号爬虫](http://blog.csdn.net/wnma3mz/article/details/78570580)

## 第三方包

- `requests`: 爬取内容

- `matplotlib`: 用于显示二维码图片(非必要)

- `PIL`: 用于显示二维码图片(非必要)


## API操作

### 支持两种爬虫方式

下面登录方式选用其一即可

1. 账号密码爬虫，输入账号密码后，扫描二维码登录。自动获取cookie和token，此种方式需要安装`matplotlib`和`PIL`

2. cookie、token爬虫，手动复制cookie和token。具体cookie和token获取方式见底部说明

```python
# 导入模块
from wechatarticles import OfficialWeChat
from wechatarticles import LoginWeChat

"""
初始化一些参数
username: 用户账号
password: 用户密码
cookie: 登录后获取的cookie
token: 登录后获取的token
nickname: 需要爬取的公众号
"""
username = username
password = password
cookie = yourcookie
token = token
nickname = nickname

# 实例化爬取对象

# 账号密码自动获取cookie和token
test = OfficialWeChat(username=usernmae, password=password)
# 手动输入账号密码
test = OfficialWeChat(cookie=cookie, token=token)

# 获取公众号文章总数
articles_sum = test.totalNums(nickname)
# 实例化爬取对象
test = OfficialWeChat(token, cookie)
# 获取公众号文章总数
articles_sum = test.totalNums(nickname)
# 获取公众号部分文章信息
artiacle_data = test.get_articles(nickname, begin="10", count="5")
# 获取公众号的一些信息
officical_info = test.get_official_info(nickname)
# 保存数据为txt格式
test.save_txt("test.txt", artiacle_data)
# 保存数据为sqlite3
test.save_sqlite("test.db", "test", artiacle_data)
```

```python
# 输出
print("articles_sum:", articles_sum)
print("artcles_data:")
pprint(artiacle_data)
print("officical_info:")
pprint(officical_info)
```

## TO-DO

1. 支持cookie的保留

2. 模拟登录微信PC端

## 获取微信公众号网页的cookie和token

1. 拥有一个微信个人订阅号，附上登陆和注册链接。[微信公众平台](https://mp.weixin.qq.com/)

2. 登录公众号之后，打开浏览器的**开发者选项**(F12), 推荐Chrome或者Firefox。

3. 刷新网页，在开发者工具里面，选择**Network**。如下图位置分别找到Cookie和token, 复制到代码中即可


![description_one](https://raw.githubusercontent.com/wnma3mz/wechat_articles_spider/master/img/description_one.png)