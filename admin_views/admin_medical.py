# coding: utf-8
from flask import render_template
from flask.ext.login import login_required
from admin_views import admin_view

name_space = 'medical'

@admin_view.route('/%s' % name_space, methods=['GET'])
@login_required
def medical_doctor_edit():
    return render_template('%s/doctor_edit.html' % name_space)
