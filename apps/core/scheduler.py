# -- coding: utf-8 --
# @Time : 2022-10-12 21:54:01
# @Author : zhuo.wang
# @File : sheduler.py
import os
import sys
import settings
from apscheduler.schedulers.background import BackgroundScheduler
import django

sys.path.insert(0,os.path.join(settings.BASE_DIR,'apps',))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f'settings.{os.getenv("ENV","dev")}')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from django_apscheduler.jobstores import DjangoJobStore
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(),'default')
scheduler.start()
