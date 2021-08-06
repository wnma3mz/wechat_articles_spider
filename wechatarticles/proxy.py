# coding:utf-8
import logging
import os
import select
import zlib

import chardet
import time
from http.client import HTTPResponse
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, ParseResult, urlunparse
from tempfile import gettempdir

from ssl import wrap_socket, SSLError
from socket import socket
from OpenSSL.crypto import (
    load_certificate,
    FILETYPE_PEM,
    TYPE_RSA,
    PKey,
    X509,
    X509Extension,
    dump_privatekey,
    dump_certificate,
    load_privatekey,
    X509Req,
)

"""
该文件并未项目核心功能，仅作辅助脚本使用
感谢baseproxy项目。原项目地址https://github.com/qiyeboy/BaseProxy，具体详细操作方法请见原项目，步骤简述如下
    1. 设置代理，开启服务
    2. 下载证书http://baseproxy.ca/，并安装至本机(受信任的根证书颁发机构)
    3. 配置完成，每次使用之前开启系统代理即可
为方便使用，在代码上进行了一定的修改，大部分内容来源于，https://github.com/qiyeboy/BaseProxy/blob/master/baseproxy/proxy.py
    1. 修改部分函数名，变量名，函数，尽量保持与mitmproxy一致
    2. 由于项目主要目的是拦截，并非篡改，增加了对链接过滤功能。若链接不包含相关字符，则不做操作，直接返回。ProxyHandle中的`self.filter_url_lst`


二次引用，若有冒犯原作者之处，敬请指出，将删除该文件。
"""

__all__ = [
    "CAAuth",
    "ProxyHandle",
    "ReqIntercept",
    "RspIntercept",
    "MitmProxy",
    "AsyncMitmProxy",
    "Request",
    "Response",
]
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class HttpTransfer(object):
    version_dict = {9: "HTTP/0.9", 10: "HTTP/1.0", 11: "HTTP/1.1"}

    def __init__(self):
        self.hostname = None
        self.port = None

        self.url = ""  # 无协议头
        # 这是请求
        self.command = None
        self.path = None
        self.request_version = None

        # 这是响应
        self.response_version = None
        self.status = None
        self.reason = None

        self._headers = None

        self._body = b""

    def parse_headers(self, headers_str):
        """
        暂时用不到
        :param headers:
        :return:
        """
        header_list = headers_str.rstrip("\r\n").split("\r\n")
        headers = {}
        for header in header_list:
            [key, value] = header.split(": ")
            headers[key.lower()] = value
        return headers

    def to_data(self):
        raise NotImplementedError("function to_data need override")

    def set_headers(self, headers):
        headers_tmp = {}
        for k, v in headers.items():
            headers_tmp[k.lower()] = v
        self._headers = headers_tmp

    def build_headers(self):
        """
        返回headers字符串
        :return:
        """
        header_str = ""
        for k, v in self._headers.items():
            header_str += k + ": " + v + "\r\n"

        return header_str

    def get_header(self, key):
        if isinstance(key, str):
            return self._headers.get(key.lower(), None)
        raise Exception("parameter should be str")

    @property
    def headers(self):
        """
        获取头部信息
        :return:
        """
        return self._headers

    def set_header(self, key, value):
        """
        设置头部
        :param key:
        :param value:
        :return:
        """
        if isinstance(key, str) and isinstance(value, str):
            self._headers[key.lower()] = value
            return
        raise Exception("parameter should be str")

    def get_body_data(self):
        """
        返回是字节格式的body内容
        :return:
        """
        return self._body

    def set_body_data(self, body):
        if isinstance(body, bytes):
            self._body = body
            self.set_header("Content-length", str(len(body)))
            return
        raise Exception("parameter should be bytes")


class Request(HttpTransfer):
    def __init__(self, req):
        HttpTransfer.__init__(self)

        self.hostname = req.hostname
        self.port = req.port
        # 这是请求
        self.command = req.command
        self.path = req.path
        self.request_version = req.request_version

        self.url = req.hostname + req.path

        self.set_headers(req.headers)

        if self.get_header("Content-Length"):
            self.set_body_data(req.rfile.read(int(self.get_header("Content-Length"))))

    def to_data(self):
        # Build request
        req_data = "%s %s %s\r\n" % (self.command, self.path, self.request_version)
        # Add headers to the request
        req_data += "%s\r\n" % self.build_headers()
        req_data = req_data.encode("utf-8")
        req_data += self.get_body_data()
        return req_data


class Response(HttpTransfer):
    def __init__(self, request, proxy_socket):

        HttpTransfer.__init__(self)

        self.request = request

        h = HTTPResponse(proxy_socket)
        h.begin()
        ##HTTPResponse会将所有chunk拼接到一起，因此会直接得到所有内容，所以不能有Transfer-Encoding
        del h.msg["Transfer-Encoding"]
        del h.msg["Content-Length"]

        self.response_version = self.version_dict[h.version]
        self.status = h.status
        self.reason = h.reason
        self.set_headers(h.msg)

        body_data = self._decode_content_body(
            h.read(), self.get_header("Content-Encoding")
        )
        self.set_body_data(body_data)
        self._text()  # 尝试将文本进行解码

        h.close()
        proxy_socket.close()

    def _text(self):
        body_data = self.get_body_data()
        if self.get_header("Content-Type") and (
            "text" or "javascript"
        ) in self.get_header("Content-Type"):
            self.decoding = chardet.detect(body_data)["encoding"]  # 探测当前的编码
            if self.decoding:
                try:
                    self._body_str = body_data.decode(self.decoding)  # 请求体
                except Exception as e:
                    self._body_str = body_data
                    self.decoding = None
            else:
                self._body_str = body_data
        else:
            self._body_str = body_data
            self.decoding = None

    def get_text(self, decoding=None):
        if decoding:
            return self.get_body_data().decode(decoding)
        return self.get_body_data().decode()

    def set_body_str(self, body_str, encoding=None):
        if isinstance(body_str, str):
            if encoding:
                self.set_body_data(body_str.encode(encoding))
            else:
                self.set_body_data(
                    body_str.encode(self.decoding if self.decoding else "utf-8")
                )
            self._body_str = body_str
            return
        raise Exception("parameter should be str")

    def _encode_content_body(self, text, encoding):

        if encoding == "identity":
            data = text
        elif encoding in ("gzip", "x-gzip"):

            gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
            data = gzip_compress.compress(text) + gzip_compress.flush()

        elif encoding == "deflate":
            data = zlib.compress(text)
        else:
            data = text

        return data

    def _decode_content_body(self, data, encoding):
        if encoding == "identity":  # 没有压缩
            text = data

        elif encoding in ("gzip", "x-gzip"):  # gzip压缩
            text = zlib.decompress(data, 16 + zlib.MAX_WBITS)
        elif encoding == "deflate":  # zip压缩
            try:
                text = zlib.decompress(data)
            except zlib.error:
                text = zlib.decompress(data, -zlib.MAX_WBITS)
        else:
            text = data

        self.set_header("Content-Encoding", "identity")  # 没有压缩
        return text

    def to_data(self):

        res_data = "%s %s %s\r\n" % (self.response_version, self.status, self.reason)
        res_data += "%s\r\n" % self.build_headers()
        res_data = res_data.encode(self.decoding if self.decoding else "utf-8")
        res_data += self.get_body_data()
        return res_data


class CAAuth(object):
    """
    用于CA证书的生成以及代理证书的自签名
    """

    def __init__(self, ca_file="ca.pem", cert_file="ca.crt"):
        self.ca_file_path = ca_file
        self.cert_file_path = cert_file
        self._gen_ca()  # 生成CA证书，需要添加到浏览器的合法证书机构中

    def _gen_ca(self, again=False):
        # Generate key
        # 如果证书存在而且不是强制生成，直接返回证书信息
        if (
            os.path.exists(self.ca_file_path)
            and os.path.exists(self.cert_file_path)
            and not again
        ):
            self._read_ca(self.ca_file_path)  # 读取证书信息
            return
        self.key = PKey()
        self.key.generate_key(TYPE_RSA, 2048)
        # Generate certificate
        self.cert = X509()
        self.cert.set_version(2)
        self.cert.set_serial_number(1)
        self.cert.get_subject().CN = "baseproxy"
        self.cert.gmtime_adj_notBefore(0)
        self.cert.gmtime_adj_notAfter(315360000)  # 十年
        self.cert.set_issuer(self.cert.get_subject())
        self.cert.set_pubkey(self.key)
        self.cert.add_extensions(
            [
                X509Extension(b"basicConstraints", True, b"CA:TRUE, pathlen:0"),
                X509Extension(b"keyUsage", True, b"keyCertSign, cRLSign"),
                X509Extension(
                    b"subjectKeyIdentifier", False, b"hash", subject=self.cert
                ),
            ]
        )
        self.cert.sign(self.key, "sha256")
        with open(self.ca_file_path, "wb+") as f:
            f.write(dump_privatekey(FILETYPE_PEM, self.key))
            f.write(dump_certificate(FILETYPE_PEM, self.cert))

        with open(self.cert_file_path, "wb+") as f:
            f.write(dump_certificate(FILETYPE_PEM, self.cert))

    def _read_ca(self, file):
        self.cert = load_certificate(FILETYPE_PEM, open(file, "rb").read())
        self.key = load_privatekey(FILETYPE_PEM, open(file, "rb").read())

    def __getitem__(self, cn):
        # 将为每个域名生成的服务器证书，放到临时目录中
        cache_dir = gettempdir()
        root_dir = os.path.join(cache_dir, "baseproxy")
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)

        cnp = os.path.join(root_dir, "baseproxy_{}.pem".format(cn))

        if not os.path.exists(cnp):
            self._sign_ca(cn, cnp)
        return cnp

    def _sign_ca(self, cn, cnp):
        # 使用合法的CA证书为代理程序生成服务器证书
        # create certificate
        try:

            key = PKey()
            key.generate_key(TYPE_RSA, 2048)

            # Generate CSR
            req = X509Req()
            req.get_subject().CN = cn
            req.set_pubkey(key)
            req.sign(key, "sha256")

            # Sign CSR
            cert = X509()
            cert.set_version(2)
            cert.set_subject(req.get_subject())
            cert.set_serial_number(self.serial)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(31536000)  # 一年
            cert.set_issuer(self.cert.get_subject())
            ss = ("DNS:%s" % cn).encode(encoding="utf-8")

            cert.add_extensions([X509Extension(b"subjectAltName", False, ss)])

            cert.set_pubkey(req.get_pubkey())
            cert.sign(self.key, "sha256")

            with open(cnp, "wb+") as f:
                f.write(dump_privatekey(FILETYPE_PEM, key))
                f.write(dump_certificate(FILETYPE_PEM, cert))
        except Exception as e:
            raise Exception("generate CA fail:{}".format(str(e)))

    @property
    def serial(self):
        return int("%d" % (time.time() * 1000))


class ProxyHandle(BaseHTTPRequestHandler):
    def __init__(self, request, client_addr, server):
        self.is_connected = False
        self.hook_init()
        BaseHTTPRequestHandler.__init__(self, request, client_addr, server)

    def hook_init(self):
        # 增加初始化的其他操作，如初始化filter_url_lst
        self.filter_url_lst = []

    def do_CONNECT(self):
        """
        处理https连接请求
        :return:
        """

        self.is_connected = True  # 用来标识是否之前经历过CONNECT
        if self.server.https:
            self.connect_intercept()
        else:
            self.connect_relay()

    def do_GET(self):
        """
        处理GET请求
        :return:
        """
        if self.path == "http://baseproxy.ca/":
            self._send_ca()
            return

        if not self.is_connected:
            # 如果不是https，需要连接http服务器
            try:
                self._proxy_to_dst()
            except Exception as e:
                self.send_error(500, "{} connect fail ".format(self.hostname))
                return
        # 这里就是代理发送请求，并接收响应信息
        request = Request(self)
        # 增加过滤模块
        flag = False
        for filter_x in self.filter_url_lst:
            if filter_x in request.url:
                flag = True
                break
        if flag:
            request = self.mitm_request(request)

        if request:
            self._proxy_sock.sendall(request.to_data())
            # 将响应信息返回给客户端
            response = Response(request, self._proxy_sock)
            if flag:
                response = self.mitm_response(response)

            if response:
                self.request.sendall(response.to_data())
            else:
                self.send_error(404, "response is None")
        else:
            self.send_error(404, "request is None")

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET
    do_OPTIONS = do_GET

    def _proxy_to_ssldst(self):
        """
        代理连接https目标服务器
        :return:
        """
        ##确定一下目标的服务器的地址与端口

        # 如果之前经历过connect
        # CONNECT www.baidu.com:443 HTTP 1.1
        self.hostname, self.port = self.path.split(":")
        self._proxy_sock = socket()
        self._proxy_sock.settimeout(10)
        self._proxy_sock.connect((self.hostname, int(self.port)))
        # 进行SSL包裹
        self._proxy_sock = wrap_socket(self._proxy_sock)

    def _proxy_to_dst(self):
        # 代理连接http目标服务器
        # http请求的self.path 类似http://www.baidu.com:80/index.html
        u = urlparse(self.path)
        if u.scheme != "http":
            raise Exception("Unknown scheme %s" % repr(u.scheme))
        self.hostname = u.hostname
        self.port = u.port or 80
        # 将path重新封装，比如http://www.baidu.com:80/index.html会变成 /index.html
        self.path = urlunparse(
            ParseResult(
                scheme="",
                netloc="",
                params=u.params,
                path=u.path or "/",
                query=u.query,
                fragment=u.fragment,
            )
        )
        self._proxy_sock = socket()
        self._proxy_sock.settimeout(10)
        self._proxy_sock.connect((self.hostname, int(self.port)))

    def connect_intercept(self):
        """
        需要解析https报文,包装socket
        :return:
        """
        try:
            # 首先建立和目标服务器的链接
            self._proxy_to_ssldst()
            # 建立成功后,proxy需要给client回复建立成功
            self.send_response(200, "Connection established")
            self.end_headers()

            # 这个时候需要将客户端的socket包装成sslsocket,这个时候的self.path类似www.baidu.com:443，根据域名使用相应的证书
            self.request = wrap_socket(
                self.request,
                server_side=True,
                certfile=self.server.ca[self.path.split(":")[0]],
            )
        except SSLError:
            self.send_error(500, "更新证书!")
            return
        except Exception as e:
            self.send_error(500, str(e))
            return

        self.setup()
        self.ssl_host = "https://%s" % self.path
        try:
            self.handle_one_request()
        except Exception as e:
            return

    def connect_relay(self):
        """
        对于https报文直接转发
        """

        self.hostname, self.port = self.path.split(":")
        try:
            self._proxy_sock = socket()
            self._proxy_sock.settimeout(10)
            self._proxy_sock.connect((self.hostname, int(self.port)))
        except Exception as e:
            self.send_error(500)
            return

        self.send_response(200, "Connection Established")
        self.end_headers()

        inputs = [self.request, self._proxy_sock]

        while True:
            readable, writeable, errs = select.select(inputs, [], inputs, 10)
            if errs:
                break
            for r in readable:
                data = r.recv(8092)
                if data:
                    if r is self.request:
                        self._proxy_sock.sendall(data)
                    elif r is self._proxy_sock:
                        self.request.sendall(data)
                else:
                    break
        self.request.close()
        self._proxy_sock.close()

    def _send_ca(self):
        # 发送CA证书给用户进行安装并信任
        cert_path = self.server.ca.cert_file_path
        with open(cert_path, "rb") as f:
            data = f.read()

        self.send_response(200)
        self.send_header("Content-Type", "application/x-x509-ca-cert")
        self.send_header("Content-Length", len(data))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(data)

    def mitm_request(self, req):
        for p in self.server.req_plugs:
            req = p(self.server).deal_request(req)
        return req

    def mitm_response(self, rsp):
        for p in self.server.rsp_plugs:
            rsp = p(self.server).deal_response(rsp)
        return rsp


class MitmProxy(ThreadingMixIn, HTTPServer):
    def __init__(
        self,
        server_addr=("", 8080),
        RequestHandlerClass=ProxyHandle,
        bind_and_activate=True,
        https=True,
        ca_file="ca.pem",
        cert_file="ca.crt",
    ):
        HTTPServer.__init__(self, server_addr, RequestHandlerClass, bind_and_activate)
        logging.info(
            "HTTPServer is running at address( %s , %d )......"
            % (server_addr[0], server_addr[1])
        )
        self.req_plugs = []  ##请求拦截插件列表
        self.rsp_plugs = []  ##响应拦截插件列表
        self.ca = CAAuth(ca_file=ca_file, cert_file=cert_file)
        self.https = https

    def register(self, intercept_plug):
        if not issubclass(intercept_plug, InterceptPlug):
            raise Exception(
                "Expected type InterceptPlug got %s instead" % type(intercept_plug)
            )

        if issubclass(intercept_plug, ReqIntercept):
            self.req_plugs.append(intercept_plug)

        if issubclass(intercept_plug, RspIntercept):
            self.rsp_plugs.append(intercept_plug)


class AsyncMitmProxy(MitmProxy):
    pass


class InterceptPlug(object):
    def __init__(self, server):
        self.server = server


class ReqIntercept(InterceptPlug):
    def deal_request(self, request):
        pass


class RspIntercept(InterceptPlug):
    def deal_response(self, response):
        pass
