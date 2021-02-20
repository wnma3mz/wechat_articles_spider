# coding: utf-8
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wechatarticles",
    version="0.6.1",
    author="wnma3mz",
    author_email="wnma3mz@gmail.com",
    description="wechat articles scrapy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wnma3mz/wechat_articles_spider",
    packages=setuptools.find_packages(),
    install_requires=["requests>=2.20.0", "beautifulsoup4>=4.7.1"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)
