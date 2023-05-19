# -- coding: utf-8 --
# @Time : 2021/12/4 6:06 下午
# @Author : zhuo.wang
# @File : log.py
from .base import *
BASE_LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(BASE_LOG_DIR):
    os.mkdir(BASE_LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(levelname)s][%(asctime)s][%(process)d:%(thread)d][%(filename)s:%(lineno)d]%(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],  # 只有在Django debug为True时才在屏幕打印日志
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'info': {
            'level': 'INFO',
            'filename': os.path.join(BASE_LOG_DIR, "info.log"),  # 日志文件
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'D',
            'interval': 1,
            'backupCount': 10,# 备份数为10
            'formatter': 'simple',
            'encoding': 'utf-8',
        },
        'error': {
            'level': 'INFO',
            'filename': os.path.join(BASE_LOG_DIR, "error.log"),  # 日志文件
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'D',
            'interval': 1,
            'backupCount': 20,# 备份数为10
            'formatter': 'simple',
            'encoding': 'utf-8',
        },
        'trading': {
            'level': 'INFO',
            'filename': os.path.join(BASE_LOG_DIR, "trading.log"),  # 日志文件
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'D',
            'interval': 1,
            'backupCount': 20,  # 备份数为10
            'formatter': 'simple',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'django': {  # 默认的logger应用如下配置
            'handlers': ['info', 'console',],
            'level': 'INFO',
            'propagate': True,
        },
        'gunicorn.access': {  # 默认的logger应用如下配置
            'handlers': ['info', 'console', ] if DEBUG else ['info'],  # 上线之后可以把'console'移除
            'level': 'INFO',
            'propagate': True,
        },
        'gunicorn.error': {  # 默认的logger应用如下配置
            'handlers': ['info', 'console', ] if DEBUG else ['info'],  # 上线之后可以把'console'移除
            'level': 'INFO',
            'propagate': True,
        },
        'info': {  #
            'handlers': ['info', 'console',],
            'level': 'INFO',
        },
        'trading': {  #
            'handlers': ['trading', 'console', ],
            'level': 'INFO',
        },
        # 'django.db.backends':{
        #     'handlers': ['console' ],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # }
    },
}
