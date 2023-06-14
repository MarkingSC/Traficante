# -*- coding: utf-8 -*-

from odoo import fields, models


class MailServer(models.Model):
    _inherit = "ir.mail_server"


    company_ids = fields.Many2one("res.company", "Company Name")