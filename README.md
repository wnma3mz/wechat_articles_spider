# 微信公众号文章爬虫

步骤:

1. 从微信公众号平台获取微信公众所有文章的url

2. 登录微信PC端获取文章的阅读数、评论等信息

具体可以参考: [微信公众号爬虫](http://blog.csdn.net/wnma3mz/article/details/78570580)

## 第三方包

- `requests`: 爬取内容

- `matplotlib`: 用于显示二维码图片

- `PIL`: 用于显示二维码图片


## API操作

```python
# 导入模块
from wechatarticles import OfficialWeChat
from wechatarticles import LoginWeChat

# 初始化一些参数， username用户账号、password用户密码需要爬取的公众号
username = username
password = password
nickname = nickname

# 实例化爬取对象
test = OfficialWeChat(username, password)
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

1. 完善登录公众号平台API

2. 模拟登录微信PC端

## 获取微信公众号网页的cookie和token

1. 拥有一个微信个人订阅号，附上登陆和注册链接。[微信公众平台](https://mp.weixin.qq.com/)

2. 登录公众号之后，打开浏览器的**开发者选项**(F12), 推荐Chrome或者Firefox。

3. 刷新网页，在开发者工具里面，选择**Network**。如下图位置分别找到Cookie和token, 复制到代码中即可


![description_one](https://raw.githubusercontent.com/wnma3mz/wechat_articles_spider/master/img/description_one.png)