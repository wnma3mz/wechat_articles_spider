# coding: utf-8
import time
import pdfkit

url = article_url
title = title
# https://github.com/wkhtmltopdf/wkhtmltopdf
config=pdfkit.configuration(wkhtmltopdf=r"D:\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
pdfkit.from_url(url, '{}.pdf'.format(title),configuration=config)
