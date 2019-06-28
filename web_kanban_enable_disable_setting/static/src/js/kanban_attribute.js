odoo.define('web_kanban_enable_disable_setting', function (require) {
    "use strict";

    var KanbanColumn = require('web.KanbanColumn');
    var KanbanView = require('web.KanbanView');

    KanbanColumn.include({
        init: function(parent, group_data, options, record_options) {
            this._super.apply(this, arguments);
            this.enable_setting = true ;
            if (record_options.enable_setting != 'undefined'){
                this.enable_setting = record_options.enable_setting;
            }
        },
    });

    KanbanView.include({
        init: function (viewInfo, params) {
            var arch = viewInfo.arch;
            this._super.apply(this, arguments);
            var activeActions = this.controllerParams.activeActions;
            this.rendererParams.record_options = {
                editable: activeActions.edit,
                deletable: activeActions.delete,
                read_only_mode: params.readOnlyMode,
                enable_setting:  arch.attrs.enable_setting,
            };
        },
    })
});