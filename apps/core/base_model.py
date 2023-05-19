# -- coding: utf-8 --
# @Time : 2022/3/20 22:43
# @Author : zhuo.wang
# @File : base_model.py
from datetime import datetime

from django.db import models


class BaseModel(models.Model):
    created_time = models.DateTimeField(
        default=datetime.now, blank=True, null=True, verbose_name="创建时间", db_index=True
    )
    update_time = models.DateTimeField(
        auto_now=True, blank=True, null=True, verbose_name="更新时间", db_index=True
    )

    class Meta:
        abstract = True

