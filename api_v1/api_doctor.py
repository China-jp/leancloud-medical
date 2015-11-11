# -*- coding: UTF-8 -*-
from flask.ext.restful import marshal_with
from api_v1.swagger_models.patient import PatientMedicalFields
from handlers import request_validator
from models.medical import PatientMedicalRecommend
from models.patient import PatientMedical

__author__ = 'Panmax'
from . import Resource, api
from flask import request
from leancloud import Query, LeanCloudError


class PatientRecommendApi(Resource):
    @marshal_with(PatientMedicalFields.resource_fields)
    def get(self, doctor_id):
        try:
            patient_medical_recommends = Query(PatientMedicalRecommend).equal_to("doctor_id", doctor_id).find()
        except LeanCloudError, e:
            if e.code == 101:
                patient_medical_recommends = []
        patient_medicals = []
        for patient_medical_recommend in patient_medical_recommends:
            patient_medical = Query(PatientMedical).get(patient_medical_recommend.get("patient_medical").id)
            patient_medicals.append(patient_medical)
        return patient_medicals

    @request_validator({"+patient_medical_id": "string"})
    @marshal_with(PatientMedicalFields.resource_fields)
    def post(self, doctor_id):
        patient_medical_id = request.jsondata.get("patient_medical_id")
        patient_medical = Query(PatientMedical).get(patient_medical_id)
        patient_medical_recommend = None
        try:
            patient_medical_recommend = Query(PatientMedicalRecommend).equal_to("patient_medical",
                                                                               patient_medical).equal_to("doctor_id",
                                                                                                         doctor_id).first()
        except LeanCloudError, e:
            if e.code == 101:
                pass
        if patient_medical_recommend:
            return patient_medical
        patient_medical_recommend = PatientMedicalRecommend()
        patient_medical_recommend.set("patient_medical", patient_medical)
        patient_medical_recommend.set("doctor_id", doctor_id)
        patient_medical_recommend.save()
        return patient_medical

api.add_resource(PatientRecommendApi, "/doctors/<int:doctor_id>/patient_medicals/recommend")
