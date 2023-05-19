# -- coding: utf-8 --
# @Time : 2022/3/20 23:57
# @Author : zhuo.wang
# @File : utils.py

# Register your models here.
def admin_method_attributes(**outer_kwargs):
    """ Wrap an admin method with passed arguments as attributes and values.
    DRY way of extremely common admin manipulation such as setting short_description, allow_tags, etc.
    """
    def method_decorator(func):
        for kw, arg in outer_kwargs.items():
            setattr(func, kw, arg)
        return func
    return method_decorator
