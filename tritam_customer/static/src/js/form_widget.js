//odoo.define('tritam.form_widget', function(require) {
//"use strict";
//var ajax = require('web.ajax');
//var core = require('web.core');
//var crash_manager = require('web.crash_manager');
//var data = require('web.data');
//var datepicker = require('web.datepicker');
//var dom_utils = require('web.dom_utils');
//var Priority = require('web.Priority');
//var ProgressBar = require('web.ProgressBar');
//var Dialog = require('web.Dialog');
//var common = require('web.form_common');
//var formats = require('web.formats');
//var framework = require('web.framework');
//var Model = require('web.DataModel');
//var pyeval = require('web.pyeval');
//var session = require('web.session');
//var utils = require('web.utils');
//var FieldStatus = core.form_widget_registry.get('statusbar')
//var _t = core._t;
//var QWeb = core.qweb;
//
//FieldStatus.include({
//    on_click_stage: _.debounce(function(ev) {
//        var self = this;
//        self.do_action({
//            type: 'ir.actions.act_window',
//            res_model: 'crm.activity.log',
//            view_mode: 'form',
//            view_type: 'form',
//            views: [
//                [false, 'form']
//            ],
//            context: {
//                default_lead_id: self.view.datarecord.id
//            },
//            target: 'new'
//        }).done(function() {
//                    self.view.reload();
//                });
//        var $li = $(ev.currentTarget);
//        var ul = $li.closest('.oe_form_field_status');
//        if (this.view.is_disabled) {
//            return;
//        }
//        var val;
//        if (ul.attr('disabled')) {
//            return;
//        }
//        if (this.field.type === "many2one") {
//            val = parseInt($li.data("id"), 10);
//        } else {
//            val = $li.data("id");
//        }
//        if (val !== self.get('value')) {
//            if (!this.view.datarecord.id ||
//                this.view.datarecord.id.toString().match(data.BufferedDataSet.virtual_id_regex)) {
//                // don't save, only set value for not-yet-saved many2ones
//                self.set_value(val);
//            } else {
//                this.view.recursive_save().done(function() {
//                    var change = {};
//                    change[self.name] = val;
//                    ul.attr('disabled', true);
//                    self.view.dataset.write(self.view.datarecord.id, change).done(function() {
//                        self.view.reload();
//                    }).always(function() {
//                        ul.removeAttr('disabled');
//                    });
//                });
//            }
//        }
//    }, 300, true),
//});
//});