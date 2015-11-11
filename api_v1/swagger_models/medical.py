# -*- coding: UTF-8 -*-
from api_v1.swagger_models.patient import PatientMedicalFields

__author__ = 'Panmax'

from flask.ext.restful_swagger import swagger
from flask.ext.restful import fields

@swagger.model
class MedicalTemplateFields(object):
    resource_fields = {
        'id': fields.String,
        'name': fields.String,
        "rank": fields.Integer,
        'show': fields.Boolean,
        'category': fields.String
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        }
    }

@swagger.model
class MedicalProcessFields(object):
    resource_fields = {
        'id': fields.String,
        'name': fields.String,
        'sort': fields.Integer,
        'icon_url': fields.String
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        }
    }

@swagger.model
class ProcessCardFields(object):
    resource_fields = {
        'id': fields.String,
        'name': fields.String,
        "card_can_loop": fields.Boolean,
        'sort': fields.Integer
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        }
    }

@swagger.model
class CardItemFields(object):
    resource_fields = {
        'id': fields.String,
        'name': fields.String,
        'item_type': fields.String,
        'item_title': fields.String,
        'item_prompt': fields.String,
        'item_choice_label': fields.String,
        'item_before_input': fields.String,
        'item_after_input': fields.String,
        "item_is_must": fields.Boolean,
        'sort': fields.Integer,
        'value': fields.String
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        }
    }

@swagger.model
class ItemFields(object):
    resource_fields = {
        'id': fields.String,
        'name': fields.String,
        'item_type': fields.String,
        'item_title': fields.String,
        'item_prompt': fields.String,
        'item_choice_label': fields.String,
        'item_before_input': fields.String,
        'item_after_input': fields.String,
        "item_is_must": fields.Boolean,
        'sort': fields.Integer,
        "value": fields.String
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        }
    }

@swagger.model
@swagger.nested(items=ItemFields.__name__)
class CardFields(object):
    resource_fields = {
        'id': fields.String,
        'name': fields.String,
        "card_can_loop": fields.Boolean,
        'sort': fields.Integer,
        "items": fields.Nested(ItemFields.resource_fields)
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        }
    }

@swagger.model
@swagger.nested(cards=CardFields.__name__)
class ProcessFields(object):
    resource_fields = {
        'id': fields.String,
        'name': fields.String,
        'sort': fields.Integer,
        'icon_url': fields.String,
        "cards": fields.Nested(CardFields.resource_fields),
        "base_url": fields.String
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        }
    }

@swagger.model
@swagger.nested(processes=ProcessFields.__name__)
class MedicalFields(object):
    resource_fields = {
        'id': fields.String,
        'name': fields.String,
        "processes": fields.Nested(ProcessFields.resource_fields)
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        }
    }

@swagger.model
class MedicalsFields(object):
    resource_fields = {
        'id': fields.String,
        'name': fields.String,
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        }
    }

@swagger.model
class ProcessesFields(object):
    resource_fields = {
        'id': fields.String,
        'name': fields.String,
        'icon_url': fields.String,
        'fill': fields.Boolean
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        },
        'fill': {
            'description': "是否已经填写"
        }
    }

@swagger.model
@swagger.nested(processes=ProcessFields.__name__,
                medical=MedicalTemplateFields.__name__)
class ProcessesFields(object):
    resource_fields = {
        'processes': fields.Nested(ProcessFields.resource_fields),
        'medical': fields.Nested(MedicalTemplateFields.resource_fields),
        "patient_medical": fields.Nested(PatientMedicalFields.resource_fields)
    }

    required = resource_fields.keys()

    swagger_metadata = {
        'name': {
            'description': "名称"
        }
    }