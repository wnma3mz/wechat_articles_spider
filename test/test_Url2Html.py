# coding: utf-8
import os
from pprint import pprint
from wechatarticles import Url2Html

if __name__ == "__main__":
    # 微信文章下载为离线HTML（含图片）
    # 微信文章的url
    url = "https://mp.weixin.qq.com/s?__biz=MzUzNjk1NDIyNg==&mid=2247506248&idx=1&sn=c9a8b4d2e11fd1b6ae924877da3f0ea8&chksm=faeccd55cd9b44432ea81578b1e33db2ae5ce938ed5a90e32847cb0ea88916a16ac47c92e135&scene=132#wechat_redirect"
    uh = Url2Html()
    # 请提前创建一个以公众号为名的文件夹，并且在该文件夹下创建imgs文件夹
    res = uh.run(url, mode=4, img_path="./黑马青年/imgs")
    print(res)
