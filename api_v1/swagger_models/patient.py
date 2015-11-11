# -*- coding: UTF-8 -*-
from flask.ext.restful_swagger import swagger
from flask.ext.restful import fields
from api_v1.swagger_models.comment import PatientMedicalCommentFields

__author__ = 'Panmax'

@swagger.model
class PatientInfoFields(object):
    resource_fields = {
        "patient_id": fields.Integer,
        'name': fields.String,
        "sex": fields.String,
        "birth": fields.String,
        "height": fields.Float,
        "weight": fields.Float,
        "age": fields.Integer
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "姓名"
        }
    }

@swagger.model
class PatientMedicalLabelFields(object):
    """
    病历标签
    """
    resource_fields = {
        "symptom": fields.String,
        "follow_symptom": fields.String,
        "disease_time": fields.String,
        "stage": fields.String,
        "pathology": fields.String,
        "check_item": fields.String,
        "medical_history": fields.String,
        "operation": fields.String,
        "treatment": fields.String,
        "complication": fields.String
    }

    required = resource_fields.keys()

@swagger.model
@swagger.nested(medical_label=PatientMedicalLabelFields.__name__,
                medical_info=PatientInfoFields.__name__)
class PatientMedicalFields(object):
    resource_fields = {
        "id": fields.String,
        'creater_id': fields.String,
        "patient_id": fields.Integer,
        "medical_id": fields.String,
        "medical_name": fields.String,
        "medical_rank": fields.Integer,
        "region_id": fields.Integer,
        "receive_doctor_id": fields.Integer,
        "medical_label": fields.Nested(PatientMedicalLabelFields.resource_fields),
        "created_at": fields.String(attribute="_created_at"),
        "updated_at": fields.String(attribute="_updated_at"),
        "patient_requirement": fields.String,    # 患者需求

        "first_create": fields.Boolean,     # 是否第一次填写，用在创建病历时
        "finish": fields.Boolean,            # 所有过程是否完成
        "comment_count": fields.Integer,       # 医生意见数
        "supplement": fields.Boolean         # 是否有过补充
    }

    required = resource_fields.keys()

class PatientMedicalDetailsFields(object):
    resource_fields = {
        'patient_medical': fields.Nested(PatientMedicalFields.resource_fields),
        'comments': fields.Nested(PatientMedicalCommentFields.resource_fields),
    }

    required = resource_fields.keys()