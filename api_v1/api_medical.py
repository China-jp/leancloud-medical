# -*- coding: UTF-8 -*-
from api_v1.swagger_models.medical import MedicalFields, MedicalsFields, ProcessesFields, ProcessFields
from api_v1.swagger_models.patient import PatientMedicalFields
from handlers import request_validator
from flask import request, current_app
from flask.ext.restful import fields, marshal_with, abort
from models.medical import MedicalTemplate, MedicalProcess, ProcessCard, CardItem, DoctorMedicalRelation
from models.patient import PatientMedical, PatientMedicalProcess

__author__ = 'Panmax'
from . import api, Resource
from leancloud import Query
from leancloud import LeanCloudError
import json

class MedicalsApi(Resource):

    @marshal_with(MedicalsFields.resource_fields)
    def get(self):
        keyword = request.args.get('keyword')
        medicals = Query(MedicalTemplate).equal_to("is_delete", False).equal_to("show", True)
        if keyword:
            medicals = medicals.contains("name", keyword)
        return medicals.find()

class MedicalApi(Resource):
    @marshal_with(MedicalFields.resource_fields)
    def get(self, medical_id):
        medical = Query(MedicalTemplate).get(medical_id)
        processes = Query(MedicalProcess).equal_to("parent", medical).equal_to("is_delete", False).\
            ascending("sort").find()
        for process in processes:
            cards = Query(ProcessCard).equal_to("parent", process).equal_to("is_delete", False).\
                ascending("sort").find()
            for card in cards:
                items = Query(CardItem).equal_to("parent", card).equal_to("is_delete", False).\
                    ascending("sort").find()
                card.items = items
            process.cards = cards
        medical.processes = processes
        return medical

class ProcessesApi(Resource):
    @marshal_with(ProcessesFields.resource_fields)
    def get(self, medical_id):
        medical = Query(MedicalTemplate).get(medical_id)
        processes = Query(MedicalProcess).equal_to("parent", medical).equal_to("is_delete", False).\
            ascending("sort").find()
        return processes
    
class CardsApi(Resource):
    @marshal_with(ProcessFields.resource_fields)
    def get(self, process_id):
        """
        获取过程
        如果给了用户病历id，则获取填写过的那个最新的过程
        :param process_id:
        :return:
        """
        patient_medical_id = request.args.get("patient_medical_id")
        if not patient_medical_id:
            process = Query(MedicalProcess).get(process_id)
            return process
        else:
            patient_medical = Query(PatientMedical).get(patient_medical_id)
            processes = json.loads(patient_medical.get("processes_json"))
            for process in processes:
                if process.get("process_id") == process_id:
                    head = process.get("head")
                    if not head:
                        process = Query(MedicalProcess).get(process_id)
                        return process
                    else:
                        process = json.loads(Query(PatientMedicalProcess).get(head).get("result_json"))
                        return process
            else:
                abort(404)


    @request_validator({"+patient_medical_id": "string",
                        "+result_json": "string",
                        "+creater_id": "string"})
    @marshal_with(ProcessFields.resource_fields)
    def post(self, process_id):
        patient_medical_id = request.jsondata.get("patient_medical_id")
        result_json = request.jsondata.get("result_json")
        creater_id = request.jsondata.get("creater_id")
        patient_medical = Query(PatientMedical).get(patient_medical_id)
        processes = json.loads(patient_medical.get("processes_json"))
        for index, process in enumerate(processes):
            if process.get("process_id") == process_id:
                medical_process = Query(MedicalProcess).get(process_id)
                patient_medical_process = PatientMedicalProcess()
                patient_medical_process.set("patient_medical", patient_medical)
                patient_medical_process.set("result_json", result_json)
                patient_medical_process.set("process", medical_process)
                patient_medical_process.set("creater_id", creater_id)
                patient_medical_process.save()

                process["head"] = patient_medical_process.id
                patient_medical.set("processes_json", json.dumps(processes))
                patient_medical.save()

                # 如果是第0个，说明是填写的第一个过程，要去除第一张卡片的第一项作为患者需求
                if index == 0:
                    patient_requirement = json.loads(result_json).get("cards")[0].get("items")[0].get("value")
                    patient_medical.set("patient_requirement", patient_requirement)
                    patient_medical.save()

                return {}
        else:
            abort(404, message="不匹配")

class PatientMedicalRecordsApi(Resource):
    @marshal_with(PatientMedicalFields.resource_fields)
    def get(self, doctor_id):
        """
        获取某医生接受的病历列表，用在我有患者-患者病历记录
        :param doctor_id:
        :return:
        """
        patient_medicals = []
        try:
            doctor_medicals = Query(DoctorMedicalRelation).equal_to("doctor_id", doctor_id).equal_to("is_cancel", False).find()
        except LeanCloudError, e:
            if e.code == 101:
                pass
        else:
            for doctor_medical in doctor_medicals:
                patient_medical = doctor_medical.get("patient_medical")
                patient_medical.fetch()
                patient_medicals.append(patient_medical)

        current_app.logger.debug(patient_medicals)

        return patient_medicals


class PatientMedicalProcessesResultApi(Resource):
    @marshal_with({
        "patient_medical": fields.Nested(PatientMedicalFields.resource_fields),
        "processes": fields.List(fields.Nested(ProcessFields.resource_fields))
    })
    def get(self, patient_medical_id):
        """
        获取患者填写过的过程
        获取填写过的最新的过程
        :param process_id:
        :return:
        """
        patient_medical = Query(PatientMedical).get(patient_medical_id)
        processes = json.loads(patient_medical.get("processes_json"))
        _processes = []
        for process in processes:
            head = process.get("head")
            if not head:
                process = Query(MedicalProcess).get(process.get("process_id"))
                _processes.append(process)
            else:
                process = json.loads(Query(PatientMedicalProcess).get(head).get("result_json"))
                _processes.append(process)
        return {"patient_medical": patient_medical, "processes": _processes}


api.add_resource(MedicalsApi, '/medicals')
api.add_resource(MedicalApi, '/medicals/<string:medical_id>')
api.add_resource(ProcessesApi, '/medicals/<string:medical_id>/processes')
api.add_resource(CardsApi, "/medicals/process/<process_id>/cards")
api.add_resource(PatientMedicalRecordsApi, '/doctors/<int:doctor_id>/patient_medicals')
api.add_resource(PatientMedicalProcessesResultApi, "/medicals/patient_medicals/<patient_medical_id>/result")
