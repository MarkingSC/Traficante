# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.


from odoo import models, fields


class UnpaidRemainder(models.Model):
    _name = 'sh.unpaid.remainder.config'
    _description = 'Unpaid Remainder'

    name = fields.Char(string='Reminder Name', required=True)
    sh_remainder_days = fields.Integer(
        string='Reminder Days Before/After (Days)-(+ve/-ve)'
    )
    sh_template_id = fields.Many2one(
        'mail.template', string='Template')
