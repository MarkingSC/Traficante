# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    unpaid_reminder = fields.Boolean("Email Notification ?")
    notify_on = fields.Selection([('inv_date', 'Invoice Date'), ('due_date', 'Due Date')],
                                 default='due_date', string="Send Email Notification on")


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    unpaid_reminder = fields.Boolean(
        string="Email Notification ?", related='company_id.unpaid_reminder', readonly=False)
    
    notify_on = fields.Selection([('inv_date', 'Invoice Date'), ('due_date', 'Due Date')],
                                 default='due_date', string="Send Email Notification on", related="company_id.notify_on", readonly=False)

    def action_set_remainder(self):
        return{
            'name': 'Invoice Due Reminder',
            'res_model': 'sh.unpaid.remainder.config',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'target': 'current',
        }
