# -- coding: utf-8 --
# @Time : 2022-10-06 23:37:42
# @Author : zhuo.wang
# @File : __init__.py.py
from .base import *
from .log import *
sys.path.insert(0,os.path.join(BASE_DIR,'apps',))


import pymysql
pymysql.install_as_MySQLdb()

exec(f"from .{os.getenv('ENV','dev')} import *")
