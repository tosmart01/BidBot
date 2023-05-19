# -- coding: utf-8 --
# @Time : 2023/5/19 10:39
# @Author : zhuo.wang
# @File : tools.py
import settings


def get_proxy():
    entry = ('http://customer-%s:%s@cn-pr.oxylabs.io:30000' % (settings.PROXY_USERNAME, settings.PROXY_PASSWORD))
    return {
        'http': entry,
        'https': entry,
    }