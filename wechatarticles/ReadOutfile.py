# coding: utf-8
from mitmproxy import io
from mitmproxy.exceptions import FlowReadException
import re
import os


# 获取appmsg_token, cookie
# command: python get_params outfile
class Reader:
    def __init__(self) -> None:
        pass
        # self.f = open(path, "rb")
        # self.w = io.FlowWriter(self.f)

    def __request(self, outfile):
        with open(outfile, "rb") as logfile:
            freader = io.FlowReader(logfile)
            try:
                for f in freader.stream():
                    # 获取完整的请求信息
                    state = f.get_state()
                    # 尝试获取cookie和appmsg_token,如果成功就停止
                    try:
                        # 截取其中request部分
                        request = state["request"]
                        # 提取Cookie
                        for item in request["headers"]:
                            key, value = item
                            if key == b"Cookie":
                                cookie = value.decode()

                        # 提取appmsg_token
                        path = request["path"].decode()
                        appmsg_token_string = re.findall("appmsg_token.+?&", path)
                        appmsg_token = appmsg_token_string[0].split("=")[1][:-1]
                        break
                    except Exception:
                        continue
            except FlowReadException as e:
                print("Flow file corrupted: {}".format(e))
            return appmsg_token, cookie

    # def __done(self):
    #     self.f.close()

    def contral(self, outfile):
        path = os.path.split(os.path.realpath(__file__))[0]
        command = "mitmdump -q -s {}/get_outfile.py -w {} mp.weixin.qq.com/mp/getappmsgext".format(
            path, outfile)
        os.system(command)
        try:
            os.system("rm ./-q")
        except Exception:
            pass
        return self.__request(outfile)
