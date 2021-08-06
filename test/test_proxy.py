# coding:utf-8
from wechatarticles.proxy import ReqIntercept, RspIntercept, MitmProxy, ProxyHandle
import re
import urllib


"""
此文件仅供参考学习，运行若有问题概不答疑

需要额外手动创建params文件夹

证书生成note
openssl req -newkey rsa:2048 -nodes -keyout CA_private.pem -x509 -subj "/CN=MY_CA" -days 365 -out CA_cert.crt
openssl genrsa -out client.pem 1024
openssl x509  -req -days 3650 -in client.csr -CA CA_cert.crt -CAkey CA_private.pem  -CAcreateserial -out client.crt
openssl genrsa -out server.pem 1024
openssl req -new -key server.pem -out server.csr -subj "/CN=server"
openssl x509  -req -days 3650 -in server.csr -CA CA_cert.crt -CAkey CA_private.pem  -CAcreateserial -out server.crt

证书使用的是原项目的，若对安全性要求高，建议重新生成
"""


class MyProxyHandle(ProxyHandle):
    def hook_init(self):
        self.filter_url_lst = [
            "mp.weixin.qq.com/mp",
            "mp.weixin.qq.com/s",
            "weread.qq.com/",
        ]


def get_request(response):
    data = response.request
    if "Cookie" in data.headers.keys():
        cookies = data.headers["Cookie"]
    elif "cookie" in data.headers.keys():
        cookies = data.headers["cookie"]
    else:
        cookies = ""
    return cookies, data.url, response.get_text()


def parse_params(url):
    nickname = re.findall("__biz=(.+?)&", url)[0]  # 此处仅作占位标识，同biz表示
    biz = re.findall("__biz=(.+?)&", url)[0]
    key = re.findall("key=(.+?)&", url)[0]
    uin = re.findall("uin=(.+?)&", url)[0]
    uin = urllib.parse.unquote(uin)
    nickname = urllib.parse.unquote(nickname)
    biz = urllib.parse.unquote(biz)
    return biz, nickname, uin, key


class DebugInterceptor(ReqIntercept, RspIntercept):
    def deal_request(self, request):
        return request

    def deal_response(self, response):
        url = response.request.url
        try:
            # 历史文章链接
            if "mp.weixin.qq.com/mp/profile_ext" in url and "action=home" in url:
                cookies, url, text = get_request(response)
                with open("history_url.txt", "w", encoding="utf-8") as f:
                    f.write(
                        text.split("var msgList = '")[1]
                        .split("';")[0]
                        .replace("&quot;", '"')
                        .replace("amp;", "")
                    )
                nickname = text.split('nickname = "')[1].split('".html(false) || "";')[
                    0
                ]
                biz, _, uin, key = parse_params(url)


            if "mp.weixin.qq.com/mp/getappmsgext" in url and "biz" in url:
                cookies, url, _ = get_request(response)
                appmsg_token = re.findall("appmsg_token=(.+?)&", url)[0]
                print("cookie = '{}'".format(cookies))
                print("appmsg_token = r'{}'".format(appmsg_token))
                with open("params/cookie_token.txt", "w", encoding="utf-8") as f:
                    f.write(cookies + "\n")
                    f.write(appmsg_token)

            # 评论
            if "mp.weixin.qq.com/mp/appmsg_comment" in url and "biz" in url:
                _, _, text = get_request(response)
                with open("comment.txt", "w", encoding="utf-8") as f:
                    f.write(text)
        except:
            pass

        return response


def run(port=8080):
    baseproxy = MitmProxy(
        server_addr=("", port),
        RequestHandlerClass=MyProxyHandle,
        bind_and_activate=True,
        https=True,
        ca_file="ca.pem",
        cert_file="ca.crt",
    )
    baseproxy.register(DebugInterceptor)
    baseproxy.serve_forever()


if __name__ == "__main__":
    run()