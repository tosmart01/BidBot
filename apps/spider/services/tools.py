# -- coding: utf-8 --
# @Time : 2023/5/19 17:28
# @Author : zhuo.wang
# @File : tools.py

from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

def update_url_params(url, params):
    # 将URL解析为其组成部分
    url_parts = urlparse(url)

    # 获取URL中的查询参数
    query_params = parse_qs(url_parts.query)

    # 更新参数字典
    query_params.update(params)

    # 将参数字典转换为URL编码的字符串
    encoded_params = urlencode(query_params, doseq=True)

    # 创建更新后的URL组成部分
    modified_url_parts = list(url_parts)
    modified_url_parts[4] = encoded_params

    # 构造最终的URL
    modified_url = urlunparse(modified_url_parts)

    return modified_url
