# -*- coding: utf-8 -*-
from flask.ext.login import UserMixin
from leancloud.object_ import Object

__author__ = 'Panmax'

class Admin(Object, UserMixin):
    """
    用户
    """
