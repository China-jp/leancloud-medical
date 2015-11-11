# -*- coding: UTF-8 -*-
from flask.ext.login import login_required

__author__ = 'Panmax'

import json

from flask import Blueprint, current_app
from flask.ext.restful import Api, abort
from flask.ext.restful_swagger import swagger
from flask.ext.restful import Resource as BaseResource


api_v1_bp = Blueprint('api_v1', __name__)


api = swagger.docs(Api(api_v1_bp), apiVersion='v1',
                   basePath='https://api.ihaoyisheng.com',
                   resourcePath='/',
                   produces=["application/json"],
                   api_spec_url='/api/doc',
                   description='我爱好医生API')


# Api Super Class
class Resource(BaseResource):
    # decorator for all methods of subclass
    method_decorators = [login_required]

    # add method names if skips auth token_key
    auth_token_without = None

@api_v1_bp.errorhandler(Exception)
def error_page(e):
    current_app.logger.exception(e)
    return json.dumps({"message": e.message}), 500

@api_v1_bp.route("/login", methods=["GET", "POST"])
def login():
    abort(403)

import api_admin_medical, api_medical, api_generate_token, api_patient, api_common, api_doctor
