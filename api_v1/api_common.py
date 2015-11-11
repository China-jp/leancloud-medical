# -*- coding: UTF-8 -*-
from flask.ext.restful import abort
from handlers import request_validator
from flask import request
from leancloud import Query
from models.patient import PatientMedical
import json

__author__ = 'Panmax'

from . import Resource, api
import requests

class ValidateTokenAPi(Resource):
    @request_validator({
        "+process_id": "string",
        "+patient_medical_id": "string",
        "doctor_id": "integer",
        "patient_id": "integer"
    })
    def post(self):
        """
        验证打开病历填写页面的人的身份
        :return:
        """
        process_id = request.jsondata.get("process_id")
        patient_medical_id = request.jsondata.get("patient_medical_id")
        doctor_id = request.jsondata.get("doctor_id")
        patient_id = request.jsondata.get("patient_id")

        patient_medical = Query(PatientMedical).get(patient_medical_id)

        if doctor_id != -1:
            if patient_medical.get("receive_doctor_id") != doctor_id:
                abort(403, message=u"token和主治医生不是同一人")
        if patient_id != -1:
            if patient_medical.get("patient_id") != patient_id:
                abort(403, message=u"open_id和患者不是同一人")
        processes = json.loads(patient_medical.get("processes_json"))

        for process in processes:
            if process.get("process_id") == process_id:
                return {}
        else:
            abort(400, message=u"过程和病历不匹配")

api.add_resource(ValidateTokenAPi, "/validate")
