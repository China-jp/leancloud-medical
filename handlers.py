# -*- coding: utf8 -*-

import valideer as V
from decorator import decorator

from flask import request
from flask.ext.restful import abort

from werkzeug.exceptions import BadRequest
from wtforms import ValidationError

def request_validator(schema):
    """
    请求验证装饰器

    :param schema:
    :return:
    """

    @decorator
    def _func(func, *args, **kwargs):
        try:
            injson = request.get_json(force=True)
        except BadRequest, e:
            abort(400, message=u"body中JSON对象错误")
        validator = V.parse(schema)
        try:
            validator.validate(injson)
        except ValidationError, e:
            abort(400, message=e.message)

        outkeys = (k.lstrip('+?') for k in schema)
        outschema = ((k, injson.get(k)) for k in outkeys if k in injson)

        request.jsondata = dict(outschema)
        return func(*args, **kwargs)

    return _func