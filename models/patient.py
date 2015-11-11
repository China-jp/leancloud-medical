# -*- coding: UTF-8 -*-
from leancloud.errors import LeanCloudError
from leancloud.query import Query
import datetime
from models.comment import PatientMedicalComment
import json
from models.medical import MedicalProcess
import datetime
import pytz

__author__ = 'Panmax'
from leancloud import Object
class PatientInfo(Object):
    @property
    def patient_id(self):
        return self.get("patient_id")

    @property
    def name(self):
        return self.get("name")

    @property
    def sex(self):
        return self.get("sex")

    @property
    def birth(self):
        return self.get("birth").strftime("%Y-%m-%d")

    @property
    def weight(self):
        return self.get("weight")

    @property
    def height(self):
        return self.get("height")

    @property
    def age(self):
        birth = self.get("birth")
        return (datetime.datetime.today().utcnow().replace(tzinfo=pytz.utc) - birth).days/365

class PatientMedical(Object):
    @property
    def creater_id(self):
        return self.get("creater_id")

    @property
    def patient_id(self):
        return self.get("patient_id")

    @property
    def medical_id(self):
        return self.get("medical").id

    @property
    def medical_name(self):
        return self.get("medical_name")

    @property
    def medical_rank(self):
        return self.get("rank")

    @property
    def processes_json(self):
        return self.get("processes_json")

    @property
    def medical(self):
        return self.get("medical")

    @property
    def receive_doctor_id(self):
        return self.get("receive_doctor_id")

    @property
    def medical_label(self):
        try:
            medical_label = Query(PatientMedicalLabel).equal_to("patient_medical", self).first()
        except LeanCloudError, e:
            if e.code == 101:
                return {
                            "symptom": u"暂无标签"
                        }
        return medical_label

    @property
    def _created_at(self):
        delta = datetime.timedelta(hours=8)
        created_at = (self.created_at + delta).strftime('%Y-%m-%d %T')
        return created_at

    @property
    def _updated_at(self):
        delta = datetime.timedelta(hours=8)
        if self.updated_at:
            updated_at = (self.updated_at + delta).strftime('%Y-%m-%d %T')
        else:
            updated_at = (self.created_at + delta).strftime('%Y-%m-%d %T')
        return updated_at


    @property
    def region_id(self):
        return self.get("region_id")


    @property
    def comment_count(self):
        try:
            count = Query(PatientMedicalComment).equal_to("patient_medical", self).count()
        except LeanCloudError, e:
            if e.code == 101:
                count = 0
        return count

    @property
    def patient_requirement(self):
        """
        患者需求
        :return:
        """
        return self.get("patient_requirement") if self.get("patient_requirement") else u""

    @property
    def finish(self):
        """
        检查所有过程是否填写
        判断所有过程是否完成，通过所有过程是否有head来判断
        :return:
        """
        processes_list = json.loads(self.get("processes_json"))
        for _process in processes_list:
            if not _process['head']:
                return False
        else:
            return True
        # return self.get("finish")

    @property
    def supplement(self):
        """
        是否有过补充
        如果其中一个过程填写超过一次，返回true
        :return:
        """
        processes_list = json.loads(self.get("processes_json"))
        for _process in processes_list:
            patient_id = self.get("patient_id")
            process_id = _process['process_id']
            process = Query(MedicalProcess).get(process_id)

            count = 0
            try:
                count = Query(PatientMedicalProcess).equal_to("process", process).equal_to("patient_id", patient_id).count()
            except LeanCloudError, e:
                if e.code == 101:
                    count = 0
            if count > 1:
                return True
        return False

    @property
    def first_create(self):
        """
        判断是不是第一次创建
        :return:
        """
        return self.get("first_create")

class PatientMedicalProcess(Object):
    pass

class PatientMedicalLabel(Object):
    @property
    def symptom(self):
        return self.get("symptom")

    @property
    def follow_symptom(self):
        return self.get("follow_symptom")

    @property
    def disease_time(self):
        return self.get("disease_time")

    @property
    def stage(self):
        return self.get("stage")

    @property
    def pathology(self):
        return self.get("pathology")

    @property
    def check_item(self):
        return self.get("check_item")

    @property
    def medical_history(self):
        return self.get("medical_history")

    @property
    def operation(self):
        return self.get("operation")

    @property
    def treatment(self):
        return self.get("treatment")

    @property
    def complication(self):
        return self.get("complication")
