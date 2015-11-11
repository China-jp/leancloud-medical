# -*- coding: UTF-8 -*-
from api_v1.swagger_models.medical import MedicalTemplateFields, MedicalProcessFields, ProcessCardFields, CardItemFields, \
    MedicalFields, MedicalsFields
from handlers import request_validator
from flask import request
from flask.ext.restful import fields, marshal_with, abort
from models.medical import MedicalTemplate, MedicalProcess, ProcessCard, CardItem

__author__ = 'Panmax'
from . import api, Resource


from leancloud import Query
from leancloud import LeanCloudError

class AdminMedicalsApi(Resource):
    @marshal_with(MedicalTemplateFields.resource_fields)
    def get(self):
        try:
            medicals = Query(MedicalTemplate).ascending('name').descending('show').equal_to("is_delete", False).find()
        except LeanCloudError, e:
            if e.code == 101:  # 服务端对应的 Class 还没创建
                medicals = []
            else:
                raise e
        return medicals

    @request_validator({"+name": "string",
                        "+rank": "integer",
                        "+category": "string"})
    @marshal_with(MedicalTemplateFields.resource_fields)
    def post(self):
        name = request.jsondata.get('name')
        rank = request.jsondata.get('rank')
        category = request.jsondata.get('category')
        medical = MedicalTemplate()
        medical.set("name", name)
        medical.set("rank", rank)
        medical.set('is_delete', False)
        medical.set('show', False)
        medical.set("category", category)
        medical.save()
        return medical

class AdminMedicalApi(Resource):
    @request_validator({"+name": "string",
                        "+show": "boolean",
                        "+rank": "integer",
                        "+category": "string"})
    @marshal_with(MedicalTemplateFields.resource_fields)
    def put(self, medical_id):
        name = request.jsondata.get('name')
        show = request.jsondata.get('show')
        rank = request.jsondata.get('rank')
        category = request.jsondata.get("category")
        medical = Query(MedicalTemplate).get(medical_id)
        medical.set("name", name)
        medical.set("show", show)
        medical.set("rank", rank)
        medical.set("category", category)
        medical.save()
        return medical

    @marshal_with(MedicalTemplateFields.resource_fields)
    def delete(self, medical_id):
        medical = Query(MedicalTemplate).get(medical_id)
        medical.set("is_delete", True)
        medical.save()
        return medical

    @marshal_with(MedicalTemplateFields.resource_fields)
    @request_validator({"+name": "string",
                        "+rank": "integer"})
    def post(self, medical_id):
        """
        复制病历
        :param medical_id:
        :return:
        """
        name = request.jsondata.get("name")
        rank = request.jsondata.get("rank")
        new_medical = MedicalTemplate()
        new_medical.set("name", name)
        new_medical.set("rank", rank)
        new_medical.set("show", False)
        new_medical.set("is_delete", False)
        new_medical.save()

        medical = Query(MedicalTemplate).get(medical_id)
        medical_processes = Query(MedicalProcess).equal_to("parent", medical).equal_to("is_delete", False).find()
        for medical_process in medical_processes:
            new_medical_process = MedicalProcess()
            new_medical_process.set("parent", new_medical)
            new_medical_process.set("is_delete", False)
            new_medical_process.set("name", medical_process.get("name"))
            new_medical_process.set("sort", medical_process.get("sort"))
            new_medical_process.set("icon_url", medical_process.get("icon_url"))
            new_medical_process.save()
            process_cards = Query(ProcessCard).equal_to("parent", medical_process).equal_to("is_delete", False).find()
            for process_card in process_cards:
                new_process_card = ProcessCard()
                new_process_card.set("parent", new_medical_process)
                new_process_card.set("is_delete", False)
                new_process_card.set("name", process_card.get("name"))
                new_process_card.set("card_can_loop", process_card.get("card_can_loop"))
                new_process_card.set("sort", process_card.get("sort"))
                new_process_card.save()
                card_items = Query(CardItem).equal_to("parent", process_card).equal_to("is_delete", False).find()
                for card_item in card_items:
                    new_card_item = CardItem()
                    new_card_item.set("parent", new_process_card)
                    new_card_item.set("is_delete", False)
                    new_card_item.set("item_before_input", card_item.get("item_before_input"))
                    new_card_item.set("item_after_input", card_item.get("item_after_input"))
                    new_card_item.set("item_choice_label", card_item.get("item_choice_label"))
                    new_card_item.set("item_is_must", card_item.get("item_is_must"))
                    new_card_item.set("item_prompt", card_item.get("item_prompt"))
                    new_card_item.set("item_title", card_item.get("item_title"))
                    new_card_item.set("item_type", card_item.get("item_type"))
                    new_card_item.set("name", card_item.get("name"))
                    new_card_item.set("sort", card_item.get("sort"))
                    new_card_item.save()
        return new_medical


class AdminMedicalProcessesApi(Resource):
    @marshal_with(MedicalProcessFields.resource_fields)
    def get(self, medical_id):
        medical = Query(MedicalTemplate).get(medical_id)
        try:
            processes = Query(MedicalProcess).ascending('sort').equal_to("is_delete", False).equal_to(
                "parent", medical).find()
        except LeanCloudError, e:
            if e.code == 101:  # 服务端对应的 Class 还没创建
                processes = []
            else:
                raise e
        return processes

    @request_validator({"+name": "string",
                        "icon_url": "string"})
    @marshal_with(MedicalProcessFields.resource_fields)
    def post(self, medical_id):
        name = request.jsondata.get('name')
        icon_url = request.jsondata.get('icon_url')
        medical = Query(MedicalTemplate).get(medical_id)
        try:
            total_processes_num = Query(MedicalProcess).equal_to("parent", medical).count()
        except LeanCloudError, e:
            if e.code == 101:  # 服务端对应的 Class 还没创建
                total_processes_num = 0
            else:
                raise e
        process = MedicalProcess()
        process.set("name", name)
        process.set('is_delete', False)
        process.set("parent", medical)
        process.set("sort", total_processes_num)
        process.set("icon_url", icon_url)
        process.save()
        return process

    @request_validator({"sort": "string"})
    @marshal_with(MedicalProcessFields.resource_fields)
    def put(self, medical_id):
        """
        重新排序
        """
        medical = Query(MedicalTemplate).get(medical_id)
        processes = Query(MedicalProcess).ascending('sort').equal_to("is_delete", False).equal_to(
                "parent", medical).find()
        sort = request.jsondata.get('sort')
        sort_list = sort.split(',')
        if len(processes) != len(sort_list):
            return abort(400, message=u"数量不同")

        for i, process_id in enumerate(sort_list):
            process = Query(MedicalProcess).get(process_id)
            process.set("sort", i)
            process.save()
        return processes

class AdminMedicalProcessApi(Resource):
    @request_validator({"+name": "string",
                        "icon_url": "string"})
    @marshal_with(MedicalProcessFields.resource_fields)
    def put(self, process_id):
        name = request.jsondata.get('name')
        icon_url = request.jsondata.get('icon_url')
        process = Query(MedicalProcess).get(process_id)
        process.set("name", name)
        process.set("icon_url", icon_url)
        process.save()
        return process

    @marshal_with(MedicalProcessFields.resource_fields)
    def delete(self, process_id):
        process = Query(MedicalProcess).get(process_id)
        process.set("is_delete", True)
        process.save()
        return process

class AdminProcessCardsApi(Resource):
    @marshal_with(ProcessCardFields.resource_fields)
    def get(self, process_id):
        process = Query(MedicalProcess).get(process_id)
        try:
            cards = Query(ProcessCard).ascending('sort').equal_to("is_delete", False).equal_to(
                "parent", process).find()
        except LeanCloudError, e:
            if e.code == 101:  # 服务端对应的 Class 还没创建
                cards = []
            else:
                raise e
        return cards

    @request_validator({"+name": "string",
                        "+card_can_loop": "boolean"})
    @marshal_with(ProcessCardFields.resource_fields)
    def post(self, process_id):
        data = request.jsondata
        name = data.get('name')
        card_can_loop = data.get("card_can_loop")

        process = Query(MedicalProcess).get(process_id)
        try:
            total_cards_num = Query(ProcessCard).equal_to("parent", process).count()
        except LeanCloudError, e:
            if e.code == 101:  # 服务端对应的 Class 还没创建
                total_cards_num = 0
            else:
                raise e

        card = ProcessCard()
        card.set("name", name)
        card.set("card_can_loop", card_can_loop)
        card.set("sort", total_cards_num)
        card.set('is_delete', False)
        card.set("parent", process)
        card.save()
        return card

    @request_validator({"sort": "string"})
    @marshal_with(ProcessCardFields.resource_fields)
    def put(self, process_id):
        """
        重新排序
        """
        process = Query(MedicalProcess).get(process_id)
        cards = Query(ProcessCard).ascending('sort').equal_to("is_delete", False).equal_to(
                "parent", process).find()
        sort = request.jsondata.get('sort')
        sort_list = sort.split(',')
        if len(cards) != len(sort_list):
            return abort(400, message=u"数量不同")

        for i, card_id in enumerate(sort_list):
            card = Query(ProcessCard).get(card_id)
            card.set("sort", i)
            card.save()
        return cards


class AdminProcessCardApi(Resource):
    @marshal_with(ProcessCardFields.resource_fields)
    def delete(self, card_id):
        card = Query(ProcessCard).get(card_id)
        card.set("is_delete", True)
        card.save()
        return card

    @request_validator({"+name": "string",
                        "+card_can_loop": "boolean"})
    @marshal_with(ProcessCardFields.resource_fields)
    def put(self, card_id):
        data = request.jsondata
        name = data.get('name')
        card_can_loop = data.get("card_can_loop")
        card = Query(ProcessCard).get(card_id)
        card.set("name", name)
        card.set("card_can_loop", card_can_loop)
        card.save()
        return card

class AdminCardItemsApi(Resource):
    @marshal_with(CardItemFields.resource_fields)
    def get(self, card_id):
        card = Query(ProcessCard).get(card_id)
        try:
            items = Query(CardItem).ascending('sort').equal_to("is_delete", False).equal_to(
                "parent", card).find()
        except LeanCloudError, e:
            if e.code == 101:  # 服务端对应的 Class 还没创建
                items = []
            else:
                raise e
        return items

    @request_validator({"+name": "string",
                        "+item_type": "string",
                        "item_title": "string",
                        "item_prompt": "string",
                        "item_choice_label": "string",
                        "item_before_input": "string",
                        "item_after_input": "string",
                        "+item_is_must": "boolean"})
    @marshal_with(CardItemFields.resource_fields)
    def post(self, card_id):
        card = Query(ProcessCard).get(card_id)
        try:
            total_items_num = Query(CardItem).equal_to("parent", card).count()
        except LeanCloudError, e:
            if e.code == 101:  # 服务端对应的 Class 还没创建
                total_items_num = 0
            else:
                raise e

        data = request.jsondata
        name = data.get('name')
        item_type = data.get('item_type')
        item_title = data.get('item_title')
        item_prompt = data.get('item_prompt')
        item_choice_label = data.get('item_choice_label')
        item_before_input = data.get('item_before_input')
        item_after_input = data.get('item_after_input')
        item_is_must = data.get('item_is_must')

        item = CardItem()
        item.set("name", name)
        item.set("item_type", item_type)
        item.set("item_title", item_title)
        item.set("item_prompt", item_prompt)
        item.set("item_choice_label", item_choice_label)
        item.set("item_before_input", item_before_input)
        item.set("item_after_input", item_after_input)
        item.set("item_is_must", item_is_must)
        item.set('is_delete', False)
        item.set("parent", card)
        item.set("sort", total_items_num)
        item.save()
        return item

    @request_validator({"sort": "string"})
    @marshal_with(CardItemFields.resource_fields)
    def put(self, card_id):
        """
        项目排序
        :param card_id:
        :return:
        """
        card = Query(ProcessCard).get(card_id)
        items = Query(CardItem).ascending('sort').equal_to("is_delete", False).equal_to(
                "parent", card).find()
        data = request.jsondata
        sort = data.get('sort')
        sort_list = sort.split(',')
        if len(items) != len(sort_list):
            return abort(400, message=u"数量不同")

        for i, item_id in enumerate(sort_list):
            item = Query(CardItem).get(item_id)
            item.set('sort', i)
            item.save()
        return items

class AdminCardItemApi(Resource):
    @request_validator({"+name": "string",
                        "+item_type": "string",
                        "item_title": "string",
                        "item_prompt": "string",
                        "item_choice_label": "string",
                        "item_before_input": "string",
                        "item_after_input": "string",
                        "+item_is_must": "boolean"})
    @marshal_with(CardItemFields.resource_fields)
    def put(self, item_id):
        data = request.jsondata
        name = data.get('name')
        item_type = data.get('item_type')
        item_title = data.get('item_title')
        item_prompt = data.get('item_prompt')
        item_choice_label = data.get('item_choice_label')
        item_before_input = data.get('item_before_input')
        item_after_input = data.get('item_after_input')
        item_is_must = data.get('item_is_must')

        item = Query(CardItem).get(item_id)
        item.set("name", name)
        item.set("item_type", item_type)
        item.set("item_title", item_title)
        item.set("item_prompt", item_prompt)
        item.set("item_choice_label", item_choice_label)
        item.set("item_before_input", item_before_input)
        item.set("item_after_input", item_after_input)
        item.set("item_is_must", item_is_must)
        item.save()
        return item

    @marshal_with(CardItemFields.resource_fields)
    def delete(self, item_id):
        item = Query(CardItem).get(item_id)
        item.set("is_delete", True)
        item.save()
        return item

    @marshal_with(CardItemFields.resource_fields)
    def get(self, item_id):
        item = Query(CardItem).get(item_id)
        return item

api.add_resource(AdminMedicalsApi, '/medical_templates')
api.add_resource(AdminMedicalApi, '/medical_templates/<string:medical_id>')
api.add_resource(AdminMedicalProcessesApi, '/medical_templates/<string:medical_id>/medical_processes')
api.add_resource(AdminMedicalProcessApi, '/medical_processes/<string:process_id>')
api.add_resource(AdminProcessCardsApi, '/medical_processes/<string:process_id>/processes_cards')
api.add_resource(AdminProcessCardApi, '/processes_cards/<string:card_id>')
api.add_resource(AdminCardItemsApi, '/processes_cards/<string:card_id>/card_items')
api.add_resource(AdminCardItemApi, '/card_items/<string:item_id>')


