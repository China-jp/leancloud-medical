# -*- coding: UTF-8 -*-
from leancloud import Object
from leancloud.query import Query

__author__ = 'Panmax'

class LeanCloudObject(Object):
    def __getattr__(self, attr):
        return self.get(attr)

class MedicalTemplate(Object):
    """
    病历模板库
    """
    @property
    def name(self):
        return self.get('name')

    @property
    def is_delete(self):
        return self.get('is_delete')

    @property
    def rank(self):
        return self.get('rank')

    @property
    def show(self):
        return self.get('show')

    # 分裂
    @property
    def category(self):
        return self.get("category")

class MedicalProcess(Object):
    """
    病历过程
    """
    @property
    def name(self):
        return self.get('name')

    @property
    def is_delete(self):
        return self.get('is_delete')

    @property
    def sort(self):
        return self.get('sort')

    @property
    def icon_url(self):
        return self.get('icon_url')

    @property
    def cards(self):
        cards = Query(ProcessCard).equal_to("parent", self).ascending("sort").equal_to("is_delete", False).find()
        return cards

    @property
    def first_create(self):
        return self.get("first_create")

    @property
    def base_url(self):
        return self.get("base_url")

    @property
    def fill(self):
        return self.get("fill")

class ProcessCard(Object):
    """
    过程中的卡片
    """
    @property
    def name(self):
        return self.get('name')

    @property
    def card_can_loop(self):
        return self.get("card_can_loop")

    @property
    def sort(self):
        return self.get('sort')

    @property
    def items(self):
        items = Query(CardItem).equal_to("parent", self).ascending("sort").equal_to("is_delete", False).find()
        return items

class CardItem(Object):
    """
    项目
    """
    @property
    def name(self):
        return self.get('name')

    @property
    def item_type(self):
        return self.get('item_type')

    @property
    def item_title(self):
        return self.get('item_title')

    @property
    def item_prompt(self):
        return self.get('item_prompt')

    @property
    def item_choice_label(self):
        return self.get('item_choice_label')

    @property
    def item_before_input(self):
        return self.get('item_before_input')

    @property
    def item_after_input(self):
        return self.get('item_after_input')

    @property
    def item_is_must(self):
        return self.get('item_is_must')

    @property
    def sort(self):
        return self.get('sort')

    @property
    def value(self):
        return ""


class PatientMedicalRecommend(Object):
    """
    医生被推荐的患者病历记录
    """
    @property
    def doctor_id(self):
        return self.get("doctor_id")

    @property
    def patient_medical(self):
        return self.get("patient_medical")


class DoctorMedicalRelation(Object):
    """
    医生接收患者记录
    """
    @property
    def doctor_id(self):
        return self.get("doctor_id")

    @property
    def patient_medical(self):
        return self.get("patient_medical")

    @property
    def is_cancel(self):
        return self.get("is_cancel")

