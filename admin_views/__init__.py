# coding: utf-8

from flask import Blueprint

admin_view = Blueprint('admin', __name__)

from . import admin_medical, auth
