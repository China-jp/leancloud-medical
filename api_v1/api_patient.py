# -*- coding: UTF-8 -*-
from leancloud.errors import LeanCloudError
from leancloud.query import Query
from api_v1.swagger_models.comment import PatientMedicalCommentFields
from api_v1.swagger_models.medical import ProcessesFields, ProcessFields
from api_v1.swagger_models.patient import PatientInfoFields, PatientMedicalFields, PatientMedicalLabelFields, \
    PatientMedicalDetailsFields
from handlers import request_validator
from models.comment import PatientMedicalComment
from models.medical import MedicalTemplate, MedicalProcess, DoctorMedicalRelation
from models.patient import PatientInfo, PatientMedical, PatientMedicalProcess, PatientMedicalLabel
from flask import request, current_app as app
import datetime
from flask.ext.restful import fields, marshal_with, abort
import json

__author__ = 'Panmax'
from . import api, Resource

class PatientInfoApi(Resource):
    @marshal_with(PatientInfoFields.resource_fields)
    def get(self, patient_id):
        """
        查询患者个人信息
        :param patient_id:
        :return:
        """
        try:
            patient_info = Query(PatientInfo).equal_to("patient_id", patient_id).first()
        except LeanCloudError, e:
            if e.code == 101:
                abort(404, message=u"该患者还没填写基本信息")
        return patient_info

    @request_validator({"+name": "string",
                        "+sex": "string",
                        "+birth": "string",
                        "+height": "number",
                        "+weight": "number"})
    @marshal_with(PatientInfoFields.resource_fields)
    def post(self, patient_id):
        """
        提交患者个人信息
        :param patient_id:
        :return:
        """
        data = request.jsondata
        name = data.get("name")
        sex = data.get("sex")
        birth = datetime.datetime.strptime(data.get("birth"), "%Y-%m-%d")
        height = data.get("height")
        weight = data.get("weight")
        try:
            patient_info = Query(PatientInfo).equal_to("patient_id", patient_id).first()
        except LeanCloudError, e:
            if e.code == 101:
                patient_info = PatientInfo()
                patient_info.set("patient_id", patient_id)
                patient_info.save()
            else:
                raise e
        patient_info.set("name", name)
        patient_info.set("sex", sex)
        patient_info.set("birth", birth)
        patient_info.set("height", height)
        patient_info.set("weight", weight)
        patient_info.save()
        return patient_info

class PatientMedicalsApi(Resource):
    @marshal_with(PatientMedicalFields.resource_fields)
    def get(self, patient_id):
        """
        查询某患者填写过的病历
        :param patient_id:
        :return:
        """
        try:
            patient_medicals = Query(PatientMedical).equal_to("patient_id", patient_id).find()
        except LeanCloudError, e:
            if e.code == 101:
                patient_medicals = []
            else:
                raise e
        for patient_medical in patient_medicals:
            patient_medical.get("medical").fetch()
        return patient_medicals

    @request_validator({"+medical_id": "string",
                        "+creater_id": "string",
                        "+region_id": "integer",
                        "+medical_name": "string"})
    @marshal_with(PatientMedicalFields.resource_fields)
    def post(self, patient_id):
        """
        创建患者病历
        :param patient_id:
        :return:
        """
        data = request.jsondata
        medical_id = data.get("medical_id")
        creater_id = data.get("creater_id")  # 创建人id，医生前边串上doctor-  患者串patient-
        medical_name = data.get("medical_name").strip()
        region_id = data.get("region_id")
        try:
            medical = Query(MedicalTemplate).equal_to("name", medical_name).first()
        except LeanCloudError, e:
            if e.code == 101:
                medical = Query(MedicalTemplate).get("560277c960b2de2d0c6662e8")
        medical_rank = medical.get("rank")
        medical_category = medical.get("category")

        app.logger.debug(u"为患者：%s，创建病历：%s，创建者：%s" % (patient_id, medical.get("name"), creater_id))

        if not (creater_id.startswith("doctor-") or creater_id.startswith("patient-")):
            abort(400, message=u"创建者id不正确")

        # 检查医生创建未完成病历数量有没有超过三个
        if creater_id.startswith("doctor-") and creater_id != "doctor-100000":
            try:
                patient_medicals = Query(PatientMedical).equal_to("creater_id", creater_id).find()
                not_finish_count = 0
                for patient_medical in patient_medicals:
                    if not patient_medical.finish:
                        not_finish_count += 1
                if not_finish_count >= 3:
                    abort(401, message=u"创建失败，未完成病历不能超过3个。")
            except LeanCloudError, e:
                if e.code == 101:
                    pass
                else:
                    raise e
        try:
            patient_medical = Query(PatientMedical).equal_to("medical", medical).equal_to("patient_id", patient_id).first()
            if patient_medical:
                if creater_id.startswith("doctor-"):
                    if not (patient_medical.get("creater_id") == creater_id or creater_id == "doctor-100000"):
                        abort(401, message=u"该患者病历已被其他医生创建")
                elif creater_id.startswith("patient-"):
                    if patient_medical.get("patient_id") != patient_id:
                        abort(401, message=u"患者只能给自己创建病历")
                patient_medical.set("first_create", False)
                return patient_medical
        except LeanCloudError, e:
            if e.code == 101:
                pass
            else:
                raise e
        patient_medical = PatientMedical()
        patient_medical.set("creater_id", creater_id)
        # 如果是医生创建，接收者就是医生id，如果是值班医生或者患者创建，那么没有接收者
        if creater_id.startswith("doctor-"):
            patient_medical.set("receive_doctor_id", int(creater_id[7:]))
        else:
            patient_medical.set("receive_doctor_id", -1)
        patient_medical.set("patient_id", patient_id)
        patient_medical.set("medical", medical)
        patient_medical.set("region_id", region_id)
        patient_medical.set("category", medical_category if medical_category else u"未分类")
        patient_medical.set("rank", medical_rank)
        patient_medical.set("medical_name", medical_name)
        patient_medical.set("finish", False)
        processes_list = []
        processes = Query(MedicalProcess).equal_to("parent", medical).equal_to("is_delete", False).ascending("sort").find()
        for process in processes:
            p_dic = {
                "process_id": process.id,
                "head": ""
            }
            processes_list.append(p_dic)
        patient_medical.set("processes_json", json.dumps(processes_list))
        patient_medical.save()

        if creater_id.startswith("doctor-") and creater_id != "doctor-100000":
            doctor_id = int(creater_id[7:])
            doctor_medical = DoctorMedicalRelation()
            doctor_medical.set("doctor_id", doctor_id)
            doctor_medical.set("patient_medical", patient_medical)
            doctor_medical.set("is_cancel", False)
            doctor_medical.save()

        patient_medical.set("first_create", True)
        app.logger.debug(u"创建成功，患者病历id为%s" % patient_medical.id)
        return patient_medical

class PatientMedicalApi(Resource):
    @marshal_with(PatientMedicalDetailsFields.resource_fields)
    def get(self, patient_medical_id):
        """
        根据创建的患者的病历id获取病历
        :param patient_medical_id:
        :return:
        """
        patient_medical = Query(PatientMedical).get(patient_medical_id)
        patient_medical.get("medical").fetch()
        comments = Query(PatientMedicalComment).equal_to("patient_medical", patient_medical).ascending("created_at").limit(2).find()
        return {"patient_medical": patient_medical, "comments": comments}

    # @marshal_with(PatientMedicalFields.resource_fields)
    # def delete(self, patient_medical_id):
    #     """
    #     推荐患者病历，将患者病历放入我要患者的池子，同时解除医患关系
    #     :param patient_medical_id:
    #     :return:
    #     """
    #     patient_medical = Query(PatientMedical).get(patient_medical_id)
    #     patient_medical.set("receive_doctor_id", -1)
    #     patient_medical.save()
    #     return patient_medical
    #
    # @request_validator({"+doctor_id": "integer"})
    # @marshal_with(PatientMedicalFields.resource_fields)
    # def put(self, patient_medical_id):
    #     """
    #     取消接收
    #     :param patient_medical_id:
    #     :return:
    #     """
    #     doctor_id = request.jsondata.get("doctor_id")
    #     patient_medical = Query(PatientMedical).get(patient_medical_id)
    #     doctor_medical = Query(DoctorMedicalRelation).equal_to("doctor_id", doctor_id).equal_to("patient_medical",
    #                                                                                             patient_medical).first()
    #     doctor_medical.set("is_cancel", True)
    #     doctor_medical.save()
    #     return patient_medical


class PatientMedicalCancelApi(Resource):
    @marshal_with(PatientMedicalFields.resource_fields)
    def delete(self, doctor_id, patient_medical_id):
        """
        取消接收
        :param patient_medical_id:
        :return:
        """
        patient_medical = Query(PatientMedical).get(patient_medical_id)
        doctor_medical = Query(DoctorMedicalRelation).equal_to("doctor_id", doctor_id).equal_to("patient_medical",
                                                                                                patient_medical).first()
        doctor_medical.set("is_cancel", True)
        doctor_medical.save()
        return patient_medical

class PatientMedicalProcessesApi(Resource):
    ProcessFields.resource_fields['fill'] = fields.Boolean

    @request_validator({"+result_json": "string",
                        "+creater_id": "string",
                        "+process_id": "string"})
    @marshal_with(ProcessesFields.resource_fields)
    def post(self, patient_medical_id):
        """
        创建病历过程
        :param patient_id: 病历id
        :return:
        """
        data = request.jsondata
        result_json = data.get("result_json")
        creater_id = data.get("creater_id")
        process_id = data.get("process_id")
        if not (creater_id.startswith("doctor-") or creater_id.startswith("patient-")):
            abort(400, message=u"创建者id不正确")
        patient_medical = Query(PatientMedical).get(patient_medical_id)

        process = Query(MedicalProcess).get(process_id)
        patient_process = PatientMedicalProcess()
        patient_process.set("process", process)
        patient_process.set("result_json", result_json)
        patient_process.set("patient_id", patient_medical.patient_id)
        patient_process.set("creater_id", creater_id)
        patient_process.save()

        # update medical record head
        processes_list = json.loads(patient_medical.get("processes_json"))
        for _process in processes_list:
            if _process['process_id'] == process_id:
                _process['head'] = patient_process.id
                break
        else:
            abort(400, message=u'更新过程head失败')

        patient_medical.set("processes_json", json.dumps(processes_list))

        if processes_list[0].get("head") and processes_list[1].get("head"):
            patient_medical.set("finish", True)
            patient_medical.save()
        else:
            patient_medical.set("finish", False)
            patient_medical.save()

        patient_medical.save()

        return patient_process

    @marshal_with(ProcessesFields.resource_fields)
    def get(self, patient_medical_id):
        """
        通过创建好的病历id，获取创建时候的过程，同时带着病历模板信息
        :param patient_medical_id: 病历id
        :return:
        """
        app.logger.debug(u"获取病历过程，患者病历id：%s" % patient_medical_id)

        patient_medical = Query(PatientMedical).get(patient_medical_id)
        processes_list = json.loads(patient_medical.get("processes_json"))
        processes = []
        for _process in processes_list:
            try:
                process = Query(MedicalProcess).get(_process['process_id'])
            except LeanCloudError, e:
                if e.code == 101:
                    continue
            process.set("fill", True if _process['head'] else False)
            process.set("base_url", "http://m.ihaoyisheng.com/medical/processes/%s?patient_medical_id=%s" % (process.id, patient_medical_id))
            processes.append(process)
        medical = patient_medical.get("medical")
        medical.fetch()

        return {
            "processes": processes,
            "medical": medical,
            "patient_medical": patient_medical
        }

class PatientsMedicalsAPi(Resource):
    @request_validator({"+patient_ids": ["integer"]})
    @marshal_with(PatientMedicalFields.resource_fields)
    def post(self):
        """
        好像没有用到。。。
        获取数组中患者id的所有创建过的病历
        为啥要用post？因为get不能传body啊！
        :return:
        """
        patient_ids = request.jsondata.get("patient_ids")
        patient_medicals = []
        for patient_id in patient_ids:
            try:
                _patient_medicals = Query(PatientMedical).equal_to("patient_id", patient_id).find()
            except LeanCloudError, e:
                if e.code == 101:
                    pass
                else:
                    raise e
            else:
                patient_medicals += _patient_medicals
        return patient_medicals

    @marshal_with(PatientMedicalFields.resource_fields)
    def get(self):
        severe = int(request.args.get("severe", 0))  # 如果是1，则取出由患者创建，并且没有医生接收的病历
        query = Query(PatientMedical)
        if severe == 1:
            query.startswith("creater_id", "patient").equal_to("receive_doctor_id", -1)

        patient_medicals = query.find()
        if not patient_medicals:
            patient_medicals = []
        return patient_medicals

class PatientMedicalLabelApi(Resource):
    @request_validator({"symptom": "string",
                        "follow_symptom": "string",
                        "disease_time": "string",
                        "stage": "string",
                        "pathology": "string",
                        "check_item": "string",
                        "medical_history": "string",
                        "operation": "string",
                        "treatment": "string",
                        "complication": "string"})
    @marshal_with(PatientMedicalLabelFields.resource_fields)
    def post(self, patient_medical_id):
        """
        提交病历标签
        :param patient_medical_id:
        :return:
        """
        data = request.jsondata
        symptom = data.get("symptom")  # 症状
        follow_symptom = data.get("follow_symptom")  # 伴随症状
        disease_time = data.get("disease_time")  # 发病时间
        stage = data.get("stage")  # 分期
        pathology = data.get("pathology")  # 病理分型
        check_item = data.get("check_item")  # 检查项目
        medical_history = data.get("medical_history")  # 相关病史
        operation = data.get("operation")  # 手术
        treatment = data.get("treatment")  # 治疗
        complication = data.get("complication")  # 合并症
        patient_medical = Query(PatientMedical).get(patient_medical_id)
        try:
            label = Query(PatientMedicalLabel).equal_to("patient_medical", patient_medical).first()
        except LeanCloudError, e:
            if e.code == 101:
                label = PatientMedicalLabel()
                label.set("patient_medical", patient_medical)
            else:
                raise e
        label.set("symptom", symptom)
        label.set("follow_symptom", follow_symptom)
        label.set("disease_time", disease_time)
        label.set("stage", stage)
        label.set("pathology", pathology)
        label.set("check_item", check_item)
        label.set("medical_history", medical_history)
        label.set("operation", operation)
        label.set("treatment", treatment)
        label.set("complication", complication)
        label.save()
        return label

    @marshal_with(PatientMedicalLabelFields.resource_fields)
    def get(self, patient_medical_id):
        patient_medical = Query(PatientMedical).get(patient_medical_id)
        try:
            label = Query(PatientMedicalLabel).equal_to("patient_medical", patient_medical).first()
        except LeanCloudError, e:
            if e.code == 101:
                abort(404, message=u"该病历还没填写过标签")
            else:
                raise e
        else:
            return label

class PatientLabelApi(Resource):
    @marshal_with(PatientMedicalLabelFields.resource_fields)
    def get(self, patient_id):
        """
        获取患者最危重的病历并且填过病历标签的标签
        :return:
        """
        medical_label = None
        try:
            patient_medicals = Query(PatientMedical).equal_to("patient_id", patient_id).find()
            if not patient_medicals:
                return {}
            for patient_medical in patient_medicals:
                patient_medical.medical.fetch()
            # 填写过的病历重新排序，严重的在前边
            patient_medicals.sort(key=lambda rank: patient_medical.medical.rank, reverse=True)
            for patient_medical in patient_medicals:
                try:
                    medical_label = Query(PatientMedicalLabel).equal_to("patient_medical", patient_medical).first()
                except LeanCloudError, e:
                    if e.code == 101:
                        pass
                if medical_label:
                    break
        except LeanCloudError, e:
            if e.code == 101:
                return {}

        if not medical_label:
            return {}
        return medical_label


class PatientsNeedApi(Resource):
    @marshal_with(PatientMedicalFields.resource_fields)
    def get(self):
        """
        我要患者首页
        :return:
        """
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 20))
        region_id = int(request.args.get("region_id", -1))
        keyword = request.args.get("keyword")
        rank = int(request.args.get("rank", 0))
        category = request.args.get("category")
        skip = (page-1) * size

        patient_medicals = []
        try:
            query = Query(PatientMedical).equal_to("finish", True)
            if region_id and region_id != -1:
                query = query.equal_to("region_id", region_id)
            elif keyword:
                query = query.contains("medical_name", keyword)
            elif category:
                query = query.equal_to("category", category)
                if rank != 0:
                    query = query.equal_to("rank", rank)
            patient_medicals = query.skip(skip).limit(size).find()
        except LeanCloudError, e:
            if e.code == 101:
                patient_medicals = []
        return patient_medicals


class PatientMedicalCommentApi(Resource):
    @request_validator({"+doctor_id": "integer",
                        "+description": "string"})
    @marshal_with(PatientMedicalCommentFields.resource_fields)
    def post(self, patient_medical_id):
        """
        给某个病历发表意见
        :param patient_medical_id:
        :return:
        """
        data = request.jsondata
        patient_medical = Query(PatientMedical).get(patient_medical_id)
        doctor_id = data.get("doctor_id")
        description = data.get("description")
        comment = PatientMedicalComment()
        comment.set("doctor_id", doctor_id)
        comment.set("description", description)
        comment.set("patient_medical", patient_medical)
        comment.save()
        return comment

    @marshal_with(PatientMedicalCommentFields.resource_fields)
    def get(self, patient_medical_id):
        """
        获取某个患者病历的意见列表
        :param patient_medical_id:
        :return:
        """
        patient_medical = Query(PatientMedical).get(patient_medical_id)
        try:
            patient_medical_comments = Query(PatientMedicalComment).equal_to("patient_medical", patient_medical).ascending("created_at").find()
        except LeanCloudError, e:
            if e.code == 101:
                patient_medical_comments = []
        return patient_medical_comments


class PatientsFirstMedicalApi(Resource):
    @request_validator({"+patient_ids": ["integer"]})
    @marshal_with(PatientMedicalFields.resource_fields)
    def post(self):
        """
        获取传进来的用户id列表的最近一次的病历，用在我有患者首页
        :return:
        """
        patient_ids = request.jsondata.get("patient_ids")
        patient_medicals = []
        for patient_id in patient_ids:
            try:
                _patient_medicals = Query(PatientMedical).equal_to("patient_id", patient_id).first()
            except LeanCloudError, e:
                if e.code == 101:
                    patient_medicals.append(None)
            else:
                patient_medicals.append(_patient_medicals)
        return patient_medicals


class PatientReceiveApi(Resource):
    @request_validator({"+doctor_id": "integer"})
    @marshal_with(PatientMedicalFields.resource_fields)
    def post(self, patient_medical_id):
        """
        我要患者-接收患者
        :return:
        """
        doctor_id = request.jsondata.get("doctor_id")
        patient_medical = Query(PatientMedical).get(patient_medical_id)
        try:
            doctor_medical = Query(DoctorMedicalRelation).equal_to("doctor_id", doctor_id).equal_to("patient_medical",
                                                                                                    patient_medical).first()
        except LeanCloudError, e:
            if e.code == 101:
                doctor_medical = DoctorMedicalRelation()
                doctor_medical.set("doctor_id", doctor_id)
                doctor_medical.set("patient_medical", patient_medical)
                doctor_medical.set("is_cancel", False)
                doctor_medical.save()
        else:
            if doctor_medical.get("is_cancel"):
                doctor_medical.set("is_cancel", False)
                doctor_medical.save()
            else:
                abort(400, message=u"您已接收该患者")
        return patient_medical

api.add_resource(PatientInfoApi, "/patients/<int:patient_id>")
api.add_resource(PatientMedicalsApi, "/patients/<int:patient_id>/medicals")
api.add_resource(PatientMedicalApi, "/patients/medicals/<patient_medical_id>")
api.add_resource(PatientMedicalCancelApi, "/patients/medicals/<int:doctor_id>/<patient_medical_id>")
api.add_resource(PatientMedicalProcessesApi, "/patients/medicals/<patient_medical_id>/processes")
api.add_resource(PatientsMedicalsAPi, "/patients/medicals")
api.add_resource(PatientMedicalLabelApi, "/patients/medicals/<patient_medical_id>/labels")
api.add_resource(PatientLabelApi, "/patients/<int:patient_id>/labels")
api.add_resource(PatientsNeedApi, "/patients/no_receive/medicals")
api.add_resource(PatientMedicalCommentApi, '/patients/medicals/<patient_medical_id>/comments')
api.add_resource(PatientsFirstMedicalApi, "/patients/medicals/first")
api.add_resource(PatientReceiveApi, "/patients/medicals/<patient_medical_id>/receive")
