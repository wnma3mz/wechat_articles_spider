# coding: utf-8
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wechatarticles",
    version="0.4.3",
    author="wnma3mz",
    author_email="wnma3mz@gmail.com",
    description="wechat articles scrapy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wnma3mz/wechat_articles_spider",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests>=2.20.0', 'matplotlib>=2.0.2', 'Pillow>=6.2.0',
        'pymongo>=3.4.0', 'mitmproxy>=4.0.4'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)