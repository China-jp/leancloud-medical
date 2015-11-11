# -*- coding: UTF-8 -*-
from flask.helpers import url_for
from leancloud.errors import LeanCloudError
from leancloud.query import Query
from leancloud.user import User

from forms.auth import LoginForm, RegisterForm
from admin_views import admin_view
from flask import redirect, render_template, request
from flask_login import (current_user, login_user, login_required,
                         logout_user, confirm_login, login_fresh)
from models.user import Admin


@admin_view.route("/login", methods=["GET", "POST"])
def login():
    """
    管理员登录
    """
    # if current_user is not None and current_user.is_authenticated:
    #     return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            User().login(form.login.data, form.password.data)
        except LeanCloudError, e:
            if e.code == 210:
                print u'帐号或密码错误'
            elif e.code == 211:
                print u'用户不存在'
            return u'帐号或密码错误'
        else:
            user = Query(User).equal_to("username", form.login.data).first()
            admin = Query(Admin).equal_to("user", user).first()
            login_user(admin)
            next = request.args.get('next')
            return redirect(next or "/admin/medical")

    return render_template('auth/login.html', form=form)

@admin_view.route("/register", methods=["GET", "POST"])
@login_required
def regist_admin():
    """
    Register a new user
    """
    form = RegisterForm()
    if form.validate_on_submit():
        user = form.save()
        return redirect(url_for('index'))
    return render_template("auth/register.html", form=form)


@admin_view.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))
