# -*- coding: UTF-8 -*-
from flask.ext.restful import abort
from leancloud.errors import LeanCloudError
from leancloud.query import Query
from leancloud.user import User
from handlers import request_validator
from models.auth_token import AuthToken
import datetime
import uuid

__author__ = 'Panmax'
from flask import request
from flask.ext.restful import Resource
from . import api

class GenerateTokenApi(Resource):
    auth_token_without = ['post']

    @request_validator({"username": "string",
                        "password": "string"})
    def post(self):
        data = request.jsondata
        username = data.get('username')
        password = data.get('password')
        try:
            User().login(username, password)
        except LeanCloudError:
            abort(403, message=u"认证失败")
        else:
            user = Query(User).equal_to("username", username).first()
            try:
                token = Query(AuthToken).equal_to("user", user).greater_than("expires_time", datetime.datetime.now()).first()
            except LeanCloudError, e:
                if e.code == 101:  # 服务端对应的 Class 还没创建
                    expires_date = datetime.datetime.now() + datetime.timedelta(hours=8)
                    token = AuthToken()
                    token.set("user", user)
                    token.set("expires_time", expires_date)
                    token.set("access_token", str(uuid.uuid1()))
                    token.save()
                    return {
                        "access_token": token.access_token,
                        "expires_time": token.expires_time.isoformat()
                    }
                else:
                    raise e
            else:
                return {
                        "access_token": token.access_token,
                        "expires_time": token.expires_time.isoformat()
                    }

api.add_resource(GenerateTokenApi, "/generate_token")
