/**
 * Created by Panmax on 15/9/7.
 */
'use strict';

angular.module('medical', ['ui.sortable'])
    .config(['$interpolateProvider', function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
    }])
    .controller('add_medical', function ($scope, $http) {
        $scope.now_select_medical_index = null;
        $scope.now_select_process_index = null;
        $scope.now_select_card_index = null;
        $scope.now_select_item_index = null;

        $scope.medical_names = [];
        $scope.process_names = [];
        $scope.card_names = [];
        $scope.item_names = [];
        $scope.init = function () {
            flush_medical();
        };

        // 点击某个病历
        $scope.click_medical_name = function (index) {
            $('#loading_model').modal('show');
            $scope.now_select_medical_index = index;
            var medical_id = $scope.medical_names[index].id;
            for(var i=0; i<$scope.medical_names.length; i++) {
                $scope.medical_names[i].select = false
            }
            $scope.medical_names[index].select = true;

            flush_process(medical_id)
        };

        // 点击新增病历
        $scope.click_add_medical = function () {
            $scope.input_medical_name = "";
            $scope.input_medical_category = "传染和寄生虫";
            $('#medical_name_model').modal('show');
        };
        // 新增病历
        $scope.add_medical_name = function () {
            if ($scope.input_medical_name == null || $scope.input_medical_name == "") {
                alert("请输入病历名称");
                return
            }
            var rank = $scope.input_medical_rank
            $('#medical_name_model').modal('hide');
            $http.post('/v1/medical_templates', {
                "name": $scope.input_medical_name,
                "category": $scope.input_medical_category,
                "rank": parseInt(rank)
            }).success(function (data) {
               flush_medical()
            }).error(function () {
                alert('添加病历失败');
            });
        };

        // 编辑病历
        // 当重命名病历按钮点击时 取得要修改的索引 并且取得修改之前的名字 展示在修改输入框中
        $scope.on_rename_medical_name_click = function (index) {
            $scope.now_select_medical_index = index;
            $scope.input_rename_medical_name = $scope.medical_names[index].name;
            $scope.input_medical_show = $scope.medical_names[index].show;
            $scope.input_medical_rank = $scope.medical_names[index].rank;
            $scope.input_medical_category = $scope.medical_names[index].category;
        };
        $scope.rename_medical_name = function () {
            $('#medical_rename_model').modal('hide');
            var medical_id = $scope.medical_names[$scope.now_select_medical_index].id;
            var name = $scope.input_rename_medical_name;
            var rank = parseInt($scope.input_medical_rank);
            var category = $scope.input_medical_category;
            if (category == null) {
                category = "";
            }
            $http.put('/v1/medical_templates/' + medical_id, {
                "name": name,
                "rank": rank,
                "show": $scope.input_medical_show,
                "category": category
            }).success(function () {
                flush_medical()
            }).error(function () {
                alert('修改失败')
            });
        };
        // 删除病历
        $scope.delete_medical_name = function (index) {
            var medical_id = $scope.medical_names[index].id;
            $http.delete('/v1/medical_templates/' + medical_id, {
            }).success(function () {
                flush_medical()
            }).error(function () {
                alert('删除失败');
            });
        };

        // 点击复制时
        $scope.on_copy_click = function (index) {
            $scope.now_select_medical_index = index;
            $scope.copy_name = $scope.medical_names[index].name;
        };

        // 复制病历
        $scope.copy_medical_name = function () {
            $('#medical_copy_model').modal('hide');
            $('#loading_model').modal('show');
            var index = $scope.now_select_medical_index;
            var medical_id = $scope.medical_names[index].id;
            var name = $scope.input_medical_name;
            var rank = parseInt($scope.input_medical_rank);
            $http.post('/v1/medical_templates/' + medical_id, {
                "name": name,
                "rank": rank
            }).success(function () {
                $('#loading_model').modal('hide');
                $scope.input_medical_name = "";
                flush_medical()
            }).error(function () {
                $('#loading_model').modal('hide');
                alert('修改失败')
            });
        };


        // 点击某个病历中的某个过程
        $scope.click_process_name = function (index) {
            $scope.now_select_process_index = index;
            for(var i=0; i<$scope.process_names.length; i++) {
                $scope.process_names[i].select = false
            }
            $scope.process_names[index].select = true;

            // 加载卡片
            var process_id = $scope.process_names[index].id;
            flush_card(process_id)
        };


        // 点击新增过程按钮
        $scope.click_add_process = function () {
            if ($scope.now_select_medical_index == null) {
                alert('请先选择一个病历');
                return
            }
            $scope.input_process_name = "";
            $scope.input_process_icon_url = "";
            $('#process_name_model').modal('show');
        };

        $scope.add_process_name = function () {
            if ($scope.input_process_name == null || $scope.input_process_name == "") {
                alert("请输入过程名称");
                return
            }
            $('#process_name_model').modal('hide'); // jQuery和angular混用，我也是够屌

            var medical_id = $scope.medical_names[$scope.now_select_medical_index].id;
            $http.post('/v1/medical_templates/' + medical_id + '/medical_processes', {
                "name": $scope.input_process_name,
                "icon_url": $scope.input_process_icon_url
            }).success(function (data) {
                flush_process(medical_id)
            }).error(function () {
                alert('获取过程失败')
            });
        };

        // 编辑过程
        $scope.on_rename_process_name_click = function (index) {
            $scope.now_select_process_index = index;
            $scope.input_rename_process_name = $scope.process_names[index].name;
            $scope.input_process_icon_url = $scope.process_names[index].icon_url;
        };
        $scope.rename_process_name = function () {
            var medical_id = $scope.medical_names[$scope.now_select_medical_index].id;
            var process_id = $scope.process_names[$scope.now_select_process_index].id;
            var name = $scope.input_rename_process_name;
            $('#process_rename_model').modal('hide');
            $http.put('/v1/medical_processes/' + process_id, {
                "name": name,
                "icon_url": $scope.input_process_icon_url
            }).success(function () {
                flush_process(medical_id);
            }).error(function () {
                alert('修改失败')
            });
        };
        // 删除过程
        $scope.delete_process_name = function (index) {
            var process_id = $scope.process_names[index].id;
            var medical_id = $scope.medical_names[$scope.now_select_medical_index].id;
            $http.delete('/v1/medical_processes/' + process_id, {
            }).success(function (data) {
                flush_process(medical_id)
            }).error(function () {
                alert('删除失败');
            });
        };

        // 点击卡片
        $scope.click_card_name = function (index) {
            $('#loading_model').modal('show');
            $scope.now_select_card_index = index;
            for (var i=0; i < $scope.card_names.length; i++) {
                $scope.card_names[i].select = false;
            }
            $scope.card_names[index].select = true;

            //加载项目
            var card_id = $scope.card_names[index].id;
            flush_item(card_id)
        };

        // 点击添加卡片
        $scope.click_add_card = function () {
            if ($scope.now_select_process_index == null) {
                alert('请先选择一个过程');
                return
            }
            $scope.input_card_name = "";
            $scope.input_card_can_loop = false;
            $('#card_name_model').modal('show');
        };
        // 添加卡片
        $scope.add_card_name = function () {
            $('#card_name_model').modal('hide');
            var process_id = $scope.process_names[$scope.now_select_process_index].id;
            $http.post('/v1/medical_processes/' + process_id + '/processes_cards', {
                "name": $scope.input_card_name,
                "card_can_loop": $scope.input_card_can_loop
            }).success(function (data) {
                flush_card(process_id)
            }).error(function () {
                alert('添加失败')
            });
        };

        // 编辑卡片
        var rename_card_index = null;
        // 当重命名卡片按钮点击时 取得要修改的索引 并且取得修改之前的名字 展示在修改输入框中
        $scope.on_rename_card_name_click = function (index) {
            rename_card_index = index;
            $scope.input_rename_card_name = $scope.card_names[index].name;
            $scope.input_card_can_loop = $scope.card_names[index].card_can_loop;
        };

        $scope.rename_card_name = function () {
            $('#card_rename_model').modal('hide');
            var process_id = $scope.process_names[$scope.now_select_process_index].id;
            var card_id = $scope.card_names[rename_card_index].id;
            var name = $scope.input_rename_card_name;
            var card_can_loop = $scope.input_card_can_loop;
            $http.put('/v1/processes_cards/' + card_id, {
                "name": name,
                "card_can_loop": card_can_loop
            }).success(function (data) {
                flush_card(process_id)
            }).error(function () {
                alert('修改失败')
            });
        };
        
        // 删除卡片
        $scope.delete_card_name = function (index) {
            var process_id = $scope.process_names[$scope.now_select_process_index].id;
            var card_id = $scope.card_names[index].id;
            $http.delete('/v1/processes_cards/' + card_id, {
            }).success(function (data) {
                flush_card(process_id)
            }).error(function () {
                alert('删除失败');
            });
        };

        // 点击添加项目
        $scope.click_add_item = function () {
            $scope.edit_item_mode = false;
            if ($scope.now_select_card_index == null) {
                alert('请先选择一个卡片');
                return
            }
            $scope.input_item_name = "";
            $scope.input_item_title = "";
            $scope.input_item_prompt = "";
            $scope.input_item_choice_label = "";
            $scope.item_type = "pic";
            $scope.input_item_before_input = "";
            $scope.input_item_after_input = "";
            $scope.input_item_is_must = false;

            $scope.need_title = true;
            $scope.need_prompt = false;
            $scope.need_date_title = false;
            $scope.need_add_label = false;
            $scope.need_before_input = false;
            $scope.need_after_input = false;

            $('#add_item_model').modal('show');
        };

        // 点击项目
        $scope.click_item_name = function (index) {
            for (var i=0; i<$scope.item_names.length; i++) {
                $scope.item_names[i].select = false;
            }
            $scope.item_names[index].select = true;
            $scope.now_select_item_index = index;
        };

        // 添加项目
        $scope.add_card_item = function () {
            var card_id = $scope.card_names[$scope.now_select_card_index].id;
            var name = $scope.input_item_name;
            var item_type = $scope.item_type;
            var item_title = $scope.input_item_title;
            var item_prompt = $scope.input_item_prompt;
            var item_choice_label = $scope.input_item_choice_label;
            var item_before_input = $scope.input_item_before_input;
            var item_after_input = $scope.input_item_after_input;
            var item_is_must = $scope.input_item_is_must;

            $http.post('/v1/processes_cards/' + card_id + '/card_items', {
                "name": name,
                "item_type": item_type,
                "item_title": item_title,
                "item_prompt": item_prompt,
                "item_choice_label": item_choice_label,
                "item_before_input": item_before_input,
                "item_after_input": item_after_input,
                "item_is_must": item_is_must
            }).success(function (data) {
                $('#add_item_model').modal('hide'); // jQuery和angular混用，我也是够屌
                //重新加载项目
                var card_id = $scope.card_names[$scope.now_select_card_index].id;
                flush_item(card_id);
            }).error(function () {
                alert('添加病历失败');
            });
        };

        // 添加项目时更改项目类型
        $scope.item_type_change = function (item_type) {
            if (item_type == "pic") {
                $scope.need_prompt = false;
                $scope.need_title = true;
                $scope.need_add_label = false;
                $scope.need_before_input = false;
                $scope.need_after_input = false;
            } else if (item_type == "text") {
                $scope.need_prompt = true;
                $scope.need_title = true;
                $scope.need_add_label = false;
                $scope.need_before_input = false;
                $scope.need_after_input = false;
            } else if (item_type == "input") {
                $scope.need_prompt = true;
                $scope.need_title = true;
                $scope.need_add_label = false;
                $scope.need_before_input = true;
                $scope.need_after_input = true;
            } else if (item_type == "checkbox") {
                $scope.need_prompt = false;
                $scope.need_title = true;
                $scope.need_add_label = true;
                $scope.need_before_input = false;
                $scope.need_after_input = false;
            } else if (item_type == "radio") {
                $scope.need_prompt = false;
                $scope.need_title = true;
                $scope.need_add_label = true;
                $scope.need_before_input = false;
                $scope.need_after_input = false;
            } else if (item_type == "select") {
                $scope.need_prompt = false;
                $scope.need_title = true;
                $scope.need_add_label = true;
                $scope.need_before_input = false;
                $scope.need_after_input = false;
            } else if (item_type == "number") {
                $scope.need_prompt = true;
                $scope.need_title = true;
                $scope.need_add_label = false;
                $scope.need_before_input = true;
                $scope.need_after_input = true;
            } else if (item_type == "date") {
                $scope.need_prompt = false;
                $scope.need_title = true;
                $scope.need_add_label = false;
                $scope.need_before_input = true;
                $scope.need_after_input = false;
            } else if (item_type == "complication") {
                $scope.need_prompt = false;
                $scope.need_title = true;
                $scope.need_add_label = false;
                $scope.need_before_input = false;
                $scope.need_after_input = false;
            } else {
                alert('卡片类型不正确');
                $scope.item_type = "pic";
                $scope.need_prompt = false;
                $scope.need_title = true;
                $scope.need_add_label = false;
                $scope.need_before_input = false;
                $scope.need_after_input = false;
            }
        };

        // 删除项
        $scope.delete_item_name = function (index) {
            var card_id = $scope.card_names[$scope.now_select_card_index].id;
            var item_id = $scope.item_names[index].id;
            $http.delete('/v1/card_items/' + item_id, {

            }).success(function (data) {
                flush_item(card_id)
            }).error(function () {
                alert('删除失败');
            });
        };

        // 点击编辑项目
        $scope.click_edit_item = function (index) {
            $('#loading_model').modal('show');
            $scope.edit_item_mode = true;
            var item_id = $scope.item_names[index].id;
            $http.get('/v1/card_items/' + item_id, {

            }).success(function (data) {
                $('#loading_model').modal('hide');
                $scope.input_item_name = data.name;
                $scope.item_type = data.item_type;
                $scope.input_item_title = data.item_title;
                $scope.input_item_prompt = data.item_prompt;
                $scope.input_item_choice_label = data.item_choice_label;
                $scope.input_item_before_input = data.item_before_input;
                $scope.input_item_after_input = data.item_after_input;
                $scope.input_item_is_must = data.item_is_must;

                $scope.item_type_change(data.item_type);
                $('#add_item_model').modal('show');
            }).error(function () {
                $('#loading_model').modal('hide');
                alert('读取失败');
            });
        };

        // 编辑项目
        $scope.edit_item = function () {
            $('#loading_model').modal('show');
            var item_id = $scope.item_names[$scope.now_select_item_index].id;
            var name = $scope.input_item_name;
            var item_type = $scope.item_type;
            var item_title = $scope.input_item_title;
            var item_prompt = $scope.input_item_prompt;
            var item_choice_label = $scope.input_item_choice_label;
            var item_before_input = $scope.input_item_before_input;
            var item_after_input = $scope.input_item_after_input;
            var item_is_must = $scope.input_item_is_must;

            $http.put('/v1/card_items/' + item_id, {
                "name": name,
                "item_type": item_type,
                "item_title": item_title,
                "item_prompt": item_prompt,
                "item_choice_label": item_choice_label,
                "item_before_input": item_before_input,
                "item_after_input": item_after_input,
                "item_is_must": item_is_must
            }).success(function (out_data) {
                $('#add_item_model').modal('hide');
                //重新加载项目
                var card_id = $scope.card_names[$scope.now_select_card_index].id;
                flush_item(card_id)
            }).error(function () {
                alert('修改失败');
            });
        };

        var before_sort = "";
        $scope.sort_process = {
            update: function(e, ui) {
                before_sort = $scope.process_names.map(function (i) {
                    return i.sort;
                }).join(',');
                console.log(before_sort)
            },
            stop: function(e, ui) {
                var sort = $scope.process_names.map(function (i) {
                    return i.id;
                }).join(',');

                if (before_sort == "") {
                    return;
                }
                $('#loading_model').modal('show');
                var medical_id = $scope.medical_names[$scope.now_select_medical_index].id;
                $http.put('/v1/medical_templates/' + medical_id + '/medical_processes', {
                    "sort": sort
                }).success(function (data) {
                    before_sort = "";
                    flush_process(medical_id)
                }).error(function () {
                    alert('过程排序失败')
                });
            }
          };

        $scope.sort_card = {
            update: function(e, ui) {
                before_sort = $scope.card_names.map(function (i) {
                    return i.sort;
                }).join(',');
                console.log(before_sort)
            },
            stop: function(e, ui) {
                var sort = $scope.card_names.map(function (i) {
                    return i.id;
                }).join(',');

                if (before_sort == "") {
                    return;
                }
                $('#loading_model').modal('show');
                var process_id = $scope.process_names[$scope.now_select_process_index].id;
                $http.put('/v1/medical_processes/' + process_id + '/processes_cards', {
                    "sort": sort
                }).success(function (data) {
                    before_sort = "";
                    // 重新加载卡片
                    flush_card(process_id)
                }).error(function () {
                    alert('排序失败')
                });
            }
          };

        $scope.sort_item = {
            update: function(e, ui) {
                before_sort = $scope.item_names.map(function (i) {
                    return i.sort;
                }).join(',');
                console.log(before_sort)
            },
            stop: function(e, ui) {
                var sort = $scope.item_names.map(function (i) {
                    return i.id;
                }).join(',');

                if (before_sort == "") {
                    return;
                }
                $('#loading_model').modal('show');
                var card_id = $scope.card_names[$scope.now_select_card_index].id;
                $http.put('/v1/processes_cards/' + card_id + '/card_items', {
                    "sort": sort
                }).success(function (data) {
                    before_sort = "";
                    flush_item(card_id)
                }).error(function () {
                    alert('过程排序失败')
                });
            }
          };

        var flush_medical = function () {
            $('#loading_model').modal('show');
            $http.get('/v1/medical_templates', {
            }).success(function (data) {
                for (var i = 0; i < data.length; i++) {
                    data[i].select = false
                }
                $scope.medical_names = data;
                $('#loading_model').modal('hide');
            }).error(function () {
                $('#loading_model').modal('hide');
                alert('获取病历失败')
            });

            $scope.process_names = [];
            $scope.card_names = [];
            $scope.item_names = [];
            $scope.now_select_medical_index = null;
            $scope.now_select_process_index = null;
            $scope.now_select_card_index = null;
            $scope.now_select_item_index = null;
        };

        var flush_process = function (medical_id) {
            $('#loading_model').modal('show');
            $http.get('/v1/medical_templates/' + medical_id + '/medical_processes', {
            }).success(function (data) {
                for (var i=0; i<data.length; i++) {
                    data[i].select = false;
                }
                $scope.process_names = data;

                $('#loading_model').modal('hide');
            }).error(function () {
                $('#loading_model').modal('hide');
                alert('加载失败')
            });

            // 清空卡片和项目
            $scope.card_names = [];
            $scope.item_names = [];
            $scope.now_select_process_index = null;
            $scope.now_select_card_index = null;
            $scope.now_select_item_index = null;
        };

        var flush_card = function (process_id) {
            $('#loading_model').modal('show');
            $http.get('/v1/medical_processes/' + process_id + '/processes_cards', {
            }).success(function (data) {
                for (var i=0; i<data.length; i++) {
                    data[i].select = false;
                }
                $scope.card_names = data;
                $('#loading_model').modal('hide');
            }).error(function () {
                $('#loading_model').modal('hide');
                alert('加载失败')
            });

            $scope.item_names = [];
            $scope.now_select_card_index = null;
            $scope.now_select_item_index = null;
        };

        var flush_item = function (card_id) {
            $('#loading_model').modal('show');
            $http.get('/v1/processes_cards/' + card_id + '/card_items', {
            }).success(function (data) {
                for (var i=0; i<data.length; i++) {
                    data[i].select = false;
                    if (data[i].item_choice_label != null && data[i].item_choice_label != "") {
                        data[i].item_choice_label_array = data[i].item_choice_label.split(" ")
                    }
                }
                $scope.item_names = data;
                $('#loading_model').modal('hide');
            }).error(function () {
                $('#loading_model').modal('hide');
                alert('获取项目失败')
            });
        }

        $scope.show_demo = function (process_id) {
            window.open("http://m.ihaoyisheng.com/medical/processes/" + process_id + "?demo=1")

        }


    });