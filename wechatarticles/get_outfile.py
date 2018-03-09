# coding: utf-8
import urllib
import sys
from mitmproxy import io, http


# 使用命令行过滤规则
# command: mitmdump -s get_outfile.py -w outfile mp.weixin.qq.com/mp/getappmsgext
class Writer:
    def __init__(self, path: str) -> None:
        self.f = open(path, "wb")
        self.w = io.FlowWriter(self.f)

    def response(self, flow: http.HTTPFlow) -> None:
        self.w.add(flow)
        url = urllib.parse.unquote(flow.request.url)
        if "mp.weixin.qq.com/mp/getappmsgext" in url:
            exit()

    def done(self):

        self.f.close()


addons = [Writer(sys.argv[1])]
