# -*- coding: UTF-8 -*-
from leancloud import Object
import time

__author__ = 'Panmax'
class PatientMedicalComment(Object):
    """
    患者病历意见
    """
    @property
    def doctor_id(self):
        return self.get('doctor_id')

    @property
    def is_delete(self):
        return self.get('is_delete')

    @property
    def description(self):
        return self.get('description')

    @property
    def patient_medical(self):
        _patient_medical = self.get("patient_medical")
        _patient_medical.fetch()
        return _patient_medical

    @property
    def created_stamp(self):
        carated_at = self.created_at
        stamp = time.mktime(carated_at.timetuple())
        return stamp
