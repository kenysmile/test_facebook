//odoo.define('tritam.kaban', function(require) {
//    "use strict";
//    var config = require('web.config');
//    var core = require('web.core');
//    var data = require('web.data');
//    var Model = require('web.DataModel');
//    var Widget = require('web.Widget');
//    var QWeb = core.qweb;
//    var KanbanColumn = require('web_kanban.Column');
//    KanbanColumn.include({
//        start: function() {
//            var self = this;
//            this._super.apply(this, arguments);
//            if (config.device.size_class > config.device.SIZES.XS && this.draggable !== false) {
//                // deactivate sortable in mobile mode.  It does not work anyway,
//                // and it breaks horizontal scrolling in kanban views.  Someday, we
//                // should find a way to use the touch events to make sortable work.
//                this.$el.sortable({
//                    connectWith: '.o_kanban_group',
//                    revert: 0,
//                    delay: 0,
//                    items: '> .o_kanban_record:not(.o_updating)',
//                    helper: 'clone',
//                    cursor: 'move',
//                    over: function() {
//                        self.$el.addClass('o_kanban_hover');
//                        self.update_column();
//                    },
//                    out: function() {
//                        self.$el.removeClass('o_kanban_hover');
//                    },
//                    update: function(event, ui) {
//                        var record = ui.item.data('record');
//                        var index = self.records.indexOf(record);
//                        var test2 = $.contains(self.$el[0], record.$el[0]);
//                        record.$el.removeAttr('style'); // jqueryui sortable add display:block inline
//                        if (index >= 0 && test2) {
//                            // resequencing records
//                            self.trigger_up('kanban_column_resequence');
//                        } else if (index >= 0 && !test2) {
//                            // removing record from this column
//                            self.records.splice(self.records.indexOf(record), 1);
//                            self.dataset.remove_ids([record.id]);
//                        } else {
//                            // adding record to this column
//                            self.records.push(record);
//                            self.dataset.add_ids([record.id]);
//                            record.setParent(self);
//                            ui.item.addClass('o_updating');
//                            self.trigger_up('kanban_column_add_record', {
//                                record: record
//                            });
//                            self.trigger('kanban_column_add_record', self.do_action({
//                                type: 'ir.actions.act_window',
//                                res_model: 'crm.activity.log',
//                                view_mode: 'form',
//                                view_type: 'form',
//                                context: {
//                                planned_revenue : 1
//                                                },
//                                views: [
//                                    [false, 'form']
//                                ],
//                                target: 'new',
//
//                            }));
//                        }
//                        self.update_column();
//                    }
//                });
//            }
//        },
//    });
//});