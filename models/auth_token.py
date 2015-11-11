# -*- coding: UTF-8 -*-
__author__ = 'Panmax'
from leancloud import Object

class AuthToken(Object):
    @property
    def access_token(self):
        return self.get("access_token")

    @property
    def expires_time(self):
        return self.get("expires_time")
