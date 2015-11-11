# -*- coding: UTF-8 -*-
__author__ = 'Panmax'

from flask.ext.restful_swagger import swagger
from flask.ext.restful import fields

@swagger.model
class PatientMedicalCommentFields(object):
    resource_fields = {
        'id': fields.String,
        'doctor_id': fields.Integer,
        'description': fields.String,
        'created_at': fields.String,
        'created_stamp': fields.Integer
    }

    required = resource_fields.keys()
