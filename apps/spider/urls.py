# -- coding: utf-8 --
# @Time : 2023/5/16 16:25
# @Author : zhuo.wang
# @File : urls.py
from django.urls import path
from .views import Search

urlpatterns = [
    path('/search/', Search.as_view()),
]