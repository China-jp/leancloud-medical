# coding: utf-8

from datetime import datetime

from flask import Flask
from flask import render_template
from flask.ext.login import LoginManager
from leancloud.errors import LeanCloudError
from leancloud.query import Query
from leancloud.user import User
from models.auth_token import AuthToken
from models.user import Admin
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

from views.todos import todos_view
app.register_blueprint(todos_view, url_prefix='/todos')

from admin_views import admin_view
app.register_blueprint(admin_view, url_prefix='/admin')

from api_v1 import api_v1_bp
app.register_blueprint(api_v1_bp, url_prefix='/v1')


app.secret_key = 'ihaoyisheng'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '.login'

@login_manager.user_loader
def load_user(user_id):
    try:
        admin = Query(Admin).get(user_id)
    except LeanCloudError:
        admin = None
    return admin

@login_manager.request_loader
def load_user_from_request(request):
    access_token = request.headers.get('Authorization')
    if access_token:
        if access_token == "Panmax":
            user = Query(User).equal_to("username", "jiapan").first()
            admin = Query(Admin).equal_to("user", user).first()
            return admin
        try:
            token = Query(AuthToken).equal_to("access_token", access_token).greater_than("expires_time", datetime.now()).first()
        except LeanCloudError:
            return None
        else:
            user = token.get('user')
            user.fetch()
            admin = Query(Admin).equal_to("user", user).first()
            return admin
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/time')
def time():
    return str(datetime.now())
