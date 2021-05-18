# 微信公众号文章爬虫（微信文章阅读点赞的获取）

![](https://img.shields.io/pypi/v/wechatarticles)![](https://img.shields.io/pypi/l/wechatarticles)[![](https://img.shields.io/badge/docs-building-blue)](https://wnma3mz.github.io/wechat_articles_spider/build/html/index.html)

安装

`pip install wechatarticles`

展示地址：

[日更，获取公众号的最新文章链接](https://data.wnma3mz.cn/demo.html)，支持日更阅读点赞评论正文

技术交流可以直接联系，微信二维码见末尾（微信；wnma3mz)。烦请进行备注，如wechat_spider

注：本项目仅供学习交流，严禁用于商业用途（该项目也没法直接使用），不能达到开箱即用的水平。使用本项目需要读文档+源码+动手实践，参考示例代码（`test`文件夹下）进行改写。

提示：另外，已经有很多朋友（大佬）通过直接看源码，已经基于这套项目，或者重写，用于各自的需求。

实现思路一:

1. 从微信公众号平台获取微信公众所有文章的url
2. 登录微信PC端或移动端获取文章的阅读数、点赞数、评论信息

完整思路可以参考我的博客: [记一次微信公众号爬虫的经历（微信文章阅读点赞的获取）](https://wnma3mz.github.io/hexo_blog/2017/11/18/记一次微信公众号爬虫的经历（微信文章阅读点赞的获取）/)

实现思路二：

1. 登陆微信PC端或移动端获取公众号所有文章的url，这种获取到的url数量大于500，具体数量每个微信号不完全一致
2. 同上种方法，获取文章阅读数、点赞数、评论信息

公开已爬取的公众号历史文章的永久链接，日期均截止commit时间，仅供测试与学习，欢迎各位关注这些优质公众号。

<details>
  <summary>公众号列表</summary>
    <li>科技美学</li>
    <li>共青团中央</li>
    <li>南方周末</li>
    <li>AppSo</li>
</details>
## Notes

项目始于2017年，当前更新于2021年3月

项目代码进行调整，调用以前的接口请使用`pip install wechatarticles==0.5.8`。

1. 爬取失败的时候，可能有以下原因
   1. **运行的时候需要关闭网络代理（抓包软件），或者添加相关参数**
   2. 参数是否最新，获取微信相关参数（cookie、token）时，一定要保证是**对应公众号**的任意文章
   3. 检查代码
   4. 需要关注对应公众号（Maybe）
2. 思路一获取url时，每页间隔可以设定久一点，比如3分钟，持续时间几小时（来自网友测试）
3. 获取文章阅读点赞时，每篇文章可以设定在5-10s左右，过期时间为4小时；若被封，大约5-10分钟就可继续抓取。
4. 思路二获取url时，如果被封，需要24小时整之后才能重新抓取

参数文件说明见[README](https://github.com/wnma3mz/wechat_articles_spider/blob/master/docs)

## python版本

- `python`: 3.6.2、3.7.3

## 功能实现

<details>
  <summary>功能</summary>
    公众号相关
    <li>公众号信息</li>
    <li>公众号biz。获取方式：清博、公众号网页</li>
    <li>公众号发表文章数量（不完全准确）</li>
    文章相关
    <li>某公众号文章的url。获取方式：公众号网页、PC端微信、移动端微信、微信读书</li>
    <li>某公众号所有文章信息（包含点赞数、阅读数、评论信息），需要手动更改循环</li>
    <li>某公众号指定文章的信息</li>
    <li>支持微信文章下载至本地转为html（图片可选是否保存）</li>
</details>

## API实例

#### 利用公众号网页版获取微信文章url
此处有次数限制，不可一次获取太多url。解决方案多个账号同时爬取
[test_WechatUrls.py](https://github.com/wnma3mz/wechat_articles_spider/blob/master/test/test_WechatUrls.py)

#### 登录微信PC端获取文章信息（阅读点赞）
[test_WechatInfo.py](https://github.com/wnma3mz/wechat_articles_spider/blob/master/test/test_WechatInfo.py)

#### 快速获取大量文章urls（利用历史文章获取链接）
[test_GetUrls.py](https://github.com/wnma3mz/wechat_articles_spider/blob/master/test/test_GetUrls.py)

#### 微信文章下载为离线HTML（含图片）
[test_Url2Html.py](https://github.com/wnma3mz/wechat_articles_spider/blob/master/test/test_Url2Html.py)

#### 学习/运行流程

可以看这个[issue](https://github.com/wnma3mz/wechat_articles_spider/issues/38#issuecomment-817256654)，十分感谢大佬简洁的文字说明。

### 相关文档

见博客与下方文档

official_cookie和token手动获取方式见[这篇文档](https://github.com/wnma3mz/wechat_articles_spider/blob/master/docs/get_cookie_token.md)

wechat_cookie和appmsg_token手动获取的介绍，可以参考[这篇文档](https://github.com/wnma3mz/wechat_articles_spider/blob/master/docs/get_appmsg_token.md)

**联系注意事项**：

1. 不（能）做自动登录微信公众号、微信

2. 不（能）做实时（获取参数、阅读点赞、获取文章）

3. 换一个公众号、参数过期，均需手动更新，如何获取参数均在文章中提及，请仔细查阅

4. 不能做关键词搜索（即微信搜一搜功能），比如搜索所有含“科技”两个字的文章。

Q & A

1. 项目能不能正常运行？

     答：项目可正常运行。

2. xxx怎么运行/启动，需要获取哪些参数？

     答：请看源码，并手动运行看看输出报错。

3. xxx参数怎么获取？

     答：文档和博客均描述的很清楚，请仔细阅读。

4. 我要xxxx，需要怎么做？

     答：看文档，看源码

5. 网页每日更新的方式怎么做的？

     答：不是万能key。方案很简单，就是模拟点击+代理软件(Fiddler或Mitmproxy)拦截包，每日抓一次，如果你有更好的方案也欢迎告知。这部分未开源（如果有看到相关完整开源的可以提个issue学习一下），纯粹是因为配环境+定制化太麻烦，而且存在一定的问题。懂的看到这里能够实现的就能实现，如果问我我也不好回答你，太耗时耗力。

6. PC端微信与抓包软件Fiddler是必装的吗？

     答：不是。这个只是我了解(认为)到，这两个是相对最容易完成整个过程的。代替方案：可以抓手机端的微信（安卓和IOS均可，安卓的要root才能抓到阅读点赞）；抓包软件Fiddler这个可替代的很多，只要能进行HTTPS抓包查看数据就行。
     
7. 大量公众号的文章怎么抓？

     答：本项目无法实现。没很好的方案，参考5。切换一个公众号的时间成本大概要3-5分钟，视熟练程度而异。
     
     

附录：

问问题的正常方式：

1. 描述清楚你运行的系统环境、Python环境...（这步骤可选择性忽略）
2. 运行了什么代码（改动了哪部分），报了什么错（请完整截图）？
3. 自己根据报错做了哪些尝试？（文档中是否有描述？在网上搜索的解决方案有哪些）

编程是实践出真知，运行的正确与否可以**直接试出来**，没必要耽误两个人的时间。如果运行出了问题，请按照以上流程进行提问，**但前提是自己要运行过**。请**直接说问题or需求**，不需要等我回复再说。谢谢！大部分问题均可以交流，如果事无巨细的提问，也接受付费教学。

<figure class="third">
   微信二维码
<img src="https://i.loli.net/2019/09/20/14QGTkfgstDxv9C.jpg"  width="50%" id="wechat_account" /><img src="https://raw.githubusercontent.com/wnma3mz/wechat_articles_spider/master/imgs/wechat.jpg" width="260"><img src="https://raw.githubusercontent.com/wnma3mz/wechat_articles_spider/master/imgs/Alipay.jpg" width="260"><img src="https://raw.githubusercontent.com/wnma3mz/wechat_articles_spider/master/imgs/Alipay_redpaper.jpg" width="260">
</figure>