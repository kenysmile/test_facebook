odoo.define('fresh_layout_list_custom_column.button', function(require) {
    "use strict";

    var ListController = require('web.ListController');
    var KbController = require('web.KanbanController');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var WebClient = require('web.WebClient');
    var KanbanView = require('web.KanbanView');
//

    ListController.include({

        // Thêm nút chỉnh sửa các cột tree vào tree view
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            this.$buttons.on('click', '#new_contact', this._onEditColumn.bind(this));
        },

        _onEditColumn: function(e) {
            e.preventDefault();
            var self = this;
            rpc.query({
                model: 'res.automatic',
                method: 'action_in',
                args: [[]],
            }).then(function(action) {
                self.reload();
            });

        },

    });


//
//    KbController.include({
//
//        // Thêm nút chỉnh sửa các cột tree vào tree view
//        renderButtons: function ($node) {
//            this._super.apply(this, arguments);
//            this.$buttons.on('click', '#new_contact', this._onEditColumn.bind(this));
//        },
//
//        _onEditColumn: function(e) {
//            e.preventDefault();
//            var self = this;
//            rpc.query({
//                model: 'res.automatic',
//                method: 'action_in',
//                args: [[]],
//            }).then(function(action) {
//                self.reload();
//            });
//
//        },
//
//    });


});

//odoo.define('tritam.kaban.button', function(require) {
//    "use strict";
//    var config = require('web.config');
//    var core = require('web.core');
//    var data = require('web.data');
//    var Model = require('web.Model');
//    var Widget = require('web.Widget');
//    var session = require('web.session');
//    var QWeb = core.qweb;
//    var KanbanView = require('web.KanbanView');
//    var rpc = require('web.rpc');
//    var WebClient = require('web.WebClient');
//
//
//
//    KanbanView.include({
//        // Thêm nút chỉnh sửa các cột tree vào tree view
//        renderButtons: function ($node) {
//            this._super.apply(this, arguments);
//            this.$buttons.on('click', '.f_button_edit_column', this._onEditColumn.bind(this));
//        }
//        _onEditColumn: function(e) {
//            e.preventDefault();
//            var self = this;
//            rpc.query({
//                model: self.modelName,
//                method: 'action_edit_column',
//                args: [[]],
//            }).then(function(action) {
//                return self.do_action(action, {
//                    on_close: function() {
//                        location.reload();
//                    },
//                });
//            });
//        },
////    KanbanView.include({
////    render_buttons: function($node) {
////        var self = this;
////        if (self.model == "crm.lead" && this.options.action_buttons !== false) {
////            this.$buttons = $(QWeb.render("KanbanView.buttons", {'widget': this,
////                                                                    'op_create' : this.is_action_enabled('create')}));
////            this.$buttons.on('click', 'button.o-kanban-button-new', function () {
////                if (self.grouped && self.widgets.length && self.on_create === 'quick_create') {
////                    // Activate the quick create in the first column
////                    self.widgets[0].add_quick_create();
////                } else if (self.on_create && self.on_create !== 'quick_create') {
////                    // Execute the given action
////                    self.do_action(self.on_create, {
////                        on_close: self.do_action.bind(self),
////                        additional_context: self.search_context,
////                    });
////                } else {
////                    // Open the form view
////                    self.add_record();
////                }
////            });
////
////            this.update_buttons();
////            this.$buttons.appendTo($node);
//
////        self.$buttons.children('#button_new_contact').css("display", "none")
////        self.$buttons.children('#button_re_use').css("display", "none")
////        self.$buttons.children('#button_re_contact').css("display", "none")
////        this.$buttons.on('click', '#button_new_contact', function () {
////            var mod = new Model("res.automatic", self.dataset.context, self.dataset.domain);
////            mod.call("action_in", [],{"context":{'check_contact':true}}).then(function(result) {
////             self.do_action();
////            });
////            });
////        this.$buttons.on('click', '#button_re_use', function () {
////            var mod = new Model("res.automatic", self.dataset.context, self.dataset.domain);
////            mod.call("action_renew_rp", [],{"context":{'check_contact':true}}).then(function(result) {
////             self.do_reload();
////            });
////        });
////
////        this.$buttons.on('click', '#button_hotline', function () {
////            var mod = new Model("res.automatic", self.dataset.context, self.dataset.domain);
////            mod.call("action_hotline", [],{"context":{'check_contact':true}}).then(function(result) {
////             self.do_reload();
////            });
////        });
////
////        this.$buttons.on('click', '#button_18h', function () {
////            var mod = new Model("res.automatic", self.dataset.context, self.dataset.domain);
////            mod.call("action_18h", [],{"context":{'check_contact':true}}).then(function(result) {
////             self.do_reload();
////            });
////        });
////        this.$buttons.on('click', '#button_re_contact', function () {
////            var mod = new Model("res.automatic", self.dataset.context, self.dataset.domain);
////            mod.call("action_to_sign", [],{"context":{'check_contact':true}}).then(function(result) {
////            self.do_reload();
////            });
////        });
////        this.$buttons.on('click', '#button_sp', function () {
////            var mod = new Model("res.automatic", self.dataset.context, self.dataset.domain);
////            mod.call("action_to_sp", [],{"context":{'check_contact':true}}).then(function(result) {
////            self.do_reload();
////            });
////        });
////        this.$buttons.on('click', '#button_re_sign_contact', function () {
////            var mod = new Model("res.automatic", self.dataset.context, self.dataset.domain);
////            mod.call("action_to_sign_recall", [],{"context":{'check_contact':true}}).then(function(result) {
////            self.do_reload();
////            });
////        });
////        this.$buttons.on('click', '#button_re_support_contact', function () {
////            var mod = new Model("res.automatic", self.dataset.context, self.dataset.domain);
////            mod.call("action_to_support_need_sp", [],{"context":{'check_contact':true}}).then(function(result) {
////            self.do_reload();
////            });
////        });
////
////        this.$buttons.on('click', '#re_supported_contact', function () {
////            var mod = new Model("res.automatic", self.dataset.context, self.dataset.domain);
////            mod.call("action_supported_to_support", [],{"context":{'check_contact':true}}).then(function(result) {
////            self.do_reload();
////            });
////        });
////        self.do_reload();
////        this.session.user_has_group('tritam_users.group_sales_team_manager').then(function(has_group) {
////                if(has_group) {
////                self.$buttons.children('#button_new_contact').css("display", "inline")
////                self.$buttons.children('#button_re_use').css("display", "inline")
////                self.$buttons.children('#button_re_contact').css("display", "inline")
////                self.$buttons.children('#button_sp').css("display", "inline")
////                }
////            });
////            }else{
////        this._super.apply(this, arguments);
////        }
////    }
//    });
//});