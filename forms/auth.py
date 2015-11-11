# -*- coding: utf-8 -*-
from leancloud.errors import LeanCloudError
from leancloud.query import Query
from leancloud.user import User
from models.user import Admin

__author__ = 'Panmax'
from datetime import datetime

from flask_wtf import Form, RecaptchaField
from wtforms import (StringField, PasswordField, BooleanField, HiddenField,
                     SubmitField)
from wtforms.validators import (DataRequired, InputRequired, Email, EqualTo,
                                regexp, ValidationError)

USERNAME_RE = r'^[\w.+-]+$'
is_username = regexp(USERNAME_RE,
                     message="You can only use letters, numbers or dashes.")

class LoginForm(Form):
    login = StringField("Username or E-Mail Address", validators=[
        DataRequired(message="A Username or E-Mail Address is required.")]
    )

    password = PasswordField("Password", validators=[
        DataRequired(message="A Password is required.")])

    remember_me = BooleanField("Remember Me", default=False)

    submit = SubmitField("Login")


class RegisterForm(Form):
    username = StringField("Username", validators=[
        DataRequired(message="A Username is required."),
        is_username])

    password = PasswordField('Password', validators=[
        InputRequired(),
        EqualTo('confirm_password', message='Passwords must match.')])

    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField("Register")

    def validate_username(self, field):
        try:
            user = Query(User).equal_to("username", field.data).first()
        except LeanCloudError, e:
            if e.code == 101:
                pass
            else:
                raise ValidationError(e.message)
        else:
            print 'This Username is already taken.'
            raise ValidationError("This Username is already taken.")

    def save(self):
        user = User()
        user.set("username", self.username.data)
        user.set("password", self.password.data)
        user.sign_up()
        admin = Admin()
        admin.set('user', user)
        admin.save()
        return user
