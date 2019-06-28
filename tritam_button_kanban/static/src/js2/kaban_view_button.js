odoo.define('kanbanview.button.inherit', function(require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require("web.session");
    var qweb = core.qweb;

    KanbanController.include({
    	/**
         * @param {jQueryElement} $node
         */
        renderButtons: function ($node) {
        	if (this.modelName == 'crm.lead'){
        	    this.$buttons = $(qweb.render('KanbanView.buttons.inherit', {widget: this}));

        	    if (session.is_superuser == true){
                    this.$buttons.on('click', '#button_new_contact', this._onEditColumn.bind(this));
                    this.$buttons.on('click', 'button.o-kanban-button-new', this._onButtonNew.bind(this));;
                    }
                else {
                    this.$buttons.on('click', '#button_new_contact', this._onEditColumn.bind(this));
                }
                this._updateButtons();
                this.$buttons.appendTo($node);
                return;

            }
        	    this._super.apply(this, arguments);
                this.$buttons = $(qweb.render('KanbanView.buttons', {widget: this}));

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

});